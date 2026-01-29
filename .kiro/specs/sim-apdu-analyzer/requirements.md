# Requirements Document: SIM APDU Analyzer

## Introduction

SIM APDU Analyzer는 SIM/eSIM APDU 로그를 분석하여 Protocol, Application, File System 3계층으로 시각화하는 웹 기반 분석 도구입니다. 이 시스템은 3GPP TS 31.102/31.103 표준을 기반으로 APDU 명령어를 해석하며, QXDM, QCAT, Shannon DM 로그 포맷을 지원합니다.

## Glossary

- **APDU**: Application Protocol Data Unit - SIM 카드와 단말기 간 통신 프로토콜 단위
- **System**: SIM APDU Analyzer 웹 애플리케이션
- **Parser**: 로그 파일에서 APDU 메시지를 추출하고 구조화하는 모듈
- **Protocol_Analyzer**: TX/RX 쌍을 매칭하고 APDU Case를 분류하는 모듈
- **Application_Analyzer**: INS 코드를 해석하고 파일 시스템을 추적하는 모듈
- **File_System_Analyzer**: READ 명령어로 읽은 파일 목록을 생성하는 모듈
- **Web_Interface**: Flask 기반 웹 사용자 인터페이스
- **QXDM**: Qualcomm eXtensible Diagnostic Monitor 로그 포맷
- **QCAT**: Qualcomm QCAT 로그 포맷
- **Shannon_DM**: Samsung Shannon DM 로그 포맷
- **DSDS**: Dual SIM Dual Standby - 듀얼 SIM 환경
- **INS**: Instruction byte - APDU 명령어 코드
- **DF**: Dedicated File - SIM 파일 시스템의 디렉토리
- **EF**: Elementary File - SIM 파일 시스템의 파일
- **SFI**: Short File Identifier - 파일의 짧은 식별자
- **Logical_Channel**: SIM 카드와의 논리적 통신 채널 (0-19)
- **Status_Word**: APDU 응답의 상태 코드 (SW1, SW2)
- **OTA**: Over-The-Air - 무선 업데이트

## Requirements

### Requirement 1: 로그 파일 업로드 및 포맷 감지

**User Story:** As a SIM engineer, I want to upload log files and have the system automatically detect the format, so that I can analyze logs from different tools without manual configuration.

#### Acceptance Criteria

1. WHEN a user uploads a text file, THE System SHALL accept files with .txt extension
2. WHEN a log file is uploaded, THE System SHALL automatically detect the format by examining file content
3. WHEN the log contains '[0x19B7]' tag, THE System SHALL identify it as QXDM or QCAT format
4. WHEN the log contains 'USIM_MAIN' string, THE System SHALL identify it as Shannon DM format
5. WHEN format detection fails, THE System SHALL return an error message to the user
6. THE System SHALL store uploaded files in a designated upload directory
7. THE System SHALL maintain the uploaded file in session for subsequent analysis

### Requirement 2: SIM 포트 선택 및 필터링

**User Story:** As a SIM engineer, I want to select which SIM (SIM1 or SIM2) to analyze in DSDS environment, so that I can focus on specific SIM card behavior.

#### Acceptance Criteria

1. THE System SHALL provide a dropdown interface for selecting SIM1 or SIM2
2. WHEN a SIM is selected, THE System SHALL filter messages belonging to that SIM port only
3. WHEN duplicate sequence numbers are detected for the same port, THE System SHALL remove duplicate messages
4. THE System SHALL maintain the selected SIM choice in session across page interactions
5. WHEN the user changes SIM selection, THE System SHALL re-analyze the log with the new selection

### Requirement 3: APDU 메시지 파싱

**User Story:** As a SIM engineer, I want the system to parse APDU messages from log files, so that I can see structured message data.

#### Acceptance Criteria

1. WHEN parsing QXDM format, THE Parser SHALL extract timestamp, SIM port, message type, and data from each log line
2. WHEN parsing QCAT format, THE Parser SHALL identify messages by '0x19B7' tag and extract structured fields
3. WHEN parsing Shannon DM format, THE Parser SHALL convert Shannon-specific format to standard APDU format
4. THE Parser SHALL handle multi-line APDU data by concatenating lines until closing brace
5. THE Parser SHALL extract sequence numbers from log messages
6. THE Parser SHALL identify message types as TX, RX, ATR, PPS, or RESET
7. WHEN consecutive duplicate messages are detected, THE Parser SHALL remove duplicates
8. THE Parser SHALL preserve message order from the original log file

