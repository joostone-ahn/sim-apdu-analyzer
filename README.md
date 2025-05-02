# 🔍 SIM-APDU-Analyzer

### A powerful tool for analyzing SIM/eSIM APDU logs from QXDM or QCAT

Modern eSIM-enabled devices with **DSDS (Dual SIM Dual Standby)** present new challenges in APDU-level tracing:

* Traditional contact-based SIM tracers (e.g., COMPRION Minimove) **cannot intercept communication** between eSIM and Mobile Equipment (ME).
* Log traces from ME contain **interleaved APDU data** from both pSIM and eSIM, making it difficult to distinguish between them.

---

### 💡 What This Tool Does

**QXDM-SIM-APDU-Analyzer** bridges that gap by enabling detailed, protocol-aware analysis of APDU logs — even in dual SIM environments.

* Analyze APDUs at **application** and **protocol layer levels**, similar to physical SIM trace tools.
* **Distinguish and filter** APDU logs by SIM type (SIM1 or SIM2), allowing focused inspection of either **pSIM** or **eSIM** traffic.
* Designed for logs captured from QXDM/QCAT — specifically `UIM APDU [0x19B7]` messages.

---

### 🛠 How to Use

1. Run the tool:

   ```bash
   python main.py
   ```

2. Choose input:

   * Click **"Open File"** to load a `.txt` file
   * Or use **"Clipboard"** to paste copied log text

3. Select target SIM:

   * **SIM1** or **SIM2** based on which SIM’s APDU logs you want to view

4. Click **"Execute"** to analyze and visualize the log contents

---

### 📂 Sample Input

Use `.txt` log files in the `file_sample/` directory, filtered with:

> **UIM APDU \[0x19B7]**
> (Captured from Qualcomm QCAT logs)

---

### 📸 UI Preview

![image](https://github.com/user-attachments/assets/7246db3b-46c2-4ed1-86f1-d170f112fc41)

![image](https://github.com/user-attachments/assets/1dbf6b2b-95c3-43f9-b4d4-c14d77c19566)
