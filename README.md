# Binance Discord Market & Search Bot (바이낸스 시세검색 디스코드 봇)

Binance REST API 기반 토큰화 주식 및 암호화폐 실시간 시세 검색 디스코드 봇입니다.

## 주요 기능

- **/시세검색 (검색어)** 또는 **/search (query)**:
  - 한글 종목명 (`SK하이닉스`, `테슬라`, `엔비디아`, `애플`, `마이크로소프트`, `비트코인`, `이더리움`, `리플` 등) 검색 지원
  - 영문 티커 및 심볼 (`SKHY`, `TSLA`, `NVDA`, `BTC`, `ETH`, `SKHYBUSDT`) 검색 지원
  - **단일 결과**: 실시간 현재가, 24시간 변동률, 고가, 저가, 거래량 및 KST 갱신시간 카드 형태로 표시
  - **다중 결과 (2개 이상 매칭 시)**: 검색어에 부합하는 모든 종목들의 실시간 시세 요약 목록을 한눈에 출력 (예: `SK` 검색 시 `SK하이닉스`, `SKL` 등 동시 출력)
- **/market**: 터미널 메뉴 UI를 통한 수동 시장 카테고리 선택 및 시세 조회

## 설치 및 실행 방법

1. **가상환경 생성 및 패키지 설치**
   ```bash
   uv venv venv
   uv pip install -r requirements.txt
   ```
   또는 standard pip:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **환경변수 설정 (`.env`)**
   - `.env.example` 파일을 복사하여 `.env` 생성:
     ```bash
     cp .env.example .env  # Windows: copy .env.example .env
     ```
   - `.env` 파일에 발급받은 Discord Bot Token을 입력합니다:
     ```env
     DISCORD_TOKEN=your_discord_bot_token_here
     ```
   *(공개 시세 API를 사용하므로 Binance API Key는 필수가 아니며 생략 가능합니다.)*

3. **검증 테스트 실행**
   ```bash
   python test_binance.py
   python test_commands.py
   ```

4. **봇 실행**
   ```bash
   python -m bot.main
   ```

## 사용법 예시

디스코드 채팅창에서 슬래시 명령어 입력:

```text
/시세검색 검색어:SK하이닉스
/시세검색 검색어:테슬라
/시세검색 검색어:SK
/search query:BTC
/market
```

## 라이선스

MIT License