# 요구사항 문서

## 소개

SIM APDU Analyzer는 실제 단말기에서 수집된 SIM/eSIM APDU 로그를 분석하는 웹 기반 도구입니다. 
모뎀과 SIM 카드 간의 통신을 프로토콜 레벨, 애플리케이션 레벨, 파일 시스템 레벨의 3단계로 분석하여 
SIM 카드 동작을 상세히 파악할 수 있습니다.

## 용어 정의

- **System**: SIM APDU Analyzer 웹 애플리케이션
- **User**: LG U+ 엔지니어 또는 기술 담당자
- **APDU**: Application Protocol Data Unit (SIM 카드와 모뎀 간 통신 단위)
- **TX**: Transmit (모뎀에서 SIM으로 전송되는 명령)
- **RX**: Receive (SIM에서 모뎀으로 전송되는 응답)
- **QXDM**: Qualcomm eXtensible Diagnostic Monitor (Qualcomm 모뎀 진단 도구)
- **QCAT**: Qualcomm QXDM Configuration and Analysis Tool
- **Shannon_DM**: Samsung Shannon 모뎀 진단 도구
- **DF**: Dedicated File (SIM 파일 시스템의 디렉토리)
- **EF**: Elementary File (SIM 파일 시스템의 파일)
- **SFI**: Short File Identifier (파일 단축 식별자)
- **Logical_Channel**: SIM 카드와의 논리적 통신 채널 (0-19)
- **DSDS**: Dual SIM Dual Standby (듀얼 SIM 지원)
- **OTA**: Over-The-Air (무선 업데이트)
- **Status_Word**: APDU 응답의 상태 코드 (SW1, SW2)
- **AKA**: Authentication and Key Agreement (인증 프로토콜)

## 요구사항

### 요구사항 1: 로그 파일 업로드 및 포맷 감지

**사용자 스토리:** 엔지니어로서, 다양한 진단 도구에서 생성된 로그 파일을 업로드하면 자동으로 포맷을 감지하여 분석할 수 있기를 원합니다.

#### 인수 기준

1. WHEN User가 .txt 확장자의 로그 파일을 업로드하면, THE System SHALL 파일을 수신하고 저장한다
2. WHEN 로그 파일의 첫 번째 라인에 '[0x19B7]'이 포함되면, THE System SHALL QXDM 포맷으로 감지한다
3. WHEN 로그 파일의 첫 두 라인에 'USIM_MAIN'이 포함되면, THE System SHALL Shannon DM 포맷으로 감지한다
4. WHEN 로그 파일이 위 조건에 해당하지 않으면, THE System SHALL QCAT 포맷으로 감지한다
5. THE System SHALL 감지된 포맷에 맞는 파서를 사용하여 APDU 메시지를 추출한다


### 요구사항 2: SIM 포트 선택 및 필터링

**사용자 스토리:** 엔지니어로서, 듀얼 SIM 단말기의 로그에서 SIM1 또는 SIM2의 메시지만 선택적으로 분석할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL SIM1과 SIM2 선택 옵션을 제공한다
2. WHEN User가 SIM 포트를 선택하면, THE System SHALL 해당 포트의 메시지만 필터링한다
3. WHEN User가 SIM 포트를 변경하면, THE System SHALL 기존 로그 파일을 재분석하여 새로운 포트의 결과를 표시한다
4. THE System SHALL 선택된 SIM 포트 정보를 세션에 저장한다

### 요구사항 3: APDU 메시지 파싱

**사용자 스토리:** 엔지니어로서, 로그 파일에서 APDU 메시지의 타임스탬프, 방향(TX/RX), 데이터를 정확히 추출할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL 각 APDU 메시지에서 타임스탬프를 추출한다
2. THE System SHALL 각 APDU 메시지의 방향(TX, RX, ATR_TX, ATR_RX, PPS_TX, PPS_RX, RESET)을 식별한다
3. THE System SHALL 각 APDU 메시지의 16진수 데이터를 추출한다
4. WHEN APDU 데이터가 여러 라인에 걸쳐 있으면, THE System SHALL 데이터를 연결하여 완전한 메시지를 구성한다
5. THE System SHALL 중복된 메시지를 제거한다

### 요구사항 4: 프로토콜 레벨 분석

