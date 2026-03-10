# LLM Proxy

멀티 벤더 LLM API를 단일 인터페이스로 통합하는 프록시 서버.
클라이언트는 벤더를 신경 쓰지 않고 동일한 API로 요청하며, 장애 시 자동 Fallback을 지원한다.


## Architecture

```
Request:  Client -> Backend API -> LLM Proxy -> Vendor API (OpenAI, Anthropic, Google, ...)
Response: Vendor API -> LLM Proxy -> Backend API -> Client
```

- 모든 Chat 응답은 **Streaming (SSE)** 으로 처리되며, chunk 단위로 지연 없이 파이프라인을 통과한다.
- 1차 벤더 실패 시 2차 벤더로 **자동 Fallback** 한다.


## Supported Vendors & Models

| Vendor | Client | 주요 모델 |
|--------|--------|-----------|
| OpenAI | `OpenAIClient` | gpt-4o, gpt-4.1, o3-mini, o4-mini |
| Azure OpenAI | `AzureClient` | gpt-4o, gpt-4.1, o3-mini |
| Anthropic | `AnthropicClient` | claude-sonnet-4-6, claude-opus-4-6 |
| AWS Bedrock | `BedrockClient` | anthropic.claude-sonnet-4-6 등 |
| Google | `GoogleClient` | gemini-2.5-flash, gemini-2.5-pro |
| xAI | `XClient` | grok-4-latest |
| 4grit (Self-hosted) | `FourgritClient` | vLLM 기반 자체 모델 |
| Local | `LocalClient` | 로컬 개발용 |


## Project Structure

```
llm-proxy/
├── main.py                  # FastAPI 엔트리포인트
├── api/
│   ├── llm.py               # /llm/chat, /llm/chat_mcp, /llm/embeddings 등
│   └── file.py              # /file/* (Google FileSearch store 관리)
├── client/
│   ├── common.py            # 공통 스트리밍, Fallback, 응답 직렬화 로직
│   ├── open_ai.py           # OpenAI API 클라이언트
│   ├── azure.py             # Azure OpenAI 클라이언트
│   ├── anthropic.py         # Anthropic API 클라이언트
│   ├── bedrock.py           # AWS Bedrock 클라이언트 + S3Client
│   ├── google.py            # Google GenAI 클라이언트 + FileSearch
│   ├── x.py                 # xAI (Grok) 클라이언트
│   ├── fourgrit.py          # 4grit 자체 호스팅 클라이언트
│   ├── local.py             # 로컬 개발용 클라이언트
│   └── fastmcp.py           # MCP (Model Context Protocol) 클라이언트
├── helper/
│   ├── llm.py               # 벤더 선택, safe_stream, 토큰 검증 등
│   └── file.py              # 파일 임포트 헬퍼
├── models/
│   ├── llm.py               # Pydantic 요청 모델 (ChatPayload 등)
│   └── file.py              # Pydantic 파일 관련 모델
├── utils/
│   ├── constants.py          # 벤더, 모델, 서비스 상수
│   ├── error.py              # 커스텀 에러 클래스
│   ├── response.py           # 응답 래퍼
│   ├── paths.py              # 경로 상수
│   └── vector.py             # 벡터 유틸
├── pyproject.toml             # 프로젝트 메타데이터 & 의존성 (uv)
├── uv.lock                   # 의존성 lock 파일
├── gunicorn.config.py        # Gunicorn 설정
└── Dockerfile                # Docker 이미지 빌드
```


## API Endpoints

### LLM

| Method | Path | 설명 |
|--------|------|------|
| POST | `/llm/chat` | LLM 채팅 (Streaming / Non-streaming) |
| POST | `/llm/chat_mcp` | MCP Tool Use 포함 채팅 (Streaming) |
| POST | `/llm/ocr_chat` | OCR + LLM 채팅 (Streaming) |
| POST | `/llm/embeddings` | 텍스트 임베딩 벡터 생성 |
| POST | `/llm/chat_on_queue` | 비동기 큐 기반 채팅 (Streaming) |

### File (Google FileSearch)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/file/create_store` | FileSearch Store 생성 |
| POST | `/file/get_stores` | Store 목록 조회 |
| POST | `/file/import_files` | S3 -> Google FileSearch 파일 업로드 |
| POST | `/file/get_files` | Store 내 파일 목록 조회 |
| POST | `/file/delete_store` | Store 삭제 |
| POST | `/file/delete_document` | 문서 삭제 |


## Tech Stack

- **Python** 3.12
- **uv** (패키지 매니저)
- **FastAPI** + **Uvicorn** (ASGI)
- **Gunicorn** (프로덕션 프로세스 매니저)
- **httpx** (비동기 HTTP 클라이언트)
- **orjson** (고성능 JSON 직렬화)
- **tiktoken** (토큰 카운팅)
- **FastMCP** (MCP 프로토콜)


## Environment Variables

```env
# Server
SERVER_STAGE=""              # docker | docker-local | (빈값: 개발)

# LLM API Keys
OPENAI_API_KEY=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_BASE_URL=""
AZURE_OPENAI_API_VERSION=""
ANTHROPIC_API_KEY=""
GOOGLE_API_KEY=""
XAI_API_KEY=""

# Self-hosted
FOURGRIT_URL=""
FOURGRIT_EMBEDDING_URL=""

# Auth
JWT_SECRET_KEY=""
```


## Getting Started

### 1. Clone & Install

```bash
git clone https://git.beusable.net/4grit/llm-proxy.git
cd llm-proxy
uv sync
```

### 2. Configure

`.env` 파일을 생성하고 필요한 환경 변수를 설정한다.

### 3. Run

개발 환경 (hot reload):
```bash
uv run python main.py
```

프로덕션 환경 (Gunicorn + Uvicorn workers):
```bash
uv run gunicorn -c gunicorn.config.py main:app
```

Docker:
```bash
docker build -t llm-proxy .
docker run -p 9999:9999 --env-file .env llm-proxy
```

서버는 `0.0.0.0:9999`에서 실행된다.


### 의존성 관리

```bash
# 패키지 추가
uv add <package>

# 패키지 제거
uv remove <package>

# lock 파일 갱신
uv lock
```


## Gunicorn Config

| 설정 | 값 |
|------|-----|
| Workers | 4 |
| Threads | 8 |
| Worker Class | `uvicorn.workers.UvicornWorker` |
| Timeout | 300s |
| Max Requests | 200 (jitter: 50) |


## Key Features

- **Vendor Abstraction**: 동일한 인터페이스로 모든 LLM 벤더에 접근
- **Auto Fallback**: 1차 벤더 장애 시 2차 벤더로 자동 전환
- **Streaming Pipeline**: SSE 기반 chunk 단위 실시간 스트리밍
- **MCP Support**: Model Context Protocol을 통한 Tool Use 지원
- **Token Validation**: 요청 전 토큰 길이 검증
- **Image Support**: Base64 / URL 이미지 입력 지원
- **FileSearch**: Google FileSearch Store CRUD + S3 연동
- **Embeddings**: 텍스트 임베딩 벡터 생성