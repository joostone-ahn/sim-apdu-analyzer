debug_mode = 0
# debug_mode = 1

import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from cachelib import SimpleCache
import msg_item
import port
import msg_sum
import msg_app
import msg_prot
import msg_files
import file_system
import re
import uuid
from datetime import datetime, timedelta

# In-memory session storage (not relying on cookies)
SESSION_STORE = {}
SESSION_TIMEOUT = 3600  # 1 hour

def create_session_id():
    """Create a new session ID and initialize storage"""
    session_id = str(uuid.uuid4())
    SESSION_STORE[session_id] = {
        'created_at': datetime.now(),
        'data': {}
    }
    return session_id

def get_session_data(session_id):
    """Get session data by ID, return None if not found or expired"""
    if not session_id or session_id not in SESSION_STORE:
        return None
    
    session_info = SESSION_STORE[session_id]
    # Check if session expired
    if datetime.now() - session_info['created_at'] > timedelta(seconds=SESSION_TIMEOUT):
        del SESSION_STORE[session_id]
        return None
    
    return session_info['data']

def save_session_data(session_id, key, value):
    """Save data to session"""
    if session_id in SESSION_STORE:
        SESSION_STORE[session_id]['data'][key] = value

def cleanup_old_sessions():
    """Remove expired sessions"""
    now = datetime.now()
    expired = [sid for sid, info in SESSION_STORE.items() 
               if now - info['created_at'] > timedelta(seconds=SESSION_TIMEOUT)]
    for sid in expired:
        del SESSION_STORE[sid]

# Get all valid file names from file_system
def get_valid_file_names():
    """Extract all file names from EF_name dictionary"""
    file_names = set()
    for df_files in file_system.EF_name.values():
        if isinstance(df_files, dict):
            file_names.update(df_files.values())
    # Add DF names too
    file_names.update(file_system.DF_name.values())
    return list(file_names)

VALID_FILE_NAMES = get_valid_file_names()

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'apdu-analyzer-secret-key-v3'

# Use in-memory cache for session storage (works in single-worker setup)
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = SimpleCache()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'apdu_'

Session(app)