**사용자 스토리:** 엔지니어로서, APDU 명령과 응답을 매칭하고 APDU Case를 분류하여 프로토콜 레벨에서 통신을 이해할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL TX와 RX 메시지를 페어링하여 완전한 APDU 트랜잭션을 구성한다
2. THE System SHALL APDU를 Case 1, Case 2, Case 3, Case 4로 분류한다
3. WHEN 연속된 TX 또는 RX가 발생하면, THE System SHALL 프로토콜 오류로 표시한다
4. WHEN TX 데이터 길이가 P3 파라미터와 일치하지 않으면, THE System SHALL 오류로 표시한다
5. WHEN Status Word가 수신되지 않으면, THE System SHALL 오류로 표시한다
6. THE System SHALL APDU 트랜잭션 중 POWER_OFF 이벤트를 감지한다


### 요구사항 5: 명령어 해석 및 파일 추적

**사용자 스토리:** 엔지니어로서, APDU 명령어를 사람이 읽을 수 있는 형태로 해석하고 현재 선택된 파일을 추적할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL INS 바이트를 명령어 이름으로 변환한다 (SELECT, READ BINARY, UPDATE BINARY, AUTHENTICATE 등)
2. WHEN INS 바이트가 알려지지 않은 값이면, THE System SHALL "INS: 0xXX" 형식으로 표시한다
3. THE System SHALL CLA 바이트에서 논리 채널 번호(0-19)를 추출한다
4. THE System SHALL 각 논리 채널별로 현재 DF와 EF를 추적한다
5. WHEN SELECT 명령이 실행되면, THE System SHALL 현재 DF 또는 EF를 업데이트한다
6. THE System SHALL 3GPP 표준에 정의된 파일 ID를 파일 이름으로 변환한다
7. WHEN 파일 ID가 알려지지 않으면, THE System SHALL "Unknown EF" 또는 "Unknown DF"로 표시한다

### 요구사항 6: Status Word 분석 및 오류 감지

**사용자 스토리:** 엔지니어로서, APDU 응답의 Status Word를 분석하여 성공/실패 여부와 오류 원인을 파악할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL Status Word(SW1, SW2)를 추출한다
2. WHEN Status Word가 '9000' 또는 '91XX'이면, THE System SHALL 성공으로 처리한다
3. WHEN Status Word가 '6A82'(File not found), '6A83'(Record not found), '6282'(Unsuccessful search), '6982'(Security status not satisfied)이면, THE System SHALL 명령어에 '(X)' 표시를 추가한다
4. WHEN Status Word가 오류 코드이면, THE System SHALL ETSI TS 102.221 표준에 따라 오류 메시지를 표시한다
5. THE System SHALL 각 오류에 대해 3GPP 규격 참조 정보를 제공한다

### 요구사항 7: Short File Identifier (SFI) 처리

**사용자 스토리:** 엔지니어로서, SFI를 사용하는 READ/UPDATE 명령에서 대상 파일을 자동으로 식별할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL READ BINARY, READ RECORD, UPDATE BINARY, UPDATE RECORD 명령에서 SFI 사용 여부를 감지한다
2. WHEN SFI가 사용되면, THE System SHALL P1 바이트에서 SFI 값을 추출한다
3. THE System SHALL SFI를 파일 ID로 변환하여 파일 이름을 표시한다
4. THE System SHALL 명령어에 "(SFI: 0xXX)" 표시를 추가한다


### 요구사항 8: 인증 프로토콜 분석

**사용자 스토리:** 엔지니어로서, AKA 인증 과정의 RAND, AUTN, RES, AUTS 값을 추출하고 Re-Sync 이벤트를 감지할 수 있기를 원합니다.

#### 인수 기준

1. WHEN AUTHENTICATE 명령(INS: 0x88 또는 0x89)이 실행되면, THE System SHALL RAND와 AUTN 값을 추출한다
2. WHEN 인증 응답이 성공(0xDB 태그)이면, THE System SHALL RES 값을 추출한다
3. WHEN 인증 응답이 Re-Sync(0xDC 태그)이면, THE System SHALL AUTS 값을 추출하고 "Re-Sync"으로 표시한다
4. THE System SHALL 인증 명령에서 사용된 ADF(USIM 또는 ISIM)를 표시한다
5. THE System SHALL 인증 정보를 Application-Level Analysis에 표시한다

