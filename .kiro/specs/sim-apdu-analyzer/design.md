# Design Document: SIM APDU Analyzer

## Overview

SIM APDU Analyzer는 3계층 아키텍처(Protocol, Application, File System)를 사용하여 SIM/eSIM APDU 로그를 분석하는 Flask 기반 웹 애플리케이션입니다. 시스템은 파이프라인 방식으로 로그 데이터를 처리하며, 각 단계에서 점진적으로 추상화 수준을 높여 최종적으로 사용자 친화적인 분석 결과를 제공합니다.

### Key Design Principles

1. **Pipeline Architecture**: 데이터는 순차적 파이프라인을 통해 처리됩니다 (Parsing → Port Filtering → Protocol Analysis → Application Analysis → File System View)
2. **Stateful Analysis**: 각 논리 채널의 파일 시스템 컨텍스트를 유지하여 명령어를 올바르게 해석합니다
3. **Standards Compliance**: 3GPP TS 31.102/31.103 및 ETSI 표준을 엄격히 준수합니다
4. **Session-based Processing**: Flask 세션을 사용하여 중간 처리 결과를 저장하고 재처리를 방지합니다
5. **Format Agnostic**: 다양한 로그 포맷을 내부 표준 형식으로 변환하여 처리합니다

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Interface (Flask)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Upload Form  │  │  APDU Tab    │  │ File System  │          │
│  │  + SIM Select│  │  + Protocol  │  │  Tab         │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Pipeline                         │
│                                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Parser  │──▶│  Port    │──▶│ Protocol │──▶│Application│    │
│  │ (msg_item│   │ Filter   │   │ Analyzer │   │ Analyzer  │    │
│  │   .py)   │   │ (port.py)│   │(msg_prot │   │ (msg_sum  │    │
│  └──────────┘   └──────────┘   │  .py)    │   │  .py)     │    │
│                                 └──────────┘   └──────────┘    │
│                                                      │           │
│                                                      ▼           │
│                                              ┌──────────────┐   │
│                                              │ File System  │   │
│                                              │  Analyzer    │   │
│                                              │ (msg_files   │   │
│                                              │   .py)       │   │
│                                              └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Reference Data Modules                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ file_system  │  │  command.py  │  │  spec_ref.py │          │
│  │    .py       │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  SELECT.py   │  │   READ.py    │  │short_file_id │          │
│  │              │  │              │  │    .py       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```


### Data Flow

1. **Upload Phase**: 사용자가 로그 파일을 업로드하고 SIM 포트를 선택
2. **Parsing Phase**: 로그 포맷을 감지하고 APDU 메시지를 추출
3. **Filtering Phase**: 선택된 SIM 포트의 메시지만 필터링
4. **Protocol Phase**: TX/RX 쌍을 매칭하고 APDU Case를 분류
5. **Application Phase**: INS 코드를 해석하고 파일 시스템 컨텍스트를 추적
6. **File System Phase**: READ 명령어로 읽은 파일 목록을 생성
7. **Presentation Phase**: 웹 인터페이스에 결과를 표시

## Components and Interfaces

### 1. Web Interface Component (main.py)

**Responsibility**: HTTP 요청 처리, 세션 관리, 결과 렌더링

**Key Functions**:
- `index()`: 메인 페이지 렌더링 및 파일 업로드 처리
- `analyze_line()`: 특정 APDU 메시지의 상세 분석 제공
- `file_detail()`: 파일 시스템 항목의 상세 정보 제공
- `download_excel()`: 파일 시스템 데이터를 Excel로 내보내기
- `get_line_color_class()`: 명령어 타입에 따른 색상 클래스 반환

**Interface**:
```python
# Input: HTTP POST with file upload and sim_select parameter
# Output: Rendered HTML with analysis results