### Requirement 4: 프로토콜 레벨 분석

**User Story:** As a SIM engineer, I want to see TX/RX message pairs and APDU case classification, so that I can understand the protocol-level communication flow.

#### Acceptance Criteria

1. WHEN analyzing messages, THE Protocol_Analyzer SHALL pair TX messages with corresponding RX messages
2. THE Protocol_Analyzer SHALL classify APDU commands into Case 1, Case 2, Case 3, or Case 4
3. WHEN consecutive TX or RX messages are detected without pairing, THE Protocol_Analyzer SHALL flag as ERROR_1
4. WHEN TX data length does not match P3 parameter, THE Protocol_Analyzer SHALL flag as ERROR_2
5. WHEN Status Word is incomplete or missing, THE Protocol_Analyzer SHALL flag as ERROR_3
6. THE Protocol_Analyzer SHALL handle POWER_OFF and RESET events as separate message types
7. WHEN POWER_OFF occurs during APDU transaction, THE Protocol_Analyzer SHALL mark it as error and create separate POWER_OFF entry
8. THE Protocol_Analyzer SHALL validate that RX messages include INS byte matching the TX command

### Requirement 5: 애플리케이션 레벨 분석

**User Story:** As a SIM engineer, I want to see interpreted APDU commands with file system context, so that I can understand what operations are being performed.

#### Acceptance Criteria

1. THE Application_Analyzer SHALL interpret INS codes using 3GPP TS 31.102/31.103 standard command mappings
2. THE Application_Analyzer SHALL maintain logical channel state for channels 0-19
3. THE Application_Analyzer SHALL track current DF and EF for each logical channel
4. WHEN SELECT command is executed, THE Application_Analyzer SHALL update current DF/EF in the logical channel
5. WHEN Status Word indicates error, THE Application_Analyzer SHALL display error description from 3GPP specifications
6. THE Application_Analyzer SHALL detect and mark commands with Status Words 6A82, 6A83, 6282, 6982 as failed operations
7. THE Application_Analyzer SHALL support extended logical channels (4-19) by parsing CLA byte bits
8. WHEN unknown INS code is encountered, THE Application_Analyzer SHALL display "Unknown INS" with hex value

### Requirement 6: SELECT 명령어 처리

**User Story:** As a SIM engineer, I want SELECT commands to update the file system context, so that subsequent commands are interpreted in the correct file context.

#### Acceptance Criteria

1. WHEN SELECT command targets AID starting with 'A0', THE Application_Analyzer SHALL update current DF to the AID
2. WHEN SELECT command targets MF or DF, THE Application_Analyzer SHALL update current DF and clear current EF
3. WHEN SELECT command targets EF, THE Application_Analyzer SHALL update current EF while maintaining current DF
4. WHEN SELECT targets '7FFF', THE Application_Analyzer SHALL select the previously stored ADF
5. THE Application_Analyzer SHALL handle hierarchical file paths by parsing multi-byte file IDs
6. WHEN SELECT fails with error Status Word, THE Application_Analyzer SHALL mark the command as failed but not update file context
7. THE Application_Analyzer SHALL distinguish between USIM ADF (A0000000871002) and ISIM ADF (A0000000871004)

### Requirement 7: Short File ID (SFI) 처리

**User Story:** As a SIM engineer, I want commands using SFI to be correctly mapped to file names, so that I can identify which files are being accessed.

#### Acceptance Criteria

1. WHEN READ BINARY, UPDATE BINARY, or INCREASE commands use SFI, THE Application_Analyzer SHALL extract SFI from P1 byte
2. WHEN READ RECORD, UPDATE RECORD, or SEARCH RECORD commands use SFI, THE Application_Analyzer SHALL extract SFI from P2 byte
3. WHEN RETRIEVE DATA or SET DATA commands use SFI, THE Application_Analyzer SHALL extract SFI from P2 byte
4. THE Application_Analyzer SHALL map SFI to file ID using current DF context
5. WHEN SFI is used, THE Application_Analyzer SHALL update current EF to the mapped file ID
6. WHEN SFI is unknown in current DF, THE Application_Analyzer SHALL display error message with SFI value
7. THE Application_Analyzer SHALL display SFI value in command summary when SFI is used

### Requirement 8: AUTHENTICATE 명령어 처리

**User Story:** As a SIM engineer, I want AUTHENTICATE commands to show RAND, AUTN, RES, and AUTS values, so that I can analyze authentication procedures and detect re-synchronization.

#### Acceptance Criteria

