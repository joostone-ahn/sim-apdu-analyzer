# 🔍 SIM-APDU-Analyzer

A powerful web-based tool for analyzing SIM/eSIM APDU logs captured from real devices.  
Tailored for modern dual SIM (DSDS) architectures, where eSIM and pSIM messages are interleaved in modem traces.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 💡 Why This Tool?

Traditional SIM tracers — _e.g., Minimove by COMPRION_ — rely on physical interfaces and can't intercept internal communication with eSIMs. This tool bridges that gap by decoding raw diagnostic logs and enabling accurate analysis of SIM1/SIM2 activity — just like a hardware SIM probe.

### Key Advantages
- ✅ **No Hardware Required**: Analyze logs from any device with modem diagnostics
- ✅ **eSIM Support**: Full support for embedded SIM profiles
- ✅ **Dual SIM**: Separate analysis for SIM1 and SIM2
- ✅ **3GPP Compliant**: Based on TS 31.102/31.103 standards
- ✅ **Web-Based**: Access from any browser, no installation needed

---

## ✨ Key Features

### 📊 Three-Layer Analysis
1. **Protocol-Level**: Raw TX/RX APDU sequences with timestamps
2. **Application-Level**: Decoded commands, logical channels, DF/EF tracking
3. **File System**: Complete EF hierarchy with parsed content

### 🔍 Advanced Capabilities
- **Dual SIM Support**: Separate analysis for SIM1/SIM2 in DSDS devices
- **OTA Tracking**: Highlight files updated via Over-The-Air
- **Authentication Analysis**: Detailed AKA authentication (RAND/AUTN/RES/AUTS)
- **Error Detection**: Automatic identification of protocol violations and failures
- **File Parsing**: Intelligent parsing of IMSI, MSISDN, PLMN lists, service tables, etc.

### 🎨 User Interface
- **Web-Based**: Modern Flask application with responsive design
- **Color-Coded**: Visual indicators for errors, warnings, and special operations
- **Interactive**: Click any message for detailed analysis
- **Export**: Download file system data to Excel

### 🖥️ Desktop Version
- PyQt5-based standalone application
- Clipboard support for quick analysis
- Same powerful analysis engine

---

## 🧾 Supported Log Formats

| Format Source      | Detection Logic             | Notes                                                    |
|--------------------|------------------------------|----------------------------------------------------------|
| QXDM / QCAT        | Contains `[0x19B7]`           | Qualcomm UIM APDU logs — supports filtering and parsing  |
| Shannon DM         | Contains `USIM_MAIN`          | Samsung Shannon logs with internal decoding              |

> Only basic structural consistency is required. `[0x19B7]` and `USIM_MAIN` act as format identifiers for filtering and decoding.

---

## 🚀 Quick Start

### 🐳 Docker (Recommended)

The easiest way to run SIM APDU Analyzer is using Docker. No Python installation required!

