# 🔍 SIM-APDU-Analyzer v3.2

A powerful web-based tool for analyzing SIM/eSIM APDU logs captured from QXDM, QCAT, or Shannon DM.  
Designed for modern dual SIM devices (DSDS), where eSIM and pSIM logs are interleaved.

---

## 💡 Why This Tool?

Traditional SIM trace tools can't intercept communication between the eSIM and the Mobile Equipment (ME).  
This tool enables APDU-level analysis of real device logs, clearly separating SIM1 and SIM2 traffic and parsing both protocol and application-level messages — just like a hardware SIM tracer would.

---

## ✅ Key Features

- **Log Upload**: Upload `.txt` logs from QXDM/QCAT/Shannon or paste from clipboard  
- **SIM Slot Selection**: Focus analysis on SIM1 or SIM2  
- **Protocol-level View**: Visualizes TX/RX APDU sequences  
- **Application-level Interpretation**: Extracts logical channel, DF/EF context, APDU commands  
- **File System Viewer**: Decodes USIM file hierarchy, EF contents, and interprets binary values  
- **Web UI**: Flask-based with modern, responsive layout and session memory

---

## 🧾 Supported Log Formats

| Format Source   | Detection Logic         | Notes                                        |
|-----------------|--------------------------|----------------------------------------------|
| QXDM / QCAT     | Contains `[0x19B7]`      | Qualcomm UIM APDU messages                   |
| Shannon DM      | Contains `USIM_MAIN`     | Samsung Shannon logs with internal decoding  |
| Generic QCAT    | Structured `.txt` logs   | Must contain UIM records per line            |

---

## 🛠 How to Use (Web Version)

1. 접속 후 `📂 File` 버튼으로 `.txt` 파일 업로드 또는 클립보드에서 붙여넣기  
2. `SIM1` / `SIM2` 선택  
3. `Analyze` 클릭  
4. 상단 탭에서 `APDU` 또는 `File System` 전환  
5. 메시지를 클릭하면 하단에 상세 분석 표시

---

## 📦 Sample Logs

You can download test samples directly from the web UI (README > bottom):

- `QXDM_apdu_sim1.txt`  
- `Shannon_debug_sim2.txt`  
- `QCAT_export_sim1.txt`

---

## 🖼 UI Preview

📸 Screenshots are available in [`readme.html`](/readme) or inside the web service:

- Protocol & Application-level analysis
- File system decoding
- Interactive inspection per APDU message

---

## 🧩 Tech Stack

- Python 3.11  
- Flask + Flask-Session  
- pandas, tabulate  
- gunicorn (for Render deployment)

---

## 🔒 Data Privacy

- Uploaded logs are stored **only in session memory**
- No logs are saved to disk or sent externally
- Session expires on browser close or timeout

---

## 📄 License & Credits

**Copyright 2025. JUSEOK AHN <ajs3013@lguplus.co.kr> all rights reserved.**

This analyzer was developed to assist with internal validation, protocol testing, and eSIM log debugging.  
Use cases include carrier-side validation, log toolchain automation, and R&D on next-gen SIM management.