1. WHEN AUTHENTICATE command is executed, THE Application_Analyzer SHALL parse RAND value from command data
2. THE Application_Analyzer SHALL parse AUTN value from command data
3. WHEN authentication succeeds, THE Application_Analyzer SHALL parse RES value from response data
4. WHEN authentication fails with re-sync, THE Application_Analyzer SHALL parse AUTS value from response data
5. WHEN response type is 'DC', THE Application_Analyzer SHALL mark the command as "Re-Sync"
6. THE Application_Analyzer SHALL display ADF context (USIM or ISIM) for AUTHENTICATE commands
7. THE Application_Analyzer SHALL format RAND, AUTN, RES, AUTS values as separate labeled fields

### Requirement 9: FETCH 명령어 처리

**User Story:** As a SIM engineer, I want FETCH commands to show proactive command types, so that I can understand SIM-initiated operations.

#### Acceptance Criteria

1. WHEN FETCH command contains proactive command tag '810301', THE Application_Analyzer SHALL extract command type
2. THE Application_Analyzer SHALL map proactive command type codes to names using ETSI TS 102.223 specification
3. WHEN FETCH type is REFRESH, THE Application_Analyzer SHALL display REFRESH sub-type
4. WHEN FETCH type is POLL INTERVAL, THE Application_Analyzer SHALL parse and display interval in seconds
5. WHEN FETCH type is SETUP EVENT LIST, THE Application_Analyzer SHALL parse and display event list items
6. THE Application_Analyzer SHALL display proactive command type in parentheses after FETCH command name

### Requirement 10: ENVELOPE 명령어 처리

**User Story:** As a SIM engineer, I want ENVELOPE commands to show envelope types and event downloads, so that I can track terminal-to-SIM communications.

#### Acceptance Criteria

1. WHEN ENVELOPE command is executed, THE Application_Analyzer SHALL extract envelope type from first byte of command data
2. THE Application_Analyzer SHALL map envelope type codes to names using ETSI TS 101.220 specification
3. WHEN envelope type is Event Download, THE Application_Analyzer SHALL parse and display specific event type
4. THE Application_Analyzer SHALL display envelope type in parentheses after ENVELOPE command name

### Requirement 11: TERMINAL RESPONSE 명령어 처리

**User Story:** As a SIM engineer, I want TERMINAL RESPONSE commands to show result codes, so that I can verify terminal responses to proactive commands.

#### Acceptance Criteria

1. WHEN TERMINAL RESPONSE command is executed, THE Application_Analyzer SHALL extract proactive command type from response data
2. THE Application_Analyzer SHALL parse result code from response data
3. WHEN result code indicates error, THE Application_Analyzer SHALL display error description from ETSI TS 102.223
4. THE Application_Analyzer SHALL mark non-successful result codes as errors

### Requirement 12: MANAGE CHANNEL 명령어 처리

**User Story:** As a SIM engineer, I want MANAGE CHANNEL commands to show channel operations, so that I can track logical channel lifecycle.

#### Acceptance Criteria

1. WHEN MANAGE CHANNEL opens a channel, THE Application_Analyzer SHALL display "OPEN" with channel number
2. WHEN MANAGE CHANNEL closes a channel, THE Application_Analyzer SHALL display "CLOSE" with channel number
3. THE Application_Analyzer SHALL parse channel number from P2 byte for CLOSE operations
4. THE Application_Analyzer SHALL parse channel number from response data for OPEN operations

### Requirement 13: 파일 시스템 뷰 생성

**User Story:** As a SIM engineer, I want to see a table of all files read from the SIM, so that I can review file contents and detect OTA updates.

#### Acceptance Criteria

1. WHEN READ BINARY or READ RECORD commands succeed, THE File_System_Analyzer SHALL add file entry to file system table
2. THE File_System_Analyzer SHALL display DF name, EF name, DF ID, EF ID for each file
3. THE File_System_Analyzer SHALL classify files as TF (Transparent File) or LF (Linear Fixed)
4. WHEN SFI is used, THE File_System_Analyzer SHALL display SFI value in the table
5. THE File_System_Analyzer SHALL display record number for Linear Fixed files
6. THE File_System_Analyzer SHALL display offset and length for Transparent Files
7. THE File_System_Analyzer SHALL store file contents in hexadecimal format
8. THE File_System_Analyzer SHALL detect OTA updates by comparing contents of same file read multiple times
9. WHEN file contents change between reads, THE File_System_Analyzer SHALL mark file as "OTA_updated"
10. THE File_System_Analyzer SHALL remove duplicate file entries with identical contents
11. THE File_System_Analyzer SHALL sort files by DF, then by File ID, then by record number