#### Prerequisites
- Docker Desktop installed and running
  - **Windows**: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
  - **macOS (Apple Silicon)**: [Download Docker Desktop for Mac (Apple Silicon)](https://www.docker.com/products/docker-desktop/)
  - **macOS (Intel)**: [Download Docker Desktop for Mac (Intel)](https://www.docker.com/products/docker-desktop/)
  - **Linux**: [Install Docker Engine](https://docs.docker.com/engine/install/)

#### Quick Start with Docker

```bash
# Pull the pre-built image from GitHub Container Registry
docker pull ghcr.io/joostone-ahn/sim-apdu-analyzer:latest

# Run the container
docker run -d \
  --name sim-apdu-analyzer \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  ghcr.io/joostone-ahn/sim-apdu-analyzer:latest

# Access the application
# Open browser: http://localhost:5000
```

#### Platform-Specific Instructions

**Windows (PowerShell)**
```powershell
docker pull ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
docker run -d --name sim-apdu-analyzer -p 5000:5000 -v ${PWD}/uploads:/app/uploads ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

**macOS (Apple Silicon - M1/M2/M3)**
```bash
docker pull ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
docker run -d --name sim-apdu-analyzer -p 5000:5000 -v $(pwd)/uploads:/app/uploads ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

**macOS (Intel)**
```bash
docker pull ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
docker run -d --name sim-apdu-analyzer -p 5000:5000 -v $(pwd)/uploads:/app/uploads ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

**Linux**
```bash
docker pull ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
docker run -d --name sim-apdu-analyzer -p 5000:5000 -v $(pwd)/uploads:/app/uploads ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
```

#### Docker Management Commands

```bash
# Check container status
docker ps

# View logs
docker logs sim-apdu-analyzer

# Stop container
docker stop sim-apdu-analyzer

# Start container
docker start sim-apdu-analyzer

# Remove container
docker rm -f sim-apdu-analyzer
```

#### Access
Open your browser and navigate to: `http://localhost:5000`

---

### 📦 Build from Source (Advanced)

If you want to build the Docker image yourself:

```bash
# Clone the repository
git clone https://github.com/joostone-ahn/SIM-APDU-Analyzer.git
cd SIM-APDU-Analyzer

# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t sim-apdu-analyzer:latest .
docker run -d -p 5000:5000 --name sim-apdu-analyzer sim-apdu-analyzer:latest
```

For more information, see the documentation in the `docs/` directory

---

## 📖 How to Use

### Step 1: Prepare Your Log File
Capture APDU logs using one of the supported tools:
- **Qualcomm**: QXDM Professional or QCAT
- **Samsung**: Shannon DM (Exynos chipsets)

Save the log as a `.txt` file.

### Step 2: Upload and Analyze
1. Click **📂 File** button to upload your log file
2. Select **SIM1** or **SIM2** from the dropdown
3. Click **Analyze** button
4. Wait for processing to complete

### Step 3: Explore Results

#### APDU Tab
- **Summary Panel**: List of all APDU commands with color coding
  - Click any row to see detailed analysis
- **Protocol Analysis**: Raw TX/RX data with timestamps
- **Application Analysis**: Decoded command parameters and file information

#### File System Tab
- **File List**: All files read during the session
  - Yellow highlight: Important OTA-updated files (IMSI, MSISDN, etc.)
  - Green highlight: Other updated files
- **File Contents**: Raw hexadecimal data
- **File Parsing**: Interpreted data (phone numbers, PLMN lists, etc.)
- **💾 Save to Excel**: Export complete file system data

---

## 🎨 Color Guide

### APDU Tab

| Color | Meaning | Examples |
|-------|---------|----------|
| 🔴 **Red** | Errors and failures | `ERROR`, malformed APDU |
| 💜 **Magenta** | Authentication re-sync | `Re-Sync` (AKA failure) |
| ⚪ **Gray** | Unknown operations | `SELECT (X)`, `Unknown` |
| 💛 **Yellow** | Proactive SIM commands | `ENVELOPE`, `REFRESH` |
| 💙 **Cyan** | Power events | `RESET`, `POWER` |
| 🔵 **Light Blue** | Channel management | `MANAGE CHANNEL` |
| 💚 **Light Green** | Authentication | `AUTHENTICATE` |

### File System Tab

| Color | Meaning | Files |
|-------|---------|-------|
| 💛 **Yellow** | Critical OTA updates | IMSI, MSISDN, OPLMNwAcT, ACC, Routing_Ind, IMPI, IMPU |
| 💚 **Light Green** | General OTA updates | All other updated files |

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

### Desktop
- **PyQt5**: Cross-platform GUI framework

### Deployment
- **Gunicorn**: WSGI HTTP server
- **Docker**: Containerization support
- **Heroku**: Cloud deployment ready

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
│                                              │
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

## 📚 Documentation

- **User Manuals**: See `docs/` directory for detailed guides
- **Sample Logs**: [Google Drive](https://drive.google.com/drive/folders/1I1Bpgms0mXRy9NLk4kg_3K9BFDVbe9LD)

---

## 🐳 Docker Deployment

### Quick Docker Commands

```bash
# Pull and run pre-built image from GitHub Container Registry
docker pull ghcr.io/joostone-ahn/sim-apdu-analyzer:latest
docker run -d -p 5000:5000 --name sim-apdu-analyzer ghcr.io/joostone-ahn/sim-apdu-analyzer:latest

# Or build from source
docker-compose up -d

# Access application at http://localhost:5000
```

### Docker Management

```bash
# Check status
docker ps

# View logs
docker logs sim-apdu-analyzer

# Stop container
docker stop sim-apdu-analyzer

# Start container
docker start sim-apdu-analyzer

# Remove container
docker rm -f sim-apdu-analyzer
```

---

## 🔐 Security & Privacy

### Data Handling
- ✅ **Server-Side Only**: All processing happens on the server
- ✅ **Session-Based**: Files stored in temporary session storage
- ✅ **No Persistence**: Data deleted when session expires
- ✅ **No External Calls**: No data sent to third parties

### Sensitive Information
Logs may contain:
- IMSI (International Mobile Subscriber Identity)
- MSISDN (Phone numbers)
- ICCID (SIM card serial numbers)
- Authentication keys (RAND, AUTN, RES)

**⚠️ Recommendation**: Deploy on internal networks or use locally

---

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Test Structure
```
tests/
├── unit/           # Unit tests for individual modules
├── integration/    # End-to-end pipeline tests
├── performance/    # Performance benchmarks
└── fixtures/       # Sample log files
```

---

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-local.txt

# Install pre-commit hooks
pre-commit install

# Run linters
black .
flake8 .
mypy .
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints (Python 3.11+)
- Write docstrings (Google style)
- Keep functions under 50 lines

---

## 📊 Performance

### Benchmarks
- **Processing Speed**: 10,000+ messages/second
- **Memory Usage**: < 500MB for 100MB log files
- **Response Time**: < 500ms for AJAX requests
- **Supported Size**: Up to 200MB log files

### Optimization Tips
- Use SIM port filtering to reduce data
- Apply time range filters for large logs
- Export to Excel for offline analysis

---

## 🔧 Troubleshooting

### Common Issues

#### "Unknown log format" Error
- **Cause**: Log file doesn't contain `[0x19B7]` or `USIM_MAIN`
- **Solution**: Verify log capture settings in QXDM/QCAT/Shannon DM

#### Slow Processing
- **Cause**: Very large log file (> 100MB)
- **Solution**: Split log file or use time range filtering

#### Missing File Names
- **Cause**: Non-standard DF/EF IDs
- **Solution**: Check `file_system.py` for supported files

#### Excel Export Fails
- **Cause**: Special characters in file contents
- **Solution**: Update to latest version (includes character filtering)

---

## 📝 Changelog

### v3.2 (Current)
- ✨ Added Excel export functionality
- ✨ Added README page in web interface
- 🐛 Fixed character encoding issues
- 📚 Improved documentation

### v3.1
- ✨ Added Shannon DM log support
- ✨ Added OTA update tracking
- ✨ Added 5G file system support (DF 5GS)
- 🐛 Fixed logical channel handling

### v3.0
- ✨ Web version release
- ✨ Flask-based architecture
- ✨ Session management
- 🎨 Modern UI design

### v2.x
- ✨ PyQt5 desktop version
- ✨ Clipboard support
- ✨ Multi-select analysis

### v1.x
- 🎉 Initial release
- ✨ QXDM log parsing
- ✨ Basic APDU analysis

---

## 📖 References

### 3GPP Standards
- [TS 31.102](https://www.3gpp.org/DynaReport/31102.htm) - USIM Application
- [TS 31.103](https://www.3gpp.org/DynaReport/31103.htm) - ISIM Application
- [TS 31.111](https://www.3gpp.org/DynaReport/31111.htm) - USIM Application Toolkit

### ETSI Standards
- [TS 102.221](https://www.etsi.org/deliver/etsi_ts/102200_102299/102221/) - UICC-Terminal Interface
- [TS 102.223](https://www.etsi.org/deliver/etsi_ts/102200_102299/102223/) - Card Application Toolkit

### Other Standards
- [ISO/IEC 7816-4](https://www.iso.org/standard/54550.html) - Integrated Circuit Cards
- [GSMA SGP.02](https://www.gsma.com/esim/) - Remote Provisioning Architecture

---

## 👥 Team

**Developer**: JUSEOK AHN (안주석)  
**Email**: ajs3013@lguplus.co.kr  
**Organization**: LG U+  
**Role**: Senior Engineer, SIM/eSIM Platform

### Support
- 📧 Email: ajs3013@lguplus.co.kr
- 📁 Sample Logs: [Google Drive](https://drive.google.com/drive/folders/1I1Bpgms0mXRy9NLk4kg_3K9BFDVbe9LD)
- 📖 Documentation: See `docs/` directory

---

## 📄 License & Credits

**© 2025 JUSEOK AHN &lt;ajs3013@lguplus.co.kr&gt; All rights reserved.**

This software is proprietary and confidential. Developed for internal analysis, SIM validation, and automation of diagnostic workflows at LG U+.

### Applicable For
- QA teams performing SIM/eSIM testing
- Engineers debugging modem-SIM communication
- Researchers working with modern SIM/eSIM infrastructure
- Network operators validating SIM profiles

### Patent Information
Related patent applications are documented in `docs/특허/` directory.

---

## 🌟 Acknowledgments

Special thanks to:
- LG U+ SIM/eSIM Platform Team
- 3GPP and ETSI for comprehensive standards documentation
- Open source community for excellent tools and libraries

---

**Made with ❤️ for better SIM/eSIM analysis**
