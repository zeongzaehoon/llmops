# Solomon API

LLM 서비스 API by 4grit

## 1. Requirements

- Python: 3.11
- FastAPI: 0.116.1
- Uvicorn: 0.23.1
- Gunicorn: 23.0.0

### 주요 의존성

| 카테고리 | 패키지 |
|---------|--------|
| Web Framework | fastapi, httpx, requests, pydantic |
| Database | motor (MongoDB), redis, pinecone[grpc,asyncio] |
| Cloud | aioboto3 (AWS S3) |
| AI/LLM | tiktoken, transformers, fastmcp |
| Auth | python-jose, cryptography |

## 2. Environment Variables

```bash
SERVER_STAGE=""          # staging / production
JWT_SECRET_KEY=""

LLM_PROXY_URL=""

# Main Database (MongoDB)
DB_URI=""
REAL_DB_URI=""
DB_NAME=""
REAL_DB_NAME=""

# Memory Database (Redis)
MEMORY_DB_HOST=""
MEMORY_DB_PORT=
MEMORY_DB_NUMBER=

# Cloud (AWS)
AWS_DEFAULT_REGION=""
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""

# Vector Database (Pinecone)
PINECONE_API_KEY=""
PINECONE_ENV=""
```

## 3. Project Structure

```
api/
├── main.py              # FastAPI 앱 진입점
├── api/                 # API 라우터
│   ├── agent.py         # MCP 서버/툴셋 관리
│   ├── operation.py     # 운영 관련 API
│   ├── question.py      # 질문/응답 핵심 API
│   └── vector.py        # 벡터 DB 관련 API
├── auth/                # 인증 미들웨어
│   ├── dependencies.py  # FastAPI 의존성 (JWT 검증)
│   └── jwt.py           # JWT 토큰 생성/검증
├── client/              # 인프라 클라이언트
│   ├── aws.py           # S3 클라이언트
│   ├── fastmcp.py       # FastMCP 클라이언트
│   ├── groxy.py         # LLM Proxy 클라이언트
│   ├── mongo.py         # MongoDB 클라이언트
│   ├── pinecone.py      # Pinecone 벡터 DB 클라이언트
│   └── redis.py         # Redis 클라이언트
├── helper/              # 비즈니스 로직
│   ├── operation.py     # 운영 로직
│   ├── question.py      # 질문 처리 로직
│   └── vector.py        # 벡터 처리 로직
├── module/              # 핵심 모듈
│   ├── llm/             # LLM 추론 모듈
│   ├── mcp/             # MCP (Model Context Protocol) 모듈
│   ├── multi_agent/     # 멀티 에이전트 오케스트레이션
│   ├── dashboard/       # 대시보드 분석 모듈
│   └── microagent/      # 마이크로에이전트 (검증 등)
├── payload/             # 요청 데이터 스키마 (Pydantic)
│   ├── agent.py
│   ├── operation.py
│   ├── question.py
│   └── vector.py
└── utils/               # 공통 유틸리티
    ├── constants.py     # 상수 정의
    ├── date.py          # 날짜 유틸리티
    ├── error.py         # 에러 핸들링
    ├── response.py      # 응답 포맷
    └── vector.py        # 벡터 유틸리티
```

## 4. API Endpoints

### Base Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/check` | 서버 상태 확인 |
| GET | `/hello` | 세션 생성 및 JWT 토큰 발급 |
| GET | `/get_new_session_token` | 새 세션 토큰 발급 |
| GET | `/refresh` | Access Token 갱신 |

### Question API (`/question`)
- `POST /ask` - LLM 질의 응답 (스트리밍)

### Agent API (`/agent`)
- `POST /enroll_mcp_server` - MCP 서버 등록
- `POST /create_mcp_toolset` - MCP 툴셋 생성

### Operation API (`/operation`)
- 운영 관련 API

### Vector API (`/vector`)
- 벡터 DB 관련 API

## 5. Supported Categories