# Session Data Structure:
{
    'filepath': str,           # Path to uploaded file
    'filename': str,           # Original filename
    'sim_select': int,         # Selected SIM (1 or 2)
    'msg_all': List[str],      # All log lines
    'msg_start': List[int],    # Start line indices
    'msg_end': List[int],      # End line indices
    'msg_SN': List[int],       # Sequence numbers
    'msg_port': List[int],     # SIM port numbers
    'msg_type': List[str],     # Message types (TX/RX/ATR/etc)
    'msg_data': List[str],     # APDU data in hex
    'prot_start': List[List[int]],  # Protocol-level start indices
    'prot_type': List[List[str]],   # Protocol-level types
    'prot_data': List[List[str]],   # Protocol-level data
    'sum_cmd': List[str],           # Command names
    'sum_read': List,               # Read command details
    'sum_error': List[str],         # Error messages
    'sum_log_ch': List[List[str]],  # Logical channel states
    'sum_log_ch_id': List[int],     # Logical channel IDs
    'df': List[dict]                # File system DataFrame as dict
}
```


### 2. Parser Component (msg_item.py)

**Responsibility**: 로그 파일에서 APDU 메시지 추출 및 구조화

**Key Functions**:
- `QCAT()`: QCAT 포맷 파싱
- `QXDM()`: QXDM 포맷 파싱
- `QXDM_filter()`: QXDM 로그 전처리
- `ShannonDM()`: Shannon DM 포맷을 QXDM 포맷으로 변환
- `basic_format()`: Shannon DM 메시지를 표준 포맷으로 변환
- `split_hex()`: 16진수 문자열을 2자리씩 분리

**Interface**:
```python
def QCAT(msg: List[str]) -> Tuple[List[int], List[int], List[int], 
                                   List[int], List[str], List[str]]:
    """
    Parse QCAT format log
    
    Args:
        msg: List of log lines
    
    Returns:
        msg_start: Start line index for each message
        msg_end: End line index for each message
        msg_SN: Sequence number for each message
        msg_port: SIM port (1 or 2) for each message
        msg_type: Message type (TX/RX/ATR/PPS/RESET)
        msg_data: APDU data in hex (spaces removed)
    """

def QXDM(msg_all: List[str]) -> Tuple[List[int], List[int], List[int],
                                       List[int], List[str], List[str]]:
    """
    Parse QXDM format log
    
    Args:
        msg_all: List of log lines (pre-filtered)
    
    Returns:
        Same as QCAT()
    
    Notes:
        - Handles multi-line APDU data
        - Removes consecutive duplicates
        - Supports ATR, PPS, TX, RX, RESET message types
    """

def ShannonDM(msg_all: List[str]) -> List[str]:
    """
    Convert Shannon DM format to QXDM format
    
    Args:
        msg_all: List of Shannon DM log lines
    
    Returns:
        List of log lines in QXDM format
    
    Notes:
        - Extracts USIM_MAIN messages
        - Converts to [0x19B7] tagged format
        - Handles fragmented APDU data
    """
```

**Format Detection Logic**:
```python
if '[0x19B7]' in msg_all[0]:
    # QXDM/QCAT format
    msg_all = msg_item.QXDM_filter(msg_all)
    result = msg_item.QXDM(msg_all)
elif 'USIM_MAIN' in msg_all[0] or 'USIM_MAIN' in msg_all[1]:
    # Shannon DM format
    msg_all = msg_item.ShannonDM(msg_all)
    result = msg_item.QXDM(msg_all)
else:
    # Default QCAT format
    result = msg_item.QCAT(msg_all)
```


### 3. Port Filter Component (port.py)

**Responsibility**: 선택된 SIM 포트의 메시지만 필터링

**Key Functions**:
- `process()`: 포트 인덱스를 기반으로 메시지 필터링 및 중복 제거

**Interface**:
```python
def process(input: Tuple, index: List[int]) -> Tuple[List[int], List[int], 
                                                       List[str], List[str]]:
    """
    Filter messages by SIM port and remove duplicates
    
    Args:
        input: (msg_all, msg_start, msg_end, msg_SN, msg_type, msg_data)
        index: List of indices for selected SIM port
    
    Returns:
        exe_start: Filtered start indices
        exe_end: Filtered end indices
        exe_type: Filtered message types
        exe_data: Filtered APDU data
    
    Notes:
        - Removes messages with duplicate sequence numbers
        - Preserves message order
    """
