# 🔍 SIM-APDU-Analyzer

A powerful web-based tool for analyzing SIM/eSIM APDU logs captured from real devices.  
Tailored for modern dual SIM (DSDS) architectures, where eSIM and pSIM messages are interleaved in modem traces.

---

## 💡 Why This Tool?

Traditional SIM tracer — _e.g., Minimove by COMPRION_ — rely on physical interfaces and can't intercept internal communication with eSIMs. This tool bridges that gap by decoding raw diagnostic logs and enabling accurate analysis of SIM1/SIM2 activity — just like a hardware SIM probe.

---

## ✅ Key Features

- **Flexible Log Input**: Upload `.txt` files  
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

> Only basic structural consistency is required. `[0x19B7]` and `USIM_MAIN` act as format identifiers for filtering and decoding.

---

## 🛠 How to Use

1. Click 📂 **File** to upload a `.txt` file, or paste from clipboard  
2. Choose **SIM1** or **SIM2**  
3. Click **Analyze**  
4. Navigate to either **APDU** or **File System** tab  

### **APDU View**
  - **Protocol-Level Analysis**: TX/RX breakdown with timestamps
  - **Application-Level Analysis**: DF/EF, logical channel, APDU interpretation  

### **File System View**
  - **File Contents**: raw hex  
  - **Parsed Structure**: interpreted according to file type — e.g., bitmap flags, PLMN list, ASCII strings, TLV templates

---

## 🎨 Color Guide

| Area                | Color       | Meaning                                |
|---------------------|-------------|----------------------------------------|
| `SELECT (X)`        | ![#888888](https://via.placeholder.com/15/888888/000000?text=+) Gray | Unknown EF selection |
| `'ENVELOPE'`, etc.  | ![#FFFF66](https://via.placeholder.com/15/FFFF66/000000?text=+) Yellow | Proactive SIM operations |
| `'RESET'`, `'POWER'`| ![#00FFFF](https://via.placeholder.com/15/00FFFF/000000?text=+) Cyan | SIM power/reset events |
| `'MANAGE CHANNEL'`  | ![#ADD8E6](https://via.placeholder.com/15/ADD8E6/000000?text=+) Light Blue | Logical channel control |
| `'AUTHENTICATE'`    | ![#90EE90](https://via.placeholder.com/15/90EE90/000000?text=+) Light Green | AKA authentication |
| `'ERROR'`           | ![#FF4D4D](https://via.placeholder.com/15/FF4D4D/000000?text=+) Red | APDU error |
| `'Re-Sync'`         | ![#FF66CC](https://via.placeholder.com/15/FF66CC/000000?text=+) Magenta | Re-synchronization |

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
