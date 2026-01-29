# 🐳 SIM APDU Analyzer - Docker 배포 가이드

이 문서는 SIM APDU Analyzer를 Docker 컨테이너로 실행하는 방법을 안내합니다.

---

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [빠른 시작](#빠른-시작)
3. [상세 설치 가이드](#상세-설치-가이드)
4. [사용 방법](#사용-방법)
5. [문제 해결](#문제-해결)
6. [고급 설정](#고급-설정)

---

## 🔧 사전 요구사항

### 필수 소프트웨어

#### Windows 사용자
1. **Docker Desktop for Windows**
   - 다운로드: https://www.docker.com/products/docker-desktop/
   - 최소 요구사항:
     - Windows 10 64-bit: Pro, Enterprise, Education (Build 19041 이상)
     - WSL 2 활성화 필요
   - 설치 후 재부팅 필요

2. **Git** (선택사항 - 소스 코드 다운로드용)
   - 다운로드: https://git-scm.com/download/win

#### macOS 사용자
1. **Docker Desktop for Mac**
   - 다운로드: https://www.docker.com/products/docker-desktop/
   - 최소 요구사항:
     - macOS 11 Big Sur 이상
     - Apple Silicon (M1/M2) 또는 Intel 프로세서

2. **Git** (선택사항)
   - 기본 설치되어 있음 (Terminal에서 `git --version` 확인)

### 시스템 요구사항
- **RAM**: 최소 4GB (권장 8GB 이상)
- **디스크 공간**: 최소 2GB
- **네트워크**: 인터넷 연결 (초기 이미지 빌드 시)

---

## 🚀 빠른 시작

### 1단계: Docker 설치 확인

터미널(Windows: PowerShell 또는 CMD, macOS: Terminal)을 열고 다음 명령어를 실행:

```bash
docker --version
docker-compose --version
```

정상적으로 버전이 표시되면 설치 완료입니다.

**예상 출력:**
```
Docker version 24.0.0, build abc1234
Docker Compose version v2.20.0
```

### 2단계: 프로젝트 파일 준비

#### 방법 A: Git으로 다운로드 (권장)
```bash
git clone <repository-url>
cd SIM-APDU-Analyzer
```

#### 방법 B: ZIP 파일 다운로드
1. 프로젝트 ZIP 파일 다운로드
2. 압축 해제
3. 터미널에서 해당 폴더로 이동
   ```bash
   cd /path/to/SIM-APDU-Analyzer
   ```

### 3단계: Docker 컨테이너 실행

프로젝트 폴더에서 다음 명령어 실행:

```bash
docker-compose up -d
```

**처음 실행 시**: 이미지 빌드에 5-10분 소요될 수 있습니다.

### 4단계: 웹 브라우저에서 접속

브라우저를 열고 다음 주소로 접속:

```
http://localhost:5000
```

✅ **성공!** SIM APDU Analyzer 웹 인터페이스가 표시됩니다.

---

## 📖 상세 설치 가이드

### Windows 상세 가이드

#### 1. Docker Desktop 설치

1. **다운로드 및 설치**
   - https://www.docker.com/products/docker-desktop/ 접속
   - "Download for Windows" 클릭
   - 다운로드한 `Docker Desktop Installer.exe` 실행
   - 설치 마법사 따라 진행
   - "Use WSL 2 instead of Hyper-V" 옵션 선택 (권장)

2. **WSL 2 설정** (필요 시)
   - PowerShell을 **관리자 권한**으로 실행
   - 다음 명령어 실행:
     ```powershell
     wsl --install
     ```
   - 컴퓨터 재부팅

3. **Docker Desktop 실행**
   - 시작 메뉴에서 "Docker Desktop" 실행
   - 초기 설정 완료 (약 2-3분 소요)
   - 트레이 아이콘에서 Docker가 실행 중인지 확인

#### 2. 프로젝트 실행

1. **PowerShell 또는 CMD 열기**
   - `Win + R` → `powershell` 입력 → Enter

2. **프로젝트 폴더로 이동**
   ```powershell
   cd C:\Users\YourName\Downloads\SIM-APDU-Analyzer
   ```

3. **Docker Compose 실행**
   ```powershell
   docker-compose up -d
   ```

4. **실행 확인**
   ```powershell
   docker ps
   ```
   
   **예상 출력:**
   ```
   CONTAINER ID   IMAGE                    STATUS         PORTS
   abc123def456   sim-apdu-analyzer:latest Up 2 minutes   0.0.0.0:5000->5000/tcp
   ```

5. **브라우저 접속**
   - Chrome, Edge, Firefox 등에서 `http://localhost:5000` 접속

### macOS 상세 가이드

#### 1. Docker Desktop 설치

1. **다운로드 및 설치**
   - https://www.docker.com/products/docker-desktop/ 접속
   - "Download for Mac" 클릭
   - Apple Silicon (M1/M2) 또는 Intel 버전 선택
   - 다운로드한 `Docker.dmg` 파일 실행
   - Docker 아이콘을 Applications 폴더로 드래그

2. **Docker Desktop 실행**
   - Applications 폴더에서 Docker 실행
   - 초기 설정 완료
   - 메뉴바에서 Docker 아이콘 확인

#### 2. 프로젝트 실행

1. **Terminal 열기**
   - `Cmd + Space` → "Terminal" 입력 → Enter

2. **프로젝트 폴더로 이동**
   ```bash
   cd ~/Downloads/SIM-APDU-Analyzer
   ```

3. **Docker Compose 실행**
   ```bash
   docker-compose up -d
   ```

4. **실행 확인**
   ```bash
   docker ps
   ```

5. **브라우저 접속**
   - Safari, Chrome 등에서 `http://localhost:5000` 접속

---

## 💡 사용 방법

### 기본 사용법

1. **로그 파일 업로드**
   - 웹 인터페이스에서 "📂 File" 버튼 클릭
   - `.txt` 형식의 APDU 로그 파일 선택
   - 지원 포맷: QXDM, QCAT, Shannon DM

2. **SIM 포트 선택**
   - 드롭다운에서 "SIM1" 또는 "SIM2" 선택

3. **분석 실행**
   - "Analyze" 버튼 클릭
   - 처리 완료까지 대기 (파일 크기에 따라 수초~수분)

4. **결과 확인**
   - **APDU 탭**: 명령어 목록 및 상세 분석
   - **File System 탭**: 파일 시스템 뷰 및 내용

5. **데이터 내보내기**
   - File System 탭에서 "💾 Save to Excel" 클릭

### Docker 컨테이너 관리

#### 컨테이너 상태 확인
```bash
docker ps
```

#### 로그 확인
```bash
docker logs sim-apdu-analyzer
```

실시간 로그 보기:
```bash
docker logs -f sim-apdu-analyzer
```

#### 컨테이너 중지
```bash
docker-compose down
```

#### 컨테이너 재시작
```bash
docker-compose restart
```

#### 컨테이너 완전 삭제 (데이터 포함)
```bash
docker-compose down -v
```

---

## 🔍 문제 해결

### 일반적인 문제

#### 1. "Docker daemon is not running" 오류

**증상:**
```
Cannot connect to the Docker daemon
```

**해결 방법:**
- **Windows**: Docker Desktop이 실행 중인지 확인 (트레이 아이콘)
- **macOS**: Docker Desktop이 실행 중인지 확인 (메뉴바 아이콘)
- Docker Desktop 재시작

#### 2. 포트 5000이 이미 사용 중

**증상:**
```
Error: bind: address already in use
```

**해결 방법 A: 다른 포트 사용**

`docker-compose.yml` 파일 수정:
```yaml
ports:
  - "5001:5000"  # 5000 → 5001로 변경
```

그 후 `http://localhost:5001`로 접속

**해결 방법 B: 기존 프로세스 종료**

Windows:
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID번호> /F
```

macOS:
```bash
lsof -ti:5000 | xargs kill -9
```

#### 3. 이미지 빌드 실패

**증상:**
```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
```

**해결 방법:**
1. 인터넷 연결 확인
2. Docker Desktop 재시작
3. 캐시 없이 재빌드:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

#### 4. 파일 업로드 실패

**증상:**
- 파일 선택 후 "Analyze" 버튼이 작동하지 않음
- 에러 메시지 표시

**해결 방법:**
1. 파일 크기 확인 (최대 200MB)
2. 파일 형식 확인 (`.txt` 파일)
3. 로그 포맷 확인 (QXDM, QCAT, Shannon DM)
4. 브라우저 콘솔 확인 (F12 → Console 탭)

#### 5. 메모리 부족 오류

**증상:**
```
Container killed due to memory limit
```

**해결 방법:**

Docker Desktop 설정에서 메모리 할당 증가:
- **Windows/macOS**: Docker Desktop → Settings → Resources → Memory
- 권장: 4GB 이상

#### 6. WSL 2 관련 오류 (Windows)

**증상:**
```
WSL 2 installation is incomplete
```

**해결 방법:**
1. PowerShell을 관리자 권한으로 실행
2. 다음 명령어 실행:
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```
3. 컴퓨터 재부팅

### 로그 확인 방법

#### 애플리케이션 로그
```bash
docker logs sim-apdu-analyzer --tail 100
```

#### 실시간 로그 모니터링
```bash
docker logs -f sim-apdu-analyzer
```

#### 컨테이너 내부 접속 (디버깅)
```bash
docker exec -it sim-apdu-analyzer /bin/bash
```

---

## ⚙️ 고급 설정

### 환경 변수 커스터마이징

`docker-compose.yml` 파일의 `environment` 섹션 수정:

```yaml
environment:
  - FLASK_ENV=production
  - SECRET_KEY=your-super-secret-key-here
  - MAX_CONTENT_LENGTH=314572800  # 300MB
  - LOG_LEVEL=INFO
```

### 영구 데이터 저장

기본적으로 업로드된 파일과 세션은 컨테이너 재시작 시 유지됩니다.

**볼륨 위치:**
- 업로드 파일: `./uploads`
- 세션 데이터: `./flask_session`

**볼륨 삭제 (초기화):**
```bash
docker-compose down -v
rm -rf uploads/* flask_session/*
```

### 프로덕션 배포

#### HTTPS 설정 (Nginx 리버스 프록시)

`docker-compose.yml`에 Nginx 추가:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - sim-apdu-analyzer
    networks:
      - sim-analyzer-network

  sim-apdu-analyzer:
    # ... 기존 설정 ...
    ports: []  # 외부 포트 노출 제거
```

#### 성능 튜닝

`Dockerfile`의 Gunicorn 설정 수정:

```dockerfile
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \          # CPU 코어 수에 맞게 조정
     "--threads", "8", \          # 동시 요청 처리 수
     "--timeout", "300", \        # 대용량 파일 처리 시간
     "--max-requests", "1000", \  # 메모리 누수 방지
     "--max-requests-jitter", "100", \
     "main_web:app"]
```

### 네트워크 설정

#### 특정 IP에서만 접속 허용

`docker-compose.yml` 수정:

```yaml
ports:
  - "127.0.0.1:5000:5000"  # localhost만 허용
```

#### 다른 컴퓨터에서 접속 허용

```yaml
ports:
  - "0.0.0.0:5000:5000"  # 모든 IP 허용
```

방화벽 설정:
- **Windows**: Windows Defender 방화벽에서 포트 5000 허용
- **macOS**: 시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽

---

## 📊 성능 최적화

### 권장 설정

#### 소규모 팀 (1-5명)
```yaml
environment:
  - WORKERS=2
  - THREADS=4
  - TIMEOUT=120
resources:
  limits:
    memory: 2G
    cpus: '1.0'
```

#### 중규모 팀 (5-20명)
```yaml
environment:
  - WORKERS=4
  - THREADS=8
  - TIMEOUT=300
resources:
  limits:
    memory: 4G
    cpus: '2.0'
```

### 모니터링

#### 리소스 사용량 확인
```bash
docker stats sim-apdu-analyzer
```

#### 컨테이너 상태 확인
```bash
docker inspect sim-apdu-analyzer
```

---

## 🔐 보안 고려사항

### 1. Secret Key 변경

프로덕션 환경에서는 반드시 `SECRET_KEY` 변경:

```bash
# 랜덤 키 생성 (Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

생성된 키를 `docker-compose.yml`에 적용:

```yaml
environment:
  - SECRET_KEY=생성된_랜덤_키
```

### 2. 네트워크 격리

내부 네트워크에서만 사용:
- VPN 연결 필수
- 방화벽 규칙 설정
- 인증 프록시 사용

### 3. 데이터 보안

민감한 로그 파일 처리 시:
- 분석 완료 후 즉시 삭제
- 정기적인 볼륨 정리
- 백업 시 암호화

```bash
# 세션 및 업로드 파일 정리
docker exec sim-apdu-analyzer rm -rf /app/uploads/* /app/flask_session/*
```

---

## 🆘 지원 및 문의

### 문제 발생 시

1. **로그 수집**
   ```bash
   docker logs sim-apdu-analyzer > error.log
   ```

2. **시스템 정보 수집**
   ```bash
   docker version > system_info.txt
   docker-compose version >> system_info.txt
   docker ps -a >> system_info.txt
   ```

3. **담당자에게 전달**
   - 이메일: ajs3013@lguplus.co.kr
   - 첨부: `error.log`, `system_info.txt`, 문제 상황 스크린샷

### 추가 리소스

- **사용자 가이드**: [README.md](./README.md)
- **기술 스펙**: [SPECIFICATION.md](./SPECIFICATION.md)
- **샘플 로그**: [Google Drive](https://drive.google.com/drive/folders/1I1Bpgms0mXRy9NLk4kg_3K9BFDVbe9LD)

---

## 📝 체크리스트

배포 전 확인사항:

- [ ] Docker Desktop 설치 및 실행 확인
- [ ] 프로젝트 파일 다운로드 완료
- [ ] `docker-compose up -d` 실행 성공
- [ ] `http://localhost:5000` 접속 확인
- [ ] 샘플 로그 파일로 테스트 완료
- [ ] 팀원들에게 접속 URL 공유
- [ ] 문제 발생 시 연락처 공유

---

## 🎉 완료!

이제 SIM APDU Analyzer를 Docker로 실행할 수 있습니다.

**다음 단계:**
1. 샘플 로그 파일로 테스트
2. 실제 로그 파일 분석
3. 팀원들과 공유

**문의사항이 있으시면 언제든지 연락주세요!**

---

**작성자**: JUSEOK AHN (안주석)  
**이메일**: ajs3013@lguplus.co.kr  
**최종 업데이트**: 2025-01-28