# Increase max content length for large log files
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_line_color_class(line):
    if 'ERROR' in line:
        return 'red'
    elif 'Re-Sync' in line:
        return 'magenta'
    elif any(x in line for x in ['(X)', '(*)', 'Unknown']):
        return 'gray'
    elif 'ENVELOPE' in line or 'REFRESH' in line:
        return 'yellow'
    elif 'RESET' in line or 'POWER' in line:
        return 'cyan'
    elif 'MANAGE CHANNEL' in line:
        return 'lightblue'
    elif 'AUTHENTICATE' in line:
        return 'lightgreen'
    return ''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    session_id = None

    if request.method == 'GET':
        # Cleanup old sessions periodically
        cleanup_old_sessions()

    if request.method == 'POST':
        # Create new session ID
        session_id = create_session_id()
        
        sim_select = int(request.form.get('sim_select', 1))
        file = request.files.get('logfile')

        if file and file.filename.endswith('.txt'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            save_session_data(session_id, 'filepath', filepath)
            save_session_data(session_id, 'filename', file.filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                msg_all = f.read().splitlines()

            if '[0x19B7]' in msg_all[0]:
                msg_all = msg_item.QXDM_filter(msg_all)
                msg_start, msg_end, msg_SN, msg_port, msg_type, msg_data = msg_item.QXDM(msg_all)
            elif 'USIM_MAIN' in msg_all[0] or 'USIM_MAIN' in msg_all[1]:
                msg_all = msg_item.ShannonDM(msg_all)
                msg_start, msg_end, msg_SN, msg_port, msg_type, msg_data = msg_item.QXDM(msg_all)
            else:
                msg_start, msg_end, msg_SN, msg_port, msg_type, msg_data = msg_item.QCAT(msg_all)

            save_session_data(session_id, 'msg_all', msg_all)
            save_session_data(session_id, 'msg_start', msg_start)
            save_session_data(session_id, 'msg_end', msg_end)
            save_session_data(session_id, 'msg_SN', msg_SN)
            save_session_data(session_id, 'msg_port', msg_port)
            save_session_data(session_id, 'msg_type', msg_type)
            save_session_data(session_id, 'msg_data', msg_data)
        else:
            return render_template('index.html', result={}, filename='', selected_sim=1, session_id=None)

        save_session_data(session_id, 'sim_select', sim_select)
        
        sess_data = get_session_data(session_id)
        msg_all = sess_data['msg_all']
        msg_start = sess_data['msg_start']
        msg_end = sess_data['msg_end']
        msg_SN = sess_data['msg_SN']
        msg_port = sess_data['msg_port']
        msg_type = sess_data['msg_type']
        msg_data = sess_data['msg_data']

        port_index = [i for i, p in enumerate(msg_port) if p == sim_select]
        port_input = msg_all, msg_start, msg_end, msg_SN, msg_type, msg_data
        exe_start, exe_end, exe_type, exe_data = port.process(port_input, port_index)
        prot_input = exe_start, exe_end, exe_type, exe_data
        prot_start, prot_end, prot_type, prot_data = msg_prot.process(prot_input)
        sum_input = msg_all, prot_start, prot_type, prot_data
        sum_rst, sum_log_ch, sum_log_ch_id, sum_cmd, sum_read, sum_error = msg_sum.rst(sum_input)

        df = None
        try:
            if any('READ' in cmd for cmd in sum_cmd):
                df = msg_files.process(sum_rst, sum_read, sum_log_ch)
        except:
            pass

        save_session_data(session_id, 'prot_start', prot_start)
        save_session_data(session_id, 'prot_type', prot_type)
        save_session_data(session_id, 'prot_data', prot_data)
        save_session_data(session_id, 'sum_cmd', sum_cmd)
        save_session_data(session_id, 'sum_read', sum_read)
        save_session_data(session_id, 'sum_error', sum_error)
        save_session_data(session_id, 'sum_log_ch', sum_log_ch)
        save_session_data(session_id, 'sum_log_ch_id', sum_log_ch_id)
        save_session_data(session_id, 'df', df.to_dict(orient='records') if df is not None else None)

        result = {
            'summary': [
                (idx, line, get_line_color_class(line)) for idx, line in enumerate(sum_rst)
            ],
            'df_with_index': list(enumerate(df.to_dict(orient='records'))) if df is not None else [],
            'session_id': session_id  # Include session_id in result
        }

    return render_template(
        'index.html',
        result=result,
        filename=sess_data.get('filename') if session_id else '',
        selected_sim=sess_data.get('sim_select', 1) if session_id else 1,
        valid_file_names=VALID_FILE_NAMES,
        session_id=session_id
    )

def parse_protocol_messages(prot_result):
    """Parse protocol result strings into structured data for HTML rendering"""
    messages = []
    
    if debug_mode:
        print("=== Parsing Protocol Messages ===")
        print(f"Total lines: {len(prot_result)}")
    
    for i, line in enumerate(prot_result):
        if debug_mode:
            print(f"Line {i}: repr={repr(line[:100])}")
        
        # Skip empty lines
        if not line.strip():
            if debug_mode:
                print("  -> Skipped (empty)")
            continue
            
        # Skip separator lines (lines with only dashes)
        if line.strip().replace('-', '').replace('=', '') == '':
            if debug_mode:
                print("  -> Skipped (separator)")
            continue
        
        # Check if line contains timestamp and [TX] or [RX]
        # Use re.DOTALL to match across newlines
        match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s+\[(TX|RX)\]\s+(.*)', line, re.DOTALL)
        if match:
            timestamp = match.group(1)
            direction = match.group(2)
            hex_data_raw = match.group(3)
            
            # Remove newlines and extra spaces from hex_data
            # The hex data may contain \n with indentation for continuation
            hex_data = re.sub(r'\s+', ' ', hex_data_raw).strip()
            
            messages.append({
                'timestamp': timestamp,
                'direction': direction,
                'hex_data': hex_data
            })
            if debug_mode:
                print(f"  -> New message: {timestamp} [{direction}]")
                print(f"     hex_data length: {len(hex_data)}")
                print(f"     first 80: {hex_data[:80]}")
                if len(hex_data) > 80:
                    print(f"     last 80: {hex_data[-80:]}")
    
    if debug_mode:
        print(f"=== Total messages parsed: {len(messages)} ===")
        for i, msg in enumerate(messages):
            print(f"Message {i}: {msg['timestamp']} [{msg['direction']}] hex_data length: {len(msg['hex_data'])}")
    
    return messages

def parse_application_data(app_result):
    """Parse application result strings into structured data for HTML rendering"""
    if not app_result:
        return None
    
    data = {
        'header': {},
        'data': {},
        'parsing': []
    }
    
    separator_count = 0
    current_section = 'header'
    
    for line in app_result:
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            continue
        
        # Separator lines indicate section changes
        if line_stripped.startswith('-'):
            separator_count += 1
            if separator_count == 1:
                current_section = 'data'
            elif separator_count == 2:
                current_section = 'parsing'
            continue
        
        # Parse header section
        if current_section == 'header':
            if 'Logical Channel' in line:
                match = re.search(r'Logical Channel\s*:\s*(.+)', line)
                if match:
                    data['header']['logical_channel'] = match.group(1).strip()
            elif 'Current DF File' in line:
                match = re.search(r'Current DF File\s*:\s*(.+)', line)
                if match:
                    data['header']['df_file'] = match.group(1).strip()
            elif 'Current EF File' in line:
                match = re.search(r'Current EF File\s*:\s*(.+)', line)
                if match:
                    data['header']['ef_file'] = match.group(1).strip()
            elif 'Current Command' in line:
                match = re.search(r'Current Command\s*:\s*(.+)', line)
                if match:
                    data['header']['command'] = match.group(1).strip()
        
        # Parse data section
        elif current_section == 'data':
            if 'Offset' in line or 'Number' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    if 'offset' not in data['data']:
                        data['data']['offset'] = match.group(1).strip()
            elif 'Length' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    data['data']['length'] = match.group(1).strip()
            elif 'Contents' in line:
                # Start collecting hex contents
                match = re.search(r':\s*(.+)', line)
                if match:
                    hex_data = match.group(1).strip()
                    if hex_data:
                        data['data']['contents'] = hex_data
                    else:
                        data['data']['contents'] = ''
            elif 'contents' in data['data'] and line_stripped:
                # Continuation of hex contents
                if re.match(r'^[0-9A-Fa-f\s]+$', line_stripped):
                    data['data']['contents'] += ' ' + line_stripped
        
        # Parse parsing section
        elif current_section == 'parsing':
            if line_stripped:
                data['parsing'].append(line_stripped)
    
    return data

@app.route('/analyze_line', methods=['POST'])
def analyze_line():
    try:
        index = int(request.form['index'])
        session_id = request.form.get('session_id')
        
        if not session_id:
            return jsonify({
                'error': 'No session_id provided',
                'protocol_structured': [],
                'application_structured': None
            }), 400
        
        sess_data = get_session_data(session_id)
        if not sess_data:
            return jsonify({
                'error': 'Session expired or not found',
                'protocol_structured': [],
                'application_structured': None
            }), 400
        
        # Check if session data exists
        required_keys = ['prot_type', 'sum_cmd', 'sum_log_ch', 'sum_log_ch_id', 'sum_read', 'sum_error', 'msg_all', 'prot_start', 'prot_data']
        missing_keys = [key for key in required_keys if key not in sess_data]
        
        if missing_keys:
            return jsonify({
                'error': f'Session data missing: {", ".join(missing_keys)}',
                'protocol_structured': [],
                'application_structured': None
            }), 400
        
        app_rst_input = sess_data['prot_type'], sess_data['sum_cmd'], sess_data['sum_log_ch'], sess_data['sum_log_ch_id']
        app_result = msg_app.rst(app_rst_input, sess_data['sum_read'], sess_data['sum_error'], index)
        prot_rst_input = sess_data['msg_all'], sess_data['prot_start'], sess_data['prot_type'], sess_data['prot_data']
        prot_result = msg_prot.rst(prot_rst_input, index)
        
        # Parse protocol result into structured data
        protocol_messages = parse_protocol_messages(prot_result)
        
        # Parse application result into structured data
        application_data = parse_application_data(app_result)
        
        return jsonify({
            'protocol': prot_result,  # Keep for backward compatibility
            'protocol_structured': protocol_messages,
            'application': app_result,  # Keep for backward compatibility
            'application_structured': application_data
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'protocol_structured': [],
            'application_structured': None
        }), 500

@app.route('/file_detail', methods=['POST'])
def file_detail():
    try:
        index = int(request.form['index'])
        session_id = request.form.get('session_id')
        
        if not session_id:
            return jsonify({
                'error': 'No session_id provided',
                'contents': '',
                'parsing': ''
            }), 400
        
        sess_data = get_session_data(session_id)
        if not sess_data:
            return jsonify({
                'error': 'Session expired or not found',
                'contents': '',
                'parsing': ''
            }), 400
        
        df = sess_data.get('df', [])
        
        if not df:
            return jsonify({
                'error': 'No file system data in session',
                'contents': '',
                'parsing': ''
            }), 400
        
        if df and 0 <= index < len(df):
            contents = df[index].get('contents', '')
            parsing = df[index].get('parsing', '')
            
            # Handle NaN values - convert to empty string
            import math
            if isinstance(contents, float) and math.isnan(contents):
                contents = ''
            if isinstance(parsing, float) and math.isnan(parsing):
                parsing = ''
                
            return jsonify({
                'contents': contents,
                'parsing': parsing
            })
        return jsonify({'contents': '', 'parsing': ''})
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'contents': '',
            'parsing': ''
        }), 500

def clean_excel_string(s):
    if isinstance(s, str):
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", s)
    return s

@app.route("/download_excel")
def download_excel():
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    df_records = session.get('df', [])
    if not df_records:
        return "No file system data available", 400

    df_full = pd.DataFrame(df_records)
    desired_cols = ['DF', 'File', 'DF_Id', 'File_Id', 'Type', 'SFI', 'REC', 'OFS', 'LEN', 'ref', 'contents', 'parsing']
    df_full = df_full[[col for col in desired_cols if col in df_full.columns]]
    df_full = df_full.map(clean_excel_string)

    output = BytesIO()
    df_full.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="file_system_export.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=True)
