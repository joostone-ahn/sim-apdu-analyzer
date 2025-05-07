from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import pandas as pd
import io
import msg_item
import port
import msg_sum
import msg_app
import msg_prot
import msg_files
import os
import re
from openpyxl.utils import escape


# print("🔥 main_web.py started")
app = Flask(__name__)
app.secret_key = 'apdu-analyzer-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
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


@app.route("/readme")
def show_static_readme():
    return render_template("readme.html")

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}

    # ✅ 접속 초기화 시 기존 세션 전체 삭제
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

        # ✅ 새로운 SIM 선택값 반영
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
        selected_sim=session.get('sim_select', 1)
    )

@app.route('/analyze_line', methods=['POST'])
def analyze_line():
    index = int(request.form['index'])
    app_rst_input = session['prot_type'], session['sum_cmd'], session['sum_log_ch'], session['sum_log_ch_id']
    app_result = msg_app.rst(app_rst_input, session['sum_read'], session['sum_error'], index)
    prot_rst_input = session['msg_all'], session['prot_start'], session['prot_type'], session['prot_data']
    prot_result = msg_prot.rst(prot_rst_input, index)
    return jsonify({
        'protocol': prot_result,
        'application': app_result
    })

@app.route('/file_detail', methods=['POST'])
def file_detail():
    index = int(request.form['index'])
    df = session.get('df', [])
    if df and 0 <= index < len(df):
        return jsonify({
            'contents': df[index].get('contents', ''),
            'parsing': df[index].get('parsing', '')
        })
    return jsonify({'contents': '', 'parsing': ''})

# Excel 허용 문자 필터 (openpyxl이 허용하는 범위 외 제거)
def clean_excel_string(s):
    if isinstance(s, str):
        # ASCII 제어문자 제거 (0x00~0x1F 제외: Tab(9), LF(10), CR(13)만 허용)
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

    # 전체 데이터로 DataFrame 구성
    df_full = pd.DataFrame(df_records)

    # 열 순서 지정 및 셀 문자열 정리
    desired_cols = ['DF', 'File', 'DF_Id', 'File_Id', 'Type', 'SFI', 'REC', 'OFS', 'LEN', 'ref', 'contents', 'parsing']
    df_full = df_full[[col for col in desired_cols if col in df_full.columns]]
    df_full = df_full.applymap(clean_excel_string)

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
    app.run(debug=True)