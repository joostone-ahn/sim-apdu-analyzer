# 🔍 SIM-APDU-Analyzer v3.2

A powerful web-based tool for analyzing SIM/eSIM APDU logs captured from QXDM, QCAT, or Shannon DM.  
Tailored for modern dual SIM devices (DSDS), where eSIM and pSIM logs are interleaved within the same trace.

---

## 💡 Why This Tool?

Traditional SIM analyzers — _e.g., Minimove by COMPRION_ — can only trace physical SIM cards.  
They fail to capture eSIM activity between the eUICC and the Mobile Equipment (ME), which happens internally.  
**SIM-APDU-Analyzer** bridges this gap by decoding raw log traces, isolating SIM1/SIM2 traffic, and presenting results comparable to hardware SIM probes.

---

## ✅ Key Features

- **Flexible Log Input**: Upload `.txt` files or paste from clipboard  
- **Dual SIM Support**: Analyze logs per SIM slot (SIM1 / SIM2)  
- **Protocol View**: TX/RX command visualization with timestamp  
- **Application View**: Parse DF/EF, logical channel, and command types  
- **File System View**: Browse EF files, see raw and interpreted content  
- **UI**: Lightweight Flask app with session-based state handling

---

## 🧾 Supported Log Formats

| Format Source   | Detection Logic     | Notes                                                       |
|-----------------|----------------------|-------------------------------------------------------------|
| QXDM / QCAT     | Contains `[0x19B7]`  | Qualcomm UIM APDU messages in CP logs                       |
| Shannon DM      | Contains `USIM_MAIN` | Samsung internal logs with decoded USIM/APDU information    |
| Generic QCAT    | Text-based `.txt`    | Should include APDU records in each relevant message line   |

---

## 🛠 How to Use (Web Version)

1. Click 📂 **File** to upload `.txt` logs or paste copied log text  
2. Choose **SIM1** or **SIM2**  
3. Click **Analyze** to decode  
4. Use the top navigation to switch between `APDU` and `File System` views  
5. In **APDU View**: Click any message to reveal:
   - **Protocol-Level Analysis**: Raw TX/RX byte sequence
   - **Application-Level Analysis**: Logical channel, DF/EF, interpreted command  
6. In **File System View**: Click any file to inspect:
   - **Raw EF Contents**
   - **Decoded Structure** such as service bits, identifiers, access rules

---

## 🎨 UI Color Guide

| Context                    | Color       | Meaning                                                                 |
|----------------------------|-------------|-------------------------------------------------------------------------|
| `[TX]` / `[RX]` lines      | **Green**   | Transmitted / received APDU data at protocol level                      |
| `SELECT (X)`              | **Gray**    | Unknown or invalid EF selection                                         |
| `'ENVELOPE'`, `'REFRESH'` | **Yellow**  | Proactive SIM commands / session updates                               |
| `'RESET'`, `'POWER'`       | **Cyan**    | SIM power/reset operations                                              |
| `'MANAGE CHANNEL'`         | **Blue**    | Channel management (open, close, etc.)                                  |
| `'AUTHENTICATE'`           | **Light Green** | SIM authentication (e.g., AKA or challenge-response)             |
| `'ERROR'` lines            | **Red**     | Malformed or failed APDU responses                                      |
| `'Re-Sync'` entries        | **Magenta** | Indicates resynchronization activity (e.g., AKA SQN desync handling)    |

---

## 📦 Sample Logs

📥 [Download Sample Logs](https://drive.google.com/drive/folders/1I1Bpgms0mXRy9NLk4kg_3K9BFDVbe9LD?usp=sharing)

Included files:

- `Clip_CM_HK.txt` – eSIM OTA logs (HK)  
- `Clip_CM_TW.txt` – eSIM OTA logs (Taiwan)  
- `Clip_CM_US.txt` – eSIM OTA logs (US)  
- `Clip_eSIM_install_OTA.txt` – Full provisioning trace  
- `QCAT_Anritsu_SIM.txt` – SIM logs captured from QCAT (lab)  
- `QCAT_eSIM_error.txt` – Error-prone log for validation/testing

---

## 🖼 UI Preview

Visit `/readme` on the web server to see example screenshots:

- Protocol & Application-level decoded view  
- EF File System inspection  
- Interactive UI with file upload and clipboard input

---

## 🧩 Tech Stack

- Python 3.11  
- Flask + Flask-Session  
- pandas, tabulate  
- gunicorn (Render deployment ready)

---

## 🔒 Data Privacy

- All uploaded logs are stored in memory (session only)  
- No persistent or external storage involved  
- Sessions expire automatically on browser close or timeout

---

## 📄 License & Credits

**© 2025 JUSEOK AHN &lt;ajs3013@lguplus.co.kr&gt; All rights reserved.**

Built to support internal network validation, protocol inspection, and dual-SIM eSIM verification.  
Useful for telecom engineers, QA testers, and researchers exploring APDU behavior on live networks.