### 요구사항 9: Proactive SIM 명령 처리

**사용자 스토리:** 엔지니어로서, FETCH, TERMINAL RESPONSE, ENVELOPE 등 Proactive SIM 명령을 해석할 수 있기를 원합니다.

#### 인수 기준

1. WHEN FETCH 명령이 실행되면, THE System SHALL Proactive 명령 타입(REFRESH, POLL INTERVAL, SETUP EVENT LIST 등)을 추출한다
2. WHEN REFRESH 명령이면, THE System SHALL REFRESH 타입(NAA, FCN, UICC Reset, SoR 등)을 표시한다
3. WHEN SETUP EVENT LIST 명령이면, THE System SHALL 이벤트 목록(MT call, Call connected, Location status 등)을 표시한다
4. WHEN TERMINAL RESPONSE 명령이 실행되면, THE System SHALL 결과 코드를 분석하고 오류 시 오류 메시지를 표시한다
5. WHEN ENVELOPE 명령이 실행되면, THE System SHALL Envelope 타입(Event Download, SMS-PP Download 등)을 표시한다

### 요구사항 10: 논리 채널 관리

**사용자 스토리:** 엔지니어로서, MANAGE CHANNEL 명령을 통한 논리 채널 개설/종료를 추적할 수 있기를 원합니다.

#### 인수 기준

1. WHEN MANAGE CHANNEL OPEN 명령이 실행되면, THE System SHALL 개설된 논리 채널 번호를 표시한다
2. WHEN MANAGE CHANNEL CLOSE 명령이 실행되면, THE System SHALL 종료된 논리 채널 번호를 표시한다
3. THE System SHALL 기본 채널(0-3)과 확장 채널(4-19)을 구분한다
4. THE System SHALL 각 논리 채널별로 독립적인 DF/EF 컨텍스트를 유지한다


### 요구사항 11: 파일 시스템 추적 및 내용 저장

**사용자 스토리:** 엔지니어로서, READ/UPDATE 명령을 통해 접근된 모든 파일의 내용과 메타데이터를 추적할 수 있기를 원합니다.

#### 인수 기준

1. WHEN READ BINARY 명령이 성공하면, THE System SHALL 파일 이름, 오프셋, 길이, 내용을 저장한다
2. WHEN READ RECORD 명령이 성공하면, THE System SHALL 파일 이름, 레코드 번호, 길이, 내용을 저장한다
3. WHEN UPDATE BINARY 명령이 실행되면, THE System SHALL 업데이트된 오프셋, 길이, 내용을 저장한다
4. THE System SHALL 파일 타입(TF: Transparent File, LF: Linear Fixed File)을 식별한다
5. THE System SHALL DF 이름, EF 이름, DF ID, File ID, SFI, 참조 메시지 번호를 함께 저장한다
6. THE System SHALL 동일한 파일에 대해 내용이 변경되면 OTA 업데이트로 표시한다

### 요구사항 12: 파일 내용 파싱

**사용자 스토리:** 엔지니어로서, 주요 SIM 파일의 내용을 사람이 읽을 수 있는 형태로 파싱하여 볼 수 있기를 원합니다.

#### 인수 기준

1. WHEN ICCID 파일을 읽으면, THE System SHALL BCD 형식을 디코딩하여 표시한다
2. WHEN IMSI 파일을 읽으면, THE System SHALL BCD 형식을 디코딩하여 표시한다
3. WHEN MSISDN 파일을 읽으면, THE System SHALL Alpha ID와 전화번호를 파싱하여 표시한다
4. WHEN PLMNwAcT, OPLMNwAcT, HPLMNwAcT 파일을 읽으면, THE System SHALL MCC, MNC, Access Technology를 파싱하여 표시한다
5. WHEN FPLMN 파일을 읽으면, THE System SHALL 금지된 PLMN 목록을 파싱하여 표시한다
6. WHEN UST(USIM Service Table) 파일을 읽으면, THE System SHALL 각 서비스의 활성화 여부를 표시한다
7. WHEN IST(ISIM Service Table) 파일을 읽으면, THE System SHALL 각 서비스의 활성화 여부를 표시한다
8. WHEN ACC(Access Control Class) 파일을 읽으면, THE System SHALL 16진수와 2진수 형식으로 표시한다
9. WHEN EPSLOCI 파일을 읽으면, THE System SHALL GUTI, TAI, EPS update status를 파싱하여 표시한다
10. WHEN IMPI, IMPU, P-CSCF 파일을 읽으면, THE System SHALL UTF-8 문자열로 디코딩하여 표시한다