```

**Duplicate Detection Logic**:
- 동일한 시퀀스 번호를 가진 연속 메시지는 중복으로 간주
- 중복 메시지 중 마지막 메시지만 유지 (로그 파일의 빈 줄로 구분)

### 4. Protocol Analyzer Component (msg_prot.py)

**Responsibility**: TX/RX 쌍 매칭 및 APDU Case 분류

**Key Functions**:
- `process()`: 메시지를 APDU 트랜잭션으로 그룹화하고 Case 분류
- `rst()`: 특정 트랜잭션의 프로토콜 상세 정보 포맷팅

**Interface**:
```python
def process(input: Tuple) -> Tuple[List[List[int]], List[List[str]], 
                                    List[List[str]], List[List[str]]]:
    """
    Group messages into APDU transactions and classify cases
    
    Args:
        input: (exe_start, exe_end, exe_type, exe_data)
    
    Returns:
        prot_start: List of start indices for each transaction
        prot_end: List of end indices for each transaction
        prot_type: List of message types for each transaction
        prot_data: List of APDU data for each transaction
    
    Notes:
        - Validates TX/RX pairing
        - Classifies as Case1/Case2/Case3/Case4
        - Detects errors (consecutive TX/RX, length mismatch, SW error)
    """
```

**APDU Case Classification**:
```
Case 1: TX(5 bytes) → RX(SW only, 4 bytes)
Case 2: TX(5 bytes) → RX(INS + data + SW)
Case 3: TX(5 bytes) → RX(INS only) → TX(data) → RX(SW)
Case 4: TX(5 bytes) → RX(INS only) → TX(data) → RX(C0 + data + SW)
```

**Error Detection**:
1. **ERROR_1**: 연속된 TX 또는 RX (쌍이 맞지 않음)
2. **ERROR_2**: TX 데이터 길이가 P3 파라미터와 불일치
3. **ERROR_3**: Status Word 불완전 (4바이트 미만)
4. **POWER_OFF during APDU**: APDU 트랜잭션 중 전원 차단


### 5. Application Analyzer Component (msg_sum.py)

**Responsibility**: INS 코드 해석 및 파일 시스템 컨텍스트 추적

**Key Functions**:
- `rst()`: 모든 트랜잭션을 분석하여 요약 생성
- Command-specific parsing for SELECT, AUTHENTICATE, FETCH, ENVELOPE, etc.

**Interface**:
```python
def rst(input: Tuple) -> Tuple[List[str], List[List[str]], List[int], 
                                List[str], List, List[str]]:
    """
    Analyze APDU transactions at application level
    
    Args:
        input: (msg_all, prot_start, prot_type, prot_data)
    
    Returns:
        sum_rst: Summary strings for each transaction
        sum_log_ch: Logical channel state [DF, EF] for each transaction
        sum_log_ch_id: Logical channel ID for each transaction
        sum_cmd: Command name for each transaction
        sum_read: Read/Auth data for each transaction
        sum_error: Error messages for each transaction
    
    Notes:
        - Maintains logical channel state (0-19 channels)
        - Tracks current DF and EF for each channel
        - Interprets command-specific data
    """
```

**Logical Channel Management**:
```python
# Channel state structure
log_ch = [
    ['', ''],           # Channel 0: [current_DF, current_EF]
    ['', ''],           # Channel 1
    # ... up to channel 19
]