### Requirement 14: 파일 내용 파싱

**User Story:** As a SIM engineer, I want specific file types to be parsed into human-readable format, so that I can understand file contents without manual decoding.

#### Acceptance Criteria

1. WHEN file is ICCID, THE System SHALL parse BCD-encoded digits and display as decimal string
2. WHEN file is IMSI, THE System SHALL parse BCD-encoded digits and display as decimal string
3. WHEN file is IMPI, IMPU, or P-CSCF, THE System SHALL decode UTF-8 text from hex data
4. WHEN file is ACC, THE System SHALL display hex and binary representation
5. WHEN file is HPLMNwAcT, OPLMNwAcT, or PLMNwAcT, THE System SHALL parse MCC, MNC, and Access Technology for each PLMN entry
6. WHEN file is FPLMN, THE System SHALL parse MCC and MNC for each forbidden PLMN entry
7. WHEN file is MSISDN, THE System SHALL parse Alpha ID, TON/NPI, and dialing number
8. WHEN file is UST, THE System SHALL parse service table and display enabled/disabled status for each service
9. WHEN file is IST, THE System SHALL parse ISIM service table and display enabled/disabled status for each service
10. WHEN file is EPSLOCI, THE System SHALL parse GUTI, TAI, and EPS update status
11. THE System SHALL display parsed content alongside raw hex data

### Requirement 15: 웹 인터페이스 - 파일 업로드

**User Story:** As a SIM engineer, I want a simple web interface to upload log files, so that I can quickly start analysis.

#### Acceptance Criteria

1. THE Web_Interface SHALL display a file upload form on the main page
2. THE Web_Interface SHALL provide a dropdown to select SIM1 or SIM2
3. WHEN user uploads a file, THE Web_Interface SHALL validate file extension is .txt
4. WHEN upload succeeds, THE Web_Interface SHALL display the uploaded filename
5. THE Web_Interface SHALL maintain session state for uploaded file and selected SIM
6. WHEN user returns to main page with GET request, THE Web_Interface SHALL clear previous session data

### Requirement 16: 웹 인터페이스 - 분석 결과 표시

**User Story:** As a SIM engineer, I want to see analysis results in organized tabs, so that I can navigate between different views easily.

#### Acceptance Criteria

1. THE Web_Interface SHALL display analysis results in two tabs: APDU and File System
2. THE Web_Interface SHALL display summary list in APDU tab showing all commands with timestamps
3. WHEN user clicks on a summary item, THE Web_Interface SHALL display protocol details and application details
4. THE Web_Interface SHALL display file system table in File System tab
5. WHEN user clicks on a file entry, THE Web_Interface SHALL display file contents and parsed data
6. THE Web_Interface SHALL preserve tab selection and scroll position during interactions

### Requirement 17: 웹 인터페이스 - 색상 코딩

**User Story:** As a SIM engineer, I want different command types to be color-coded, so that I can quickly identify important events and errors.

#### Acceptance Criteria

1. WHEN command contains "ERROR", THE Web_Interface SHALL display the line in red color
2. WHEN command contains "Re-Sync", THE Web_Interface SHALL display the line in magenta color
3. WHEN command contains "(X)", "(*)", or "Unknown", THE Web_Interface SHALL display the line in gray color
4. WHEN command is ENVELOPE or REFRESH, THE Web_Interface SHALL display the line in yellow color
5. WHEN command is RESET or POWER, THE Web_Interface SHALL display the line in cyan color
6. WHEN command is MANAGE CHANNEL, THE Web_Interface SHALL display the line in light blue color
7. WHEN command is AUTHENTICATE, THE Web_Interface SHALL display the line in light green color

### Requirement 18: 웹 인터페이스 - Excel 내보내기

**User Story:** As a SIM engineer, I want to export file system data to Excel, so that I can perform additional analysis or share results.

#### Acceptance Criteria

1. THE Web_Interface SHALL provide an "Export to Excel" button in File System tab
2. WHEN user clicks export button, THE System SHALL generate Excel file with all file system data
3. THE System SHALL include all columns: DF, File, DF_Id, File_Id, Type, SFI, REC, OFS, LEN, ref, contents, parsing
4. THE System SHALL remove invalid Excel characters from cell contents before export
5. THE System SHALL send Excel file as downloadable attachment with filename "file_system_export.xlsx"