### 요구사항 13: 웹 UI - Summary 뷰

**사용자 스토리:** 엔지니어로서, 분석된 APDU 메시지를 시간순으로 요약하여 보고 중요한 이벤트를 색상으로 구분할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL 각 APDU 트랜잭션을 한 줄로 요약하여 표시한다
2. THE System SHALL 메시지 번호, 타임스탬프, 명령어 이름, 파일 이름, 추가 정보를 표시한다
3. WHEN 메시지에 'ERROR'가 포함되면, THE System SHALL 빨간색으로 표시한다
4. WHEN 메시지에 'Re-Sync'가 포함되면, THE System SHALL 자홍색(magenta)으로 표시한다
5. WHEN 메시지에 '(X)', '(*)', 'Unknown'이 포함되면, THE System SHALL 회색으로 표시한다
6. WHEN 메시지에 'ENVELOPE' 또는 'REFRESH'가 포함되면, THE System SHALL 노란색으로 표시한다
7. WHEN 메시지에 'RESET' 또는 'POWER'가 포함되면, THE System SHALL 청록색(cyan)으로 표시한다
8. WHEN 메시지에 'MANAGE CHANNEL'이 포함되면, THE System SHALL 연한 파란색(lightblue)으로 표시한다
9. WHEN 메시지에 'AUTHENTICATE'가 포함되면, THE System SHALL 연한 초록색(lightgreen)으로 표시한다

### 요구사항 14: 웹 UI - 상세 분석 뷰

**사용자 스토리:** 엔지니어로서, Summary에서 메시지를 클릭하면 프로토콜 레벨과 애플리케이션 레벨의 상세 분석을 볼 수 있기를 원합니다.

#### 인수 기준

1. WHEN User가 Summary에서 메시지를 클릭하면, THE System SHALL 해당 메시지의 상세 분석을 표시한다
2. THE System SHALL Protocol-Level Analysis 영역에 TX/RX 메시지의 16진수 데이터를 표시한다
3. THE System SHALL Application-Level Analysis 영역에 논리 채널, 현재 DF, 현재 EF, 명령어를 표시한다
4. WHEN READ 또는 UPDATE 명령이면, THE System SHALL 오프셋/레코드 번호, 길이, 내용을 표시한다
5. WHEN AUTHENTICATE 명령이면, THE System SHALL RAND, AUTN, RES, AUTS 값을 표시한다
6. WHEN 파싱된 데이터가 있으면, THE System SHALL 파싱 결과를 함께 표시한다
7. WHEN 오류가 있으면, THE System SHALL 오류 메시지와 규격 참조를 표시한다


### 요구사항 15: 웹 UI - File System 뷰