| 카테고리 | 설명 |
|---------|------|
| AIREPORT | AI 리포트 분석 |
| SCHEMATAG | 스키마 태그 분석 |
| DOCENT | 도슨트 대화형 분석 |
| HEATMAP | 히트맵 분석 |
| VOC | 고객의 소리 분석 |
| DASHBOARD | 대시보드 데이터 분석 |
| UXGPT | UX 분석 챗봇 |
| MCP | Model Context Protocol 기반 분석 |

## 6. Running the Server

### Development
```bash
python main.py
```

### Production (with Gunicorn)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8888
```

### Docker
```bash
docker build -t solomon-api .
docker run -p 8888:8888 solomon-api
```

## 7. Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│ Solomon API │───▶│ LLM Proxy   │
└─────────────┘    └──────┬──────┘    └─────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   MongoDB     │ │    Redis      │ │   Pinecone    │
│  (Main DB)    │ │ (Memory/Cache)│ │  (Vector DB)  │
└───────────────┘ └───────────────┘ └───────────────┘
        │
        ▼
┌───────────────┐
│   AWS S3      │
│  (Storage)    │
└───────────────┘
```

## 8. DB Schema

### `solomonChatHistory`

대화 이력 저장.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | PK |
| `sessionKey` | string | 세션 식별자 |
| `ask_id` | string | 질문 고유 ID |
| `role` | string | `"human"` / `"ai"` |
| `message` | string | 메시지 내용 |
| `agent` | string | 에이전트명 |
| `vendor` | string | LLM 벤더 |
| `model` | string | 모델명 |
| `date` | datetime | 생성일시 |
| `rating` | int | 사용자 평가 (default: 0) |
| `token` | int | 토큰 수 |
| `is_demo` | boolean | 데모 여부 |
| `is_mcp` | boolean | MCP 사용 여부 |
| `mcp_tools` | string | 사용된 MCP 도구 |
| `isError` | boolean | 에러 여부 |
| `isInit` | boolean | 초기 메시지 여부 |
| `serviceType` | string | 서비스 타입 (`ba`, `beus` 등) |
| `language` | string | 언어 코드 |
| `cid` | string | Chat ID |
| `pid` | string | Prompt ID |
| `qid` | string | Query ID |
| `rid` | string | Retrieval ID |
| `tid` | string | Table/Report ID |
| `filename` | string | 업로드 파일명 |
| `aireportId` | string | AI 리포트 ID |
| `aireportType` | string | AI 리포트 타입 |
| `memo` | string | 메모 |
| `email` | string | 사용자 이메일 |
| `solved` | boolean | 해결 여부 |

**Indexes:** `ask_id`, `session_id`, `regDate`

---

### `solomonPromptHistory`

프롬프트 버전 관리.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | PK |
| `agent` | string | 에이전트명 |
| `prompt` | string | 프롬프트 내용 |
| `kind` | string | 프롬프트 종류 (`system`, `prompt`, `query`, `refer` 등) |
| `roleName` | string | 역할명 |
| `memo` | string | 메모 |
| `date` | datetime | 생성일시 |
| `getResult` | boolean | 결과 포함 여부 (default: false) |
| `deployStatus` | string | 배포 상태 (`green`: 운영, `blue`: 이전 버전) |

**Indexes:** `deployStatus`

> `deployStatus`는 배포(`deploy`) 시에만 설정됨. 최초 삽입 시에는 미설정.

---

### `solomonModels`

에이전트별 LLM 모델 설정.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | PK |
| `agent` | string | 에이전트명 |
| `vendor` | string | LLM 벤더 (`openai`, `anthropic`, `google` 등) |
| `model` | string | 모델 ID |
| `date` | datetime | 설정일시 |

---

### `solomonMCPServers`

MCP 서버 등록 정보.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | PK |
| `name` | string | 서버명 |
| `uri` | string | 서버 URI |
| `token` | string | 인증 토큰 |
| `desc` | string | 설명 |

**Indexes:** `name`

---

### `solomonMCPAgents`

에이전트별 MCP 툴셋 관리.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | PK |
| `agent` | string | 에이전트명 |
| `name` | string | 툴셋명 |
| `mcpInfo` | array | MCP 설정 배열 |
| `mcpInfo[].serverId` | ObjectId | MCP 서버 ID (→ `solomonMCPServers._id`) |
| `mcpInfo[].tools` | array | 선택된 도구 목록 |
| `isService` | boolean | 서비스 적용 여부 (default: false) |
| `regDate` | datetime | 등록일시 |
| `desc` | string | 설명 |

