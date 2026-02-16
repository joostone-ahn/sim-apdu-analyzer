# 🔍 SIM-APDU-Analyzer

A powerful web-based tool for analyzing SIM/eSIM APDU logs extracted from internal modem traces. Optimized for Dual SIM (DSDS) architectures, it de-interleaves mixed pSIM and eSIM APDU streams into distinct logical sessions, providing hardware-level probe capabilities (e.g., COMPRION Minimove) using only software-based modem diagnostic logs.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 💡 Why This Tool?
Traditional SIM tracers, such as COMPRION MiniMove, rely on physical interfaces and cannot intercept internal communication with eSIMs. This tool overcomes that limitation by parsing raw modem diagnostic logs, providing full visibility into both pSIM and eSIM activity without requiring additional hardware.

### ✨ Key Features
- **No Hardware Required**: Eliminates the need for physical sniffing tools by directly processing internal modem diagnostic traces.
- **eSIM & Dual SIM Support**: De-interleaves mixed traffic into independent logical sessions (SIM1/SIM2) for Dual SIM environments.
- **Multi-Layer Analysis**: Provides systematic visibility across the Protocol (Raw I/O), Application (Command/Logical Channel), and File System (EF Hierarchy) layers.
- **3GPP Compliance**: : Decoding of TS 31.102/103 Elementary Files (EFs), such as IMSI, MSISDN, PLMNwAcT, and UST.
---

## 🧾 Supported Log Formats

| Format Source      | Detection Logic             | Notes                                                    |
|--------------------|------------------------------|----------------------------------------------------------|
| QXDM / QCAT        | Contains `[0x19B7]`           | Qualcomm UIM APDU logs<br> • **Log mask file**: `dmc/QXDM_log_mask_UIM_0x19B7.dmc` (apply in QXDM: `View` → `Configuration` → `Load Config`) |
| Shannon DM         | Contains `USIM_MAIN`          | Samsung Shannon logs with internal decoding              |

> `[0x19B7]` and `USIM_MAIN` are used for format detection and parsing.

---

## 🚀 Quick Start

### 1. 🌐 Try Online (No Installation Required)