# Extended channels (4-19) detected from CLA byte:
# CLA bits [7:6] = '01' or '11' → extended channel
# Channel ID = 4 + int(CLA[4:8], 2)
```

**Command-Specific Processing**:

1. **SELECT Command**:
   - Updates current DF/EF in logical channel
   - Handles AID selection (A0...)
   - Handles hierarchical paths (7F10, 7FFF, etc.)
   - Distinguishes USIM vs ISIM ADF

2. **AUTHENTICATE Command**:
   - Parses RAND (16 bytes)
   - Parses AUTN (16 bytes)
   - Parses RES (8 bytes) or AUTS (14 bytes)
   - Detects Re-Sync (response type 'DC')

3. **FETCH Command**:
   - Extracts proactive command type from tag '810301'
   - Parses REFRESH sub-type
   - Parses POLL INTERVAL duration
   - Parses SETUP EVENT LIST events

4. **ENVELOPE Command**:
   - Extracts envelope type from first byte
   - Parses Event Download events

5. **TERMINAL RESPONSE Command**:
   - Extracts proactive command type
   - Parses result code
   - Detects error results

6. **MANAGE CHANNEL Command**:
   - Detects OPEN (P2=00) or CLOSE (P2=80)
   - Extracts channel number

7. **Short File ID (SFI) Commands**:
   - Extracts SFI from P1 or P2 byte
   - Maps SFI to file ID using current DF
   - Updates current EF


### 6. File System Analyzer Component (msg_files.py)

**Responsibility**: READ 명령어로 읽은 파일 목록 생성 및 OTA 업데이트 감지

**Key Functions**:
- `process()`: 파일 시스템 DataFrame 생성

**Interface**:
```python
def process(sum_rst: List[str], sum_read: List, 
            sum_log_ch: List[List[str]]) -> pd.DataFrame:
    """
    Generate file system view from READ commands
    
    Args:
        sum_rst: Summary strings
        sum_read: Read command data
        sum_log_ch: Logical channel states
    
    Returns:
        DataFrame with columns:
        - DF: DF name
        - File: EF name
        - DF_Id: DF identifier
        - File_Id: EF identifier
        - Type: TF (Transparent) or LF (Linear Fixed)
        - SFI: Short File ID (if used)
        - REC#: Record number (for LF files)
        - OFS: Offset (for TF files)
        - LEN: Length
        - ref: Reference to summary line
        - OTA_updated: 1 if file contents changed
        - contents: File data in hex
        - parsing: Parsed human-readable content
    
    Notes:
        - Filters out failed READ commands
        - Detects OTA updates by comparing contents
        - Sorts by DF, File_Id, REC#
    """
```

**Processing Steps**:
1. Filter READ BINARY and READ RECORD commands
2. Extract file metadata (DF, EF, offset, length, record number)
3. Map DF_Id and File_Id to names using file_system.py
4. Detect OTA updates (same file read multiple times with different contents)
5. Remove duplicate entries
6. Sort by DF hierarchy (MF first, then USIM, then ISIM, then Unknown)

### 7. Detail View Component (msg_app.py)

**Responsibility**: 특정 APDU 트랜잭션의 상세 정보 포맷팅

**Key Functions**:
- `rst()`: 트랜잭션 상세 정보 생성
- `split_contents()`: 파일 내용을 읽기 쉽게 포맷팅
- `split_parsing()`: 파싱 결과를 여러 줄로 포맷팅

**Interface**:
```python
def rst(input: Tuple, read: List, error: List, 
        item_num: int) -> List[str]:
    """
    Generate detailed view for specific transaction
    
    Args:
        input: (prot_type, sum_cmd, sum_log_ch, sum_log_ch_id)
        read: Read command data
        error: Error messages
        item_num: Transaction index
    
    Returns:
        List of formatted strings showing:
        - Logical channel number
        - Current DF file with name
        - Current EF file with name
        - Current command
        - Command-specific details (offset, length, contents, parsing)
        - Error messages
    """
```


### 8. Reference Data Modules

#### file_system.py

**Responsibility**: DF/EF 정의 및 파일 이름 매핑

**Data Structures**:
```python
DF_name: Dict[str, str] = {
    '3F00': 'MF',
    '7F10': 'DF TELECOM',
    'A0000000871002': 'ADF USIM',
    'A0000000871004': 'ADF ISIM',
    '7FFF5FC0': 'DF 5GS',
    # ... 30+ DF definitions
}