**Indexes:** `name`, `{agent, isService}`

---

### `solomonMultiAgentGraphs`

멀티 에이전트 그래프 설정.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | PK |
| `name` | string | 그래프명 |
| `graphType` | string | 그래프 타입 (`linear`, `debate`, `parallel`, `router`, `custom`) |
| `agents` | array | 에이전트 목록 |
| `agents[].agent` | string | 에이전트명 |
| `agents[].role` | string | 역할 설명 |
| `edges` | array | 엣지 목록 (`custom` graphType 전용) |
| `edges[].from` | string | 출발 에이전트명 |
| `edges[].to` | string | 도착 에이전트명 |
| `edges[].condition` | string | 조건 프롬프트 (LLM 평가). null이면 무조건 통과 |
| `edges[].onFailure` | string | 조건 실패 시 행동: `retry`, `end`, 또는 에이전트명 |
| `edges[].maxRetries` | int | retry 시 최대 재시도 횟수 (default: 2) |
| `config.maxIterations` | int | 최대 반복 횟수 (default: 3) |
| `regDate` | datetime | 등록일시 |
| `desc` | string | 설명 |

**Indexes:** `name`, `graphType`

**Graph Types:**

| Type | Description |
|------|-------------|
| `linear` | 순차 실행 (A → B → C). 이전 결과가 다음 컨텍스트로 전달 |
| `debate` | 라운드별 토론. 마지막 라운드의 마지막 에이전트가 모더레이터로 종합 |
| `parallel` | 전 에이전트 병렬 실행 후 마지막 에이전트가 결과 종합 |
| `router` | 첫 번째 에이전트가 질문 분석 → 적합한 에이전트 선택 → 실행 |
| `custom` | DAG 기반 실행. edge 조건 평가 → 통과/재시도/분기 |

---

## 9. Agent Lifecycle

```
1. 에이전트 생성       POST /agent/create_mcp_toolset
2. 프롬프트 주입       POST /agent/insert_prompt
3. 모델 설정          POST /agent/set_vendor_and_model
4. 에이전트 동작       POST /question/ask (단일)
                     POST /question/ask + graphId (멀티)
```

### Multi-Agent Flow

```
1. 그래프 생성         POST /agent/create_multi_agent_graph
                     body: { name, graphType, agents: [{agent, role}], maxIterations }

2. 질문 시 graphId 전달  POST /question/ask
                       body: { agent, prompt, graphId }

3. 서버가 그래프 조회 → RunMultiAgent 실행
   - 각 에이전트의 프롬프트/모델을 DB에서 로드
   - graphType에 따라 오케스트레이션
   - SSE 스트리밍 응답
```

### Custom Graph (Edge 기반) 예시

```json
{
  "name": "검증 파이프라인",
  "graphType": "custom",
  "agents": [
    {"agent": "researcher", "role": "자료 조사"},
    {"agent": "analyzer", "role": "분석"},
    {"agent": "reviewer", "role": "검증"},
    {"agent": "writer", "role": "최종 작성"},
    {"agent": "fallback_analyzer", "role": "대체 분석"}
  ],
  "edges": [
    {"from": "researcher", "to": "analyzer"},
    {"from": "analyzer", "to": "reviewer", "condition": "분석 결과에 근거가 충분한가?", "onFailure": "retry", "maxRetries": 2},
    {"from": "reviewer", "to": "writer", "condition": "검증을 통과했는가?", "onFailure": "fallback_analyzer"},
    {"from": "fallback_analyzer", "to": "writer"}
  ]
}
```

**Edge 동작:**
- `condition: null` → 무조건 다음 에이전트로 전달
- `onFailure: "retry"` → source 에이전트 재시도 (maxRetries까지)
- `onFailure: "end"` → 해당 경로 중단
- `onFailure: "에이전트명"` → 지정한 에이전트로 분기