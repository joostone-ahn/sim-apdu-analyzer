# 🔍 SIM-APDU-Analyzer v3.2

A powerful web-based tool for analyzing SIM/eSIM APDU logs captured from QXDM, QCAT, or Shannon DM.  
Designed for modern dual SIM devices (DSDS), where eSIM and pSIM logs are interleaved.

---

## 💡 Why This Tool?

Traditional contact-based SIM trace tools — e.g., the Minimove device by COMPRION — can't intercept communication between the eSIM and Mobile Equipment (ME), as they rely on physical interfaces.  
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

1. Click the `📂 File` button to upload a `.txt` log file, or paste log contents from the clipboard  
2. Select either `SIM1` or `SIM2` to focus analysis  
3. Click the `Analyze` button to begin decoding  
4. Switch between `APDU` and `File System` tabs using the top navigation  
5. In **APDU view**, click each message to see protocol and application-level details below  
   In **File System view**, click each file item to inspect its decoded contents and parsed structure

---

## 📦 Sample Logs

You can download test samples directly from the web UI (README > bottom):

- `QXDM_apdu_sim1.txt`  
- `Shannon_debug_sim2.txt`  
- `QCAT_export_sim1.txt`

---

## 🖼 UI Preview

### Protocol & Application-level analysis


### File system decoding


---

## 📄 License & Credits

**Copyright 2025. JUSEOK AHN <ajs3013@lguplus.co.kr> all rights reserved.**

This analyzer was developed to assist with internal validation, protocol testing, and eSIM log debugging.  
Use cases include carrier-side validation, log toolchain automation, and R&D on next-gen SIM management.