EF_name: Dict[str, Dict[str, str]] = {
    '3F00': {
        '2FE2': 'ICCID',
        '2F05': 'PL',
        # ... MF children
    },
    'A0000000871002': {
        '6F07': 'IMSI',
        '6F38': 'UST',
        '6FE3': 'EPSLOCI',
        # ... 100+ USIM EF definitions
    },
    # ... other DFs
}
```

**Key Functions**:
```python
def process(current_DF: str, current_EF: str, 
            file_id: str) -> Tuple[str, str]:
    """
    Map file IDs to names
    
    Args:
        current_DF: Current DF identifier
        current_EF: Current EF identifier
        file_id: File ID being accessed
    
    Returns:
        file_name: Human-readable file name
        error: Error message if file not found
    """
```

#### command.py

**Responsibility**: INS 코드 매핑

**Data Structure**:
```python
cmd_name: Dict[str, str] = {
    'A4': 'SELECT',
    'B0': 'READ BINARY',
    'B2': 'READ RECORD',
    'D6': 'UPDATE BINARY',
    '88': 'AUTHENTICATE',
    '12': 'FETCH',
    'C2': 'ENVELOPE',
    '14': 'TERMINAL RESPONSE',
    '70': 'MANAGE CHANNEL',
    # ... 30+ command definitions
}
```

#### spec_ref.py

**Responsibility**: 3GPP/ETSI 스펙 참조 데이터

**Data Structures**:
```python
UST_type: Dict[int, str]           # USIM Service Table (146 services)
IST_type: Dict[int, str]           # ISIM Service Table (21 services)
Proactive_type: Dict[str, str]     # Proactive command types
REFRESH_type: Dict[str, str]       # REFRESH sub-types
Event_list: Dict[str, str]         # Event Download types
Envelope_type: Dict[str, str]      # Envelope types
TR_RST_list: Dict[str, str]        # Terminal Response result codes
RAPDU_list: Dict[str, str]         # Common error Status Words
Error_RAPDU_list: Dict[str, str]   # Error Status Words
```


#### SELECT.py

**Responsibility**: SELECT 명령어 처리 및 파일 시스템 컨텍스트 업데이트

**Key Functions**:
```python
def process(data: List[str], log_ch: List[List[str]], 
            log_ch_id: int) -> Tuple[List[List[str]], str, str]:
    """
    Process SELECT command and update file context
    
    Args:
        data: APDU data [TX, optional RX, file_id, RX with SW]
        log_ch: Logical channel states
        log_ch_id: Current logical channel ID
    
    Returns:
        log_ch: Updated logical channel states
        file_name: Selected file name
        error: Error message if any
    
    Logic:
        - AID (A0...): Update DF, clear EF
        - MF/DF (3F00, 7F10, etc.): Update DF, clear EF
        - EF (4 hex digits): Update EF, keep DF
        - 7FFF: Select ADF (USIM or ISIM based on context)
        - Hierarchical paths: Parse and update accordingly
    """
```

#### READ.py

**Responsibility**: 파일 내용 파싱

**Key Functions**:
```python
def process(ins: str, file_name: str, data: List[str], 
            sum_read: List) -> List:
    """
    Process READ command and parse file contents
    
    Args:
        ins: Instruction code ('B0' or 'B2')
        file_name: File being read
        data: APDU data
        sum_read: Accumulated read data
    
    Returns:
        Updated sum_read with file data and parsing
    """

def parser(file_name: str, data: str, offset: str) -> str:
    """
    Parse file contents based on file type
    
    Supported files:
        - ICCID: BCD decoding
        - IMSI: BCD decoding
        - IMPI, IMPU, P-CSCF: UTF-8 decoding
        - ACC: Binary representation
        - HPLMNwAcT, OPLMNwAcT, PLMNwAcT: PLMN + Access Technology
        - FPLMN: Forbidden PLMN list
        - MSISDN: Alpha ID + dialing number
        - UST: Service table with 146 services
        - IST: ISIM service table with 21 services
        - EPSLOCI: GUTI + TAI + EPS update status
    
    Returns:
        Parsed human-readable string
    """