**사용자 스토리:** 엔지니어로서, 접근된 모든 파일을 테이블 형태로 보고 OTA 업데이트된 파일을 강조 표시할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL File System 탭을 제공한다
2. THE System SHALL 파일 목록을 테이블로 표시한다 (DF, File, DF_Id, File_Id, Type, SFI, REC#, OFS, LEN, ref)
3. THE System SHALL 파일을 DF 순서로 정렬한다 (MF → USIM → ISIM → Unknown)
4. THE System SHALL 동일 DF 내에서 File_Id와 REC# 순으로 정렬한다
5. WHEN 파일이 OTA 업데이트되고 중요 파일(IMSI, MSISDN, OPLMNwAcT, ACC, Routing_Ind, IMPI, IMPU)이면, THE System SHALL 노란색으로 강조 표시한다
6. WHEN 파일이 OTA 업데이트되고 일반 파일이면, THE System SHALL 연한 초록색으로 강조 표시한다
7. WHEN User가 파일 행을 클릭하면, THE System SHALL 파일 내용과 파싱 결과를 표시한다

### 요구사항 16: Excel 내보내기

**사용자 스토리:** 엔지니어로서, 파일 시스템 분석 결과를 Excel 파일로 다운로드하여 추가 분석이나 보고서 작성에 활용할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL File System 탭에 "Save to Excel" 버튼을 제공한다
2. WHEN User가 버튼을 클릭하면, THE System SHALL 파일 시스템 데이터를 Excel 형식(.xlsx)으로 변환한다
3. THE System SHALL 모든 컬럼(DF, File, DF_Id, File_Id, Type, SFI, REC, OFS, LEN, ref, contents, parsing)을 포함한다
4. THE System SHALL Excel에서 허용되지 않는 제어 문자를 제거한다
5. THE System SHALL 파일 이름 "file_system_export.xlsx"로 다운로드를 제공한다

### 요구사항 17: 세션 관리

**사용자 스토리:** 엔지니어로서, 분석 결과가 세션에 저장되어 SIM 포트를 변경하거나 상세 분석을 볼 때 재분석 없이 빠르게 결과를 확인할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL 파일 시스템 기반 세션을 사용한다
2. WHEN User가 페이지에 처음 접속하면, THE System SHALL 기존 세션을 초기화한다
3. THE System SHALL 업로드된 파일 경로와 이름을 세션에 저장한다
4. THE System SHALL 파싱된 APDU 메시지 데이터를 세션에 저장한다
5. THE System SHALL 프로토콜 분석 결과를 세션에 저장한다
6. THE System SHALL 애플리케이션 분석 결과를 세션에 저장한다
7. THE System SHALL 파일 시스템 데이터를 세션에 저장한다
8. THE System SHALL 선택된 SIM 포트를 세션에 저장한다


### 요구사항 18: 3GPP 표준 준수

**사용자 스토리:** 엔지니어로서, 시스템이 3GPP 및 ETSI 표준에 정의된 파일 구조와 명령어를 정확히 해석할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL 3GPP TS 31.102(USIM Application)에 정의된 파일 구조를 지원한다
2. THE System SHALL 3GPP TS 31.103(ISIM Application)에 정의된 파일 구조를 지원한다
3. THE System SHALL ETSI TS 102.221(UICC-Terminal Interface)에 정의된 명령어를 지원한다
4. THE System SHALL ETSI TS 102.223(Card Application Toolkit)에 정의된 Proactive 명령을 지원한다
5. THE System SHALL GSMA SGP.02(eSIM Remote Provisioning)에 정의된 ISD-R, ISD-P, ECASD 파일을 지원한다
6. THE System SHALL Android UICC Carrier Privilege에 정의된 ARA-M, ARA-D 파일을 지원한다

### 요구사항 19: 오류 처리 및 복원력

**사용자 스토리:** 엔지니어로서, 불완전하거나 손상된 로그 파일에서도 가능한 한 많은 정보를 추출할 수 있기를 원합니다.

#### 인수 기준

1. WHEN 파일 업로드가 실패하면, THE System SHALL 사용자에게 오류 메시지를 표시한다
2. WHEN APDU 메시지가 불완전하면, THE System SHALL 해당 메시지를 건너뛰고 다음 메시지를 처리한다
3. WHEN 파일 시스템 데이터 생성 중 오류가 발생하면, THE System SHALL 오류를 무시하고 Summary 뷰만 제공한다
4. WHEN 알 수 없는 파일 ID가 발견되면, THE System SHALL "Unknown EF" 또는 "Unknown DF"로 표시하고 계속 진행한다
5. WHEN Excel 내보내기 중 오류가 발생하면, THE System SHALL 400 오류 코드와 메시지를 반환한다

### 요구사항 20: 성능 및 확장성

**사용자 스토리:** 엔지니어로서, 대용량 로그 파일(수천 개의 APDU 메시지)도 합리적인 시간 내에 분석할 수 있기를 원합니다.

#### 인수 기준

1. THE System SHALL 10,000개 이상의 APDU 메시지를 포함한 로그 파일을 처리한다
2. THE System SHALL 분석 결과를 메모리에 효율적으로 저장한다
3. THE System SHALL 웹 UI에서 대량의 메시지를 스크롤 가능한 테이블로 표시한다
4. THE System SHALL AJAX를 사용하여 상세 분석을 비동기적으로 로드한다
5. THE System SHALL 파일 시스템 데이터에서 중복 항목을 제거하여 메모리를 절약한다