**Live Demo**: [https://huggingface.co/spaces/Joostone/sim-apdu-analyzer](https://huggingface.co/spaces/Joostone/sim-apdu-analyzer)

Try the tool instantly in your browser without any installation. Perfect for quick testing and evaluation.

> **Note**: The online version runs on Hugging Face Spaces and may have limited resources.

---

### 2. 🐳 Using Docker (Recommended for Local Deployment)

#### Mac (Intel)

```bash
docker run -d \
  -p 8090:8090 \
  --name sim-apdu-analyzer \
  ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

#### Mac (Apple Silicon)

```bash
docker run -d \
  --platform linux/amd64 \
  -p 8090:8090 \
  --name sim-apdu-analyzer \
  ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

> **Note**: Apple Silicon users must use `--platform linux/amd64` as the image is built for AMD64 architecture

#### Windows

```powershell
docker run -d -p 8090:8090 --name sim-apdu-analyzer ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

> **Note**: Windows users need WSL2 installed for Docker Desktop

#### Access Application

Open your browser and navigate to: http://localhost:8090

---

### 3. 💻 Running from Source (For Development)

If you want to modify the code or run from source:

#### Setup

```bash
# Clone repository
git clone https://github.com/joostone-ahn/sim-apdu-analyzer.git
cd sim-apdu-analyzer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

#### Access Application

Open your browser and navigate to: http://localhost:8090

---

## 📖 How to Use

### Step 1: Capture Logs

- **Qualcomm**: QXDM Professional or QCAT
- **Samsung**: Shannon DM (Exynos chipsets)

Save the log as a `.txt` file.

### Step 2: Upload and Analyze
1. Click **📁 Open Log File** button to upload your log file
2. Select **SIM1** or **SIM2** from the dropdown
3. Click **🔍 Analyze** button
4. Wait for processing to complete

### Step 3: Explore Results

#### APDU Tab
- **📋 Summary**: List of all APDU commands with color coding
- **📶 Protocol-Level Analysis**: Raw TX/RX data with timestamps
- **💻 Application-Level Analysis**: Decoded command parameters and file information

#### File System Tab
- **📁 File System**: All files read during the session
- **📄 File Contents**: Raw hexadecimal data
- **🔍 Parsing Data**: Interpreted data (phone numbers, PLMN lists, etc.)

> **Note**: Click any row in the Summary or File System table to view detailed analysis in the right-side panels.

### Step 4: Export and Copy Data

- **💾 Save to Excel**: Export Summary or File System data to Excel format
- **📋 Copy**: Copy Protocol-Level Analysis, Application-Level Analysis, File Contents, or Parsing Data to clipboard

---

## 🎨 Color Guide

### APDU Tab

| Color | Meaning | Examples |
|-------|---------|----------|
| **Red** | Errors and failures | `❌ ERROR` |
| **Magenta** | Authentication re-sync | `🔐 AUTHENTICATE w/ Re-Sync` |
| **Gray** | Unknown file or command | `🚫 SELECT`, `❓ UNKNOWN` |
| **Yellow** | SIM OTA updates | `📨 ENVELOPE`, `🔄 REFRESH` |
| **Cyan** | Power events | `🔌 RESET`, `🔌 POWER` |
| **Light Blue** | Channel management | `🔀 MANAGE CHANNEL` |
| **Light Green** | Authentication | `🔐 AUTHENTICATE` |

### File System Tab

| Color | Meaning | Files |
|-------|---------|-------|
| **Yellow** | Critical OTA updates | IMSI, MSISDN, OPLMNwAcT, ACC, Routing_Ind, IMPI, IMPU |
| **Light Green** | General OTA updates | All other updated files |

---

## 🧩 Tech Stack

### Backend
- **Python 3.11**: Core language
- **Flask 3.0**: Web framework
- **Flask-Session**: Server-side session management
- **pandas**: Data processing and analysis
- **openpyxl**: Excel file generation

### Frontend
- **HTML5 + CSS3**: Modern web standards
- **jQuery**: AJAX and DOM manipulation
- **Responsive Design**: Works on desktop and mobile

### Deployment
- **Gunicorn**: WSGI HTTP server
- **Docker**: Containerization support
- **GitHub Container Registry**: Image distribution

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (Browser)                │
│  • File Upload Interface                    │
│  • Interactive Tables                       │
│  • Real-time Analysis Display               │
└──────────────┬──────────────────────────────┘
               │ HTTP/JSON
┌──────────────▼──────────────────────────────┐
│         Flask Web Server                    │
│  • Route Handlers                           │
│  • Session Management                       │
│  • File Processing                          │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│       Core Processing Pipeline              │
│                                             │
│  msg_item    → Log Format Detection         │
│  port        → SIM Port Filtering           │
│  msg_prot    → Protocol Analysis            │
│  msg_sum     → Application Analysis         │
│  msg_app     → Detailed View                │
│  msg_files   → File System View             │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│       Reference Data (3GPP Standards)       │
│  • file_system.py  (DF/EF Definitions)      │
│  • command.py      (INS Code Mapping)       │
│  • spec_ref.py     (Status Words, Events)   │
│  • SELECT.py       (File Selection Logic)   │
│  • READ.py         (Content Parsing)        │
└─────────────────────────────────────────────┘
```

---

## 📖 References

### 3GPP Standards
- [TS 31.102](https://www.3gpp.org/ftp/Specs/archive/31_series/31.102/) - USIM Application
- [TS 31.103](https://www.3gpp.org/ftp/Specs/archive/31_series/31.103/) - ISIM Application
- [TS 31.111](https://www.3gpp.org/ftp/Specs/archive/31_series/31.111/) - USIM Application Toolkit

### ETSI Standards
- [TS 102.221](https://www.etsi.org/deliver/etsi_ts/102200_102299/102221/) - UICC-Terminal Interface
- [TS 102.223](https://www.etsi.org/deliver/etsi_ts/102200_102299/102223/) - Card Application Toolkit

### Other Standards
- [ISO/IEC 7816-4](https://www.iso.org/standard/54550.html) - Integrated Circuit Cards
- [GSMA SGP.02](https://www.gsma.com/esim/) - Remote Provisioning Architecture

---

## 👤 Author

**JUSEOK AHN (안주석)**  
**Email**: ajs3013@lguplus.co.kr  
**Organization**: LG U+  
**Role**: Technical Specialist, Telecommunications Engineer

---

## 📄 License & Credits

**© 2026 JUSEOK AHN &lt;ajs3013@lguplus.co.kr&gt; All rights reserved.**

This software is proprietary and confidential. Developed for internal analysis, SIM validation, and automation of diagnostic workflows at LG U+.

### Applicable For
- QA teams performing SIM/eSIM testing
- Engineers debugging modem-SIM communication
- Researchers working with modern SIM/eSIM infrastructure
- Network operators validating SIM profiles

### Patent Information
This software is protected by patent applications filed with the Korean Intellectual Property Office.

---

**Made with ❤️ for better SIM/eSIM analysis**