### Requirement 19: 3GPP 표준 준수

**User Story:** As a SIM engineer, I want the system to follow 3GPP standards, so that analysis results are accurate and reliable.

#### Acceptance Criteria

1. THE System SHALL support DF and EF definitions from 3GPP TS 31.102 Release 16 for USIM
2. THE System SHALL support DF and EF definitions from 3GPP TS 31.103 Release 16 for ISIM
3. THE System SHALL support command codes from ETSI TS 102.221
4. THE System SHALL support Status Word definitions from ETSI TS 102.221 section 10.2
5. THE System SHALL support proactive command types from ETSI TS 102.223
6. THE System SHALL support envelope types from ETSI TS 101.220
7. THE System SHALL support 5G file system (DF 5GS) from 3GPP TS 31.102
8. THE System SHALL map file IDs to standard file names using 3GPP specifications

### Requirement 20: 에러 처리 및 검증

**User Story:** As a SIM engineer, I want the system to detect and report errors in APDU sequences, so that I can identify communication problems.

#### Acceptance Criteria

1. WHEN Status Word is 6A82, THE System SHALL report "File not found" error
2. WHEN Status Word is 6A83, THE System SHALL report "Record not found" error
3. WHEN Status Word is 6282, THE System SHALL report "Unsuccessful search" error
4. WHEN Status Word is 6982, THE System SHALL report "Security status not satisfied" error
5. WHEN Status Word is not 9000 or 91xx for data commands, THE System SHALL report error with Status Word value
6. WHEN current DF is not determined, THE System SHALL report "DF NOT determined" error
7. WHEN file ID is unknown in current DF, THE System SHALL report "Unknown file id" error
8. WHEN DF is unknown, THE System SHALL report "Unknown DF" error
9. THE System SHALL display error messages with reference to 3GPP specification sections

### Requirement 21: 성능 요구사항

**User Story:** As a SIM engineer, I want the system to process large log files efficiently, so that I can analyze long test sessions without delays.

#### Acceptance Criteria

1. THE System SHALL process log files up to 10MB in size within 30 seconds
2. THE System SHALL handle logs with up to 10,000 APDU messages
3. THE System SHALL maintain responsive web interface during file processing
4. THE System SHALL use session storage to avoid re-processing on page refresh
5. THE System SHALL clean up uploaded files older than 24 hours

### Requirement 22: 데이터 무결성

**User Story:** As a SIM engineer, I want the system to preserve original log data, so that analysis results are traceable to source.

#### Acceptance Criteria

1. THE System SHALL preserve original timestamp from log files
2. THE System SHALL preserve original message order from log files
3. THE System SHALL not modify original uploaded files
4. WHEN duplicate messages are removed, THE System SHALL keep the first occurrence
5. THE System SHALL maintain line number references to original log file

### Requirement 23: 다중 로그 포맷 지원

**User Story:** As a SIM engineer, I want to analyze logs from different tools, so that I can work with various test equipment.

#### Acceptance Criteria

1. THE System SHALL support QXDM log format with [0x19B7] tag
2. THE System SHALL support QCAT log format with 0x19B7 message ID
3. THE System SHALL support Shannon DM log format with USIM_MAIN identifier
4. THE System SHALL convert Shannon DM format to standard APDU format internally
5. THE System SHALL handle multi-line APDU data in all supported formats
6. THE System SHALL extract timestamp in format HH:MM:SS.mmm from all supported formats

### Requirement 24: Dual SIM 지원

**User Story:** As a SIM engineer, I want to analyze each SIM separately in DSDS devices, so that I can isolate SIM-specific issues.

#### Acceptance Criteria

1. THE System SHALL identify SIM port from log messages (SLOT_1 or SLOT_2)
2. THE System SHALL allow user to select which SIM port to analyze
3. WHEN SIM port is selected, THE System SHALL filter all messages to show only selected port
4. THE System SHALL handle logs containing both SIM1 and SIM2 messages
5. THE System SHALL maintain separate logical channel state for each SIM port

### Requirement 25: 배포 및 운영

**User Story:** As a system administrator, I want the application to be easily deployable, so that I can run it in different environments.

#### Acceptance Criteria

1. THE System SHALL be packaged as Docker container
2. THE System SHALL use Gunicorn as production WSGI server
3. THE System SHALL expose service on port 8090
4. THE System SHALL create required directories (uploads, flask_session) on startup
5. THE System SHALL use filesystem-based session storage
6. THE System SHALL serve static files and templates correctly in Docker environment
