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

| Area                | Color         | Meaning                                                                 |
|---------------------|---------------|-------------------------------------------------------------------------|
| **APDU Tab**        |               |                                                                         |
| `SELECT (X)`        | <span style="background:#888; color:#fff; padding:2px 6px; border-radius:4px;">Gray</span> | Unknown EF selection |
| `'ENVELOPE'`, etc.  | <span style="background:#ffff66; padding:2px 6px; border-radius:4px;">Yellow</span> | Proactive SIM operations |
| `'RESET'`, `'POWER'`| <span style="background:#00ffff; padding:2px 6px; border-radius:4px;">Cyan</span> | SIM power/reset events |
| `'MANAGE CHANNEL'`  | <span style="background:#add8e6; padding:2px 6px; border-radius:4px;">Light Blue</span> | Logical channel control |
| `'AUTHENTICATE'`    | <span style="background:#90ee90; padding:2px 6px; border-radius:4px;">Light Green</span> | AKA or challenge-response authentication |
| `'ERROR'`           | <span style="background:#ff4d4d; padding:2px 6px; border-radius:4px;">Red</span> | Error message or malformed APDU |
| `'Re-Sync'`         | <span style="background:#ff66cc; padding:2px 6px; border-radius:4px;">Magenta</span> | Authentication resynchronization triggered |
| **File System Tab** |               |                                                                         |
| File updated (highlighted) | <span style="background:#ffff66; padding:2px 6px; border-radius:4px;">Yellow</span> | OTA-updated file of key importance (e.g., IMSI, MSISDN) |
| File updated        | <span style="background:#90ee90; padding:2px 6px; border-radius:4px;">Light Green</span> | General EF file updated in log trace |

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
