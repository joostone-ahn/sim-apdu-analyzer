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

![image](https://github.com/joostone-ahn/SIM-APDU-Analyzer-for-QXDM/assets/98713651/433349e4-63e7-4392-8e42-92a659bc3a25)
![image](https://github.com/joostone-ahn/SIM-APDU-Analyzer-for-QXDM/assets/98713651/1f17cf00-3238-45f8-93a4-16c3e00e2947)
![image](https://github.com/joostone-ahn/SIM-APDU-Analyzer-for-QXDM/assets/98713651/b6629585-e379-4b3f-bc2c-f8f14d890d98)
