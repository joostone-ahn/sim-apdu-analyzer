# QXDM-SIM-APDU-Analyzer

eSIM device supporting DSDS(Dual SIM Dual Standby) has following limitations.
 - The interface between eSIM and ME(Mobile Equipment) can not be traced with contact-based SIM tracer alike Minimove (COMPRION) 
 - ME's logs includes mixed APDU logs from pSIM and eSIM.

This tool helps you to overcome the above limits.
 - APDU logs can be analyzed on application-level and protocol-leved similarly to contact-based SIM tracer.
 - APDU logs from pSIM or eSIM can be sorted by user's selection.


[Guide]
1) run main.py
2) click 'Open file' or 'Clipboard' button
3) select SIM1 or SIM2
4) click 'Execute' button

※ text file(.txt) in 'file_sample' directory, which is filtered with 'UIM APDU [0x19B7]' from QCAT logs

![image](https://github.com/user-attachments/assets/bea42c76-a26a-403d-adb5-67ae38949d44)

![image](https://github.com/user-attachments/assets/90a1dd3d-eaea-45c7-9737-e78dbd3e94e1)
