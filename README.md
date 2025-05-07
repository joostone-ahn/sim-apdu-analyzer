# 🔍 SIM-APDU-Analyzer v3.2

A powerful web-based tool for analyzing SIM/eSIM APDU logs captured from real devices.  
Tailored for modern dual SIM (DSDS) architectures, where eSIM and pSIM messages are interleaved in modem traces.

---

## 💡 Why This Tool?

Traditional SIM analyzers — _e.g., Minimove by COMPRION_ — rely on physical interfaces and can't intercept internal communication with eSIMs.  
This tool bridges that gap by decoding raw diagnostic logs and enabling accurate analysis of SIM1/SIM2 activity — just like a hardware SIM probe.

---

## ✅ Key Features

- **Flexible Log Input**: Upload `.txt` files or paste from clipboard  
- **Dual SIM Support**: Analyze logs for SIM1 or SIM2 separately  
- **Protocol View**: Visualize TX/RX APDU command sequences with timestamps  
- **Application View**: Decode DF/EF structures, logical channels, and command content  
- **File System View**: Inspect EF hierarchy, raw file content, and parsed values  
- **UI**: Flask-based, responsive design with persistent session handling

---

## 🧾 Supported Log Formats

| Format Source      | Detection Logic             | Notes                                                    |
|--------------------|------------------------------|----------------------------------------------------------|
| QXDM / QCAT        | Contains `[0x19B7]`           | Qualcomm UIM APDU logs — supports filtering and parsing  |
| Shannon DM         | Contains `USIM_MAIN`          | Samsung Shannon logs with internal decoding              |

Only basic structural consistency is required. `[0x19B7]` and `USIM_MAIN` act as format identifiers for filtering and decoding.

---

## 🛠 How to Use (Web Version)

1. Click 📂 **File** to upload a `.txt` file, or paste from clipboard  
2. Choose **SIM1** or **SIM2**  
3. Click **Analyze**  
4. Navigate to either **APDU** or **File System** tab  
5.  
   - In **APDU View**, click a message to display:
     - **Protocol-Level Analysis**: TX/RX breakdown with timestamps
     - **Application-Level Analysis**: DF/EF, logical channel, APDU interpretation  
   - In **File System View**, click a file to view:
     - **File Contents** (raw hex)
     - **Parsed Structure** (decoded binary interpretation)

---

## 🎨 Color Guide

| Area                | Color         | Meaning                                                                 |
|---------------------|---------------|-------------------------------------------------------------------------|
| **APDU Tab**        |               |                                                                         |
| TX/RX APDU lines    | Green         | Raw APDU protocol data                                                  |
| `SELECT (X)`        | Gray          | Unknown EF selection                                                    |
| `'ENVELOPE'`, etc.  | Yellow        | Proactive SIM operations                                                |
| `'RESET'`, `'POWER'`| Cyan          | SIM power/reset events                                                  |
| `'MANAGE CHANNEL'`  | Light Blue    | Logical channel control                                                 |
| `'AUTHENTICATE'`    | Light Green   | AKA or challenge-response authentication                               |
| `'ERROR'`           | Red           | Error message or malformed APDU                                         |
| `'Re-Sync'`         | Magenta       | Authentication resynchronization triggered                              |
| **File System Tab** |               |                                                                         |
| File updated (highlighted) | Yellow        | OTA-updated file of key importance (e.g., IMSI, MSISDN)                 |
| File updated        | Light Green   | General EF file updated in log trace                                    |

---

## 📦 Sample Logs

📥 [Download Sample Logs](https://drive.google.com/drive/folders/1I1Bpgms0mXRy9NLk4kg_3K9BFDVbe9LD?usp=sharing)

Included examples:

- `Clip_CM_HK.txt` – eSIM OTA (HK)  
- `Clip_CM_TW.txt` – eSIM OTA (Taiwan)  
- `Clip_CM_US.txt` – eSIM OTA (US)  
- `Clip_eSIM_install_OTA.txt` – End-to-end installation trace  
- `QCAT_Anritsu_SIM.txt` – Diagnostic log from QCAT  
- `QCAT_eSIM_error.txt` – Error reproduction sample

---

## 🖼 UI Preview

Browse to `/readme` in your deployment to view screenshots:

- Protocol & Application analysis  
- EF file system decoding  
- Clipboard and file input support  
- Interactive color-coded logs

---

## 🧩 Tech Stack

- Python 3.11  
- Flask + Flask-Session  
- pandas, tabulate  
- gunicorn (for cloud deployment)

---

## 🔒 Data Privacy

- Logs are stored only in server-side session memory  
- Nothing is written to disk or externalized  
- Sessions expire when the browser is closed or idle

---

## 📄 License & Credits

**© 2025 JUSEOK AHN &lt;ajs3013@lguplus.co.kr&gt; All rights reserved.**

Developed for internal analysis, SIM validation, and automation of diagnostic workflows.  
Applicable for QA teams, engineers, and researchers working with modern SIM/eSIM infrastructure.
