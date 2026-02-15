debug_mode = 0
# debug_mode = 1

import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import msg_item
import port
import msg_sum
import msg_app
import msg_prot
import msg_files
import file_system
import re

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
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
os.makedirs('/tmp/flask_session', exist_ok=True)
Session(app)

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

    if request.method == 'GET':
        session.clear()

    if request.method == 'POST':
        sim_select = int(request.form.get('sim_select', 1))
        file = request.files.get('logfile')

        if file and file.filename.endswith('.txt'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session['filepath'] = filepath
            session['filename'] = file.filename

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

            session['msg_all'] = msg_all
            session['msg_start'] = msg_start
            session['msg_end'] = msg_end
            session['msg_SN'] = msg_SN
            session['msg_port'] = msg_port
            session['msg_type'] = msg_type
            session['msg_data'] = msg_data

        elif 'filepath' in session:
            filepath = session['filepath']
            with open(filepath, 'r', encoding='utf-8') as f:
                msg_all = f.read().splitlines()

            msg_start = session['msg_start']
            msg_end = session['msg_end']
            msg_SN = session['msg_SN']
            msg_port = session['msg_port']
            msg_type = session['msg_type']
            msg_data = session['msg_data']
        else:
            return render_template('index.html', result={}, filename='', selected_sim=1)

        session['sim_select'] = sim_select

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

        session['prot_start'] = prot_start
        session['prot_type'] = prot_type
        session['prot_data'] = prot_data
        session['sum_cmd'] = sum_cmd
        session['sum_read'] = sum_read
        session['sum_error'] = sum_error
        session['sum_log_ch'] = sum_log_ch
        session['sum_log_ch_id'] = sum_log_ch_id
        session['df'] = df.to_dict(orient='records') if df is not None else None

        result = {
            'summary': [
                (idx, line, get_line_color_class(line)) for idx, line in enumerate(sum_rst)
            ],
            'df_with_index': list(enumerate(df.to_dict(orient='records'))) if df is not None else []
        }

    return render_template(
        'index.html',
        result=result,
        filename=session.get('filename'),
        selected_sim=session.get('sim_select', 1),
        valid_file_names=VALID_FILE_NAMES
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
        
        # Check if session data exists
        required_keys = ['prot_type', 'sum_cmd', 'sum_log_ch', 'sum_log_ch_id', 'sum_read', 'sum_error', 'msg_all', 'prot_start', 'prot_data']
        missing_keys = [key for key in required_keys if key not in session]
        
        if missing_keys:
            return jsonify({
                'error': f'Session data missing: {", ".join(missing_keys)}',
                'protocol_structured': [],
                'application_structured': None
            }), 400
        
        app_rst_input = session['prot_type'], session['sum_cmd'], session['sum_log_ch'], session['sum_log_ch_id']
        app_result = msg_app.rst(app_rst_input, session['sum_read'], session['sum_error'], index)
        prot_rst_input = session['msg_all'], session['prot_start'], session['prot_type'], session['prot_data']
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
        df = session.get('df', [])
        
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