```

#### short_file_id.py

**Responsibility**: Short File ID 처리

**Data Structure**:
```python
cmd_SFI_list = ['B0', 'D6', 'B2', 'DC', 'A2', '32', 'CB', 'DB']

SFI_file_id: Dict[str, Dict[str, str]] = {
    '3F00': {'02': '2FE2', '05': '2F05', ...},
    'A0000000871002': {'01': '6FB7', '07': '6F07', ...},
    # ... SFI mappings for each DF
}
```

**Key Functions**:
```python
def category(prot_data: str) -> Tuple[bool, str]:
    """
    Determine if command uses SFI and extract SFI value
    
    Args:
        prot_data: APDU command data
    
    Returns:
        SFI_used: True if SFI is used
        SFI: SFI value in hex
    
    Logic:
        - READ/UPDATE BINARY: Check P1 bit 7
        - READ/UPDATE/SEARCH RECORD: Check P2 bits 7-3
        - RETRIEVE/SET DATA: Check P2 bits 7-3
    """

def process(log_ch: List[List[str]], log_ch_id: int, 
            SFI: str) -> Tuple[List[List[str]], str, str]:
    """
    Map SFI to file ID and update logical channel
    
    Args:
        log_ch: Logical channel states
        log_ch_id: Current channel ID
        SFI: Short File ID
    
    Returns:
        log_ch: Updated channel states
        file_name: Mapped file name
        error: Error message if SFI unknown
    """
```


## Data Models

### Message Data Model

```python
# Raw message from parser
Message = {
    'start': int,        # Start line index in log file
    'end': int,          # End line index in log file
    'SN': int,           # Sequence number
    'port': int,         # SIM port (1 or 2)
    'type': str,         # 'TX', 'RX', 'ATR', 'PPS', 'RESET'
    'data': str          # APDU data in hex (no spaces)
}
```

### Protocol Transaction Model

```python
# Protocol-level transaction
Transaction = {
    'start': List[int],  # Start indices for each message in transaction
    'end': List[int],    # End indices
    'type': List[str],   # Message types
    'data': List[str],   # APDU data
    'case': str          # 'Case1', 'Case2', 'Case3', 'Case4', or error
}
```

### Application Command Model

```python
# Application-level command
Command = {
    'summary': str,           # Formatted summary line
    'log_ch': List[str],      # [current_DF, current_EF]
    'log_ch_id': int,         # Logical channel ID (0-19)
    'cmd': str,               # Command name
    'read': List,             # Read/Auth data (varies by command)
    'error': str              # Error message if any
}
```

### File System Entry Model

```python
# File system entry
FileEntry = {
    'DF': str,           # DF name (e.g., 'ADF USIM')
    'File': str,         # EF name (e.g., 'IMSI')
    'DF_Id': str,        # DF identifier (e.g., 'A0000000871002')
    'File_Id': str,      # EF identifier (e.g., '6F07')
    'Type': str,         # 'TF' or 'LF'
    'SFI': str,          # Short File ID or '-'
    'REC#': str,         # Record number or '-'
    'OFS': str,          # Offset (hex) or '-'
    'LEN': str,          # Length (hex)
    'ref': str,          # Reference to summary line (e.g., '[123]')
    'OTA_updated': int,  # 1 if contents changed, 0 otherwise
    'contents': str,     # File data in hex
    'parsing': str       # Parsed human-readable content
}
```

### Logical Channel State Model

```python
# Logical channel state
ChannelState = {
    'DF': str,           # Current DF identifier
    'EF': str,           # Current EF identifier
    'ADF': str           # Original ADF (for 7FFF selection)
}

# System maintains 20 channels (0-19)
LogicalChannels = List[ChannelState]  # Length 20
```

