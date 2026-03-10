# Solomon - LLM 기반 분석 & 리포트 플랫폼

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Solomon |
| **소속** | 4grit |
| **역할** | 리드 개발 (Backend / Infra) |
| **기간** | 기업 프로젝트 |
| **한 줄 요약** | 20개 이상의 분석 카테고리를 지원하는 멀티 LLM 기반 실시간 AI 분석 플랫폼 |

Solomon은 UX 히트맵, 저니맵, VOC, 대시보드 등 다양한 분석 데이터를 LLM에 연결하여 **자연어 기반의 인사이트 도출과 AI 리포트 자동 생성**을 제공하는 엔터프라이즈 플랫폼입니다. 단순 챗봇이 아닌, RAG 파이프라인과 MCP(Model Context Protocol) 에이전트를 결합한 **지능형 분석 인프라**를 설계하고 구현했습니다.

---

## 기술 스택

### Backend
`Python` `FastAPI` `Gunicorn` `Uvicorn` `asyncio` `Motor(MongoDB)` `Redis` `Pinecone` `aioboto3(AWS S3)` `JWT` `tiktoken` `FastMCP` `Pydantic`

### Frontend
`Vue 3` `Composition API` `Vite` `Vuex` `Vue Router` `vue-i18n` `Chart.js` `CKEditor 5` `html2pdf.js` `SCSS` `Vitest`

### Infra / DevOps
`Docker` `Docker Compose` `Nginx` `Slack Webhook`

### AI / ML
`OpenAI API` `Anthropic API` `Azure OpenAI` `AWS Bedrock` `Google Gemini` `Pinecone(Vector DB)` `RAG` `MCP(Model Context Protocol)`

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                   Vue 3 Frontend (:3333)                │
│         Playground Chat / AI Report / Dashboard         │
│            다국어 지원 (KO / EN / JA)                   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Nginx Reverse Proxy (:9876)            │
│        / → Frontend    /solomon-api/ → Backend          │
│            WebSocket Upgrade / 180s Streaming           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               FastAPI Backend (:8888)                   │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │
│  │ Question API│  │  Agent API   │  │ Operation API │   │
│  │  (핵심 Q&A) │  │  (MCP 관리)  │  │  (운영 관리)  │   │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘   │
│         │                │                              │
│  ┌──────▼────────────────▼──────┐                       │
│  │    Category Router (24+)     │                       │
│  │  AIReport / VOC / Dashboard  │                       │
│  │  Heatmap / Docent / MCP ...  │                       │
│  └──────┬───────────────────────┘                       │
│         │                                               │
│  ┌──────▼──────────────────┐  ┌──────────────────────┐  │
│  │  RunLLM (LLM 오케스트라)│  │   RunMCP (에이전트)  │  │
│  │  Prompt + RAG + Stream  │  │  Tool Use + Context  │  │
│  └─────────────────────────┘  └──────────────────────┘  │
└────┬──────────┬──────────┬──────────┬───────────────────┘
     │          │          │          │
┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼──────┐
│MongoDB │ │ Redis  │ │Pinecone│ │ AWS S3   │
│ (Data) │ │(Cache) │ │(Vector)│ │(Storage) │
└────────┘ └────────┘ └────────┘ └──────────┘
                                       │
                               ┌───────▼────────┐
                               │  LLM Proxy     │
                               │  (groxy)       │
                               │ OpenAI / Claude│
                               │ Bedrock / etc. │
                               └────────────────┘
```

---

## 핵심 성과 및 기술적 도전

### 1. 멀티 LLM 프로바이더 추상화 계층 설계

**문제**: OpenAI, Anthropic, Azure, AWS Bedrock, Google, X.AI 등 6개 이상의 LLM 프로바이더를 지원해야 했으며, 각 프로바이더마다 API 스펙과 스트리밍 방식이 상이했습니다.

**해결**: LLM Proxy(groxy)를 통한 단일 추상화 레이어를 설계하여, 비즈니스 로직에서 프로바이더 종속성을 완전히 제거했습니다. 카테고리별로 최적의 벤더/모델을 매핑하는 전략 패턴을 적용했습니다.

```
카테고리별 모델 매핑 예시:
- Dashboard 분석 → Anthropic Claude Sonnet (복잡한 데이터 해석)
- AI Report 생성 → OpenAI GPT-4o (긴 문서 생성)
- 기본 질의 → OpenAI o3-mini (비용 효율)
```

**성과**: 프로바이더 교체/추가 시 비즈니스 로직 변경 없이 설정만으로 대응 가능한 유연한 구조 확보

---

### 2. 비동기 기반 고성능 데이터 오케스트레이션

**문제**: 하나의 질문 처리에 MongoDB(프롬프트 조회), Pinecone(유사 문서 검색), Redis(대화 이력), S3(리포트 데이터) 등 **4개 이상의 데이터 소스**를 조회해야 했습니다.

**해결**: `asyncio.gather()`를 활용한 병렬 I/O 패턴으로 모든 데이터 소스를 동시 조회하도록 설계했습니다.

```python
# 순차 처리 시: ~2000ms → 병렬 처리 시: ~500ms (최대 지연 소스 기준)
system_prompt, retrieval_data, history = await asyncio.gather(
    get_system_prompt(main_db),      # MongoDB
    get_retrieval(vector_db),         # Pinecone
    get_conversation_history(redis),  # Redis
)
```

**성과**: 응답 지연 시간을 순차 처리 대비 약 **75% 단축**, 높은 동시성 처리 달성

---

### 3. RAG (Retrieval-Augmented Generation) 파이프라인 구축

**문제**: LLM이 기업 내부 데이터(UX 분석 결과, 고객 데이터 등)를 알지 못하므로, 정확한 답변을 위해 관련 문맥을 동적으로 주입해야 했습니다.

**해결**: Pinecone 벡터 DB를 활용한 카테고리별 RAG 파이프라인을 구축했습니다.

- 카테고리별 독립 인덱스 운영 (환경별 staging/production 분리)
- 질문에 대한 유사도 기반 문서 검색 (top-k=4)
- 검색된 문맥을 시스템 프롬프트에 동적 삽입
- tiktoken 기반 토큰 수 계산으로 컨텍스트 윈도우 최적화

**성과**: 도메인 특화 데이터에 대한 정확한 답변 생성, 할루시네이션 감소

---

### 4. 실시간 스트리밍 응답 아키텍처

**문제**: LLM 응답은 수 초~수십 초가 소요되며, 사용자가 빈 화면을 보고 기다리는 UX는 허용할 수 없었습니다.

**해결**: 엔드투엔드 스트리밍 파이프라인을 구축했습니다.

- **Backend**: FastAPI의 `StreamingResponse`와 비동기 제너레이터로 토큰 단위 전송
- **Nginx**: WebSocket 업그레이드 헤더 + 180초 타임아웃 설정
- **Frontend**: Fetch API의 `ReadableStream`과 `AbortController`로 실시간 렌더링 및 중단 처리

**성과**: 첫 토큰 수신까지의 시간(TTFT)을 최소화하여 체감 응답 속도 대폭 개선

---

### 5. 24개 이상의 분석 카테고리 확장 가능한 설계

**문제**: AIReport, VOC, Dashboard, Heatmap, Docent, Schema, Geo 등 지속적으로 새로운 분석 유형이 추가되었습니다.

**해결**: 카테고리 기반 라우팅 아키텍처를 설계하여, 새 카테고리 추가 시 비즈니스 로직만 구현하면 되는 플러그인 구조를 만들었습니다.

| 분류 | 카테고리 |
|------|---------|
| 리포트 | AIReport, Docent, ReportChat, ScrollChat |
| 분석 | Dashboard, DashboardChat, DashboardHell |
| AIEO | GeoSimple, GeoJSON, GeoChat |
| 고객분석 | VOC, UXGPT, ContactUs |
| 에이전트 | JourneyMapMCP, CXDataTrendMCP, BI-MCP |

**성과**: 단일 코드베이스에서 24개 이상의 분석 서비스를 관리하며, 새 카테고리 추가 시 개발 비용 최소화

---

### 6. MCP (Model Context Protocol) 에이전트 통합

**문제**: 단순 Q&A를 넘어, LLM이 외부 도구를 호출하고 다단계 추론을 수행하는 에이전트 기능이 필요했습니다.

**해결**: FastMCP를 활용한 에이전트 시스템을 구축했습니다.

- MCP 서버 등록/관리 API (`/agent/enroll_mcp_server`)
- 동적 툴셋 구성 (`/agent/create_mcp_toolset`)
- RunMCP 클래스를 통한 에이전트 실행 파이프라인
- RunLLM과 RunMCP 간 전략적 분기 처리

**성과**: LLM이 외부 데이터 소스 접근, 계산, API 호출 등을 자율적으로 수행하는 에이전트 기능 구현

---

### 7. 멀티 테넌트 데이터 격리

**문제**: 일반 고객과 삼성 등 엔터프라이즈 고객의 데이터를 완전히 격리해야 했습니다.

**해결**: 별도의 MongoDB 인스턴스(MongoClient / SSMongoClient)와 독립 API 라우터(`/ss_question`)를 구성하여 물리적 데이터 격리를 달성했습니다.

**성과**: 엔터프라이즈 고객별 데이터 보안 요구사항 충족

---

### 8. 컨테이너 기반 마이크로서비스 인프라 구축

4개의 Docker 컨테이너를 오케스트레이션하는 인프라를 설계했습니다.

```yaml
서비스 구성:
  solomon-web    # Vue 3 프론트엔드 (Node 18)
  solomon-api    # FastAPI 백엔드 (Python 3.12)
  solomon-redis  # 세션/캐시 (Redis)
  solomon-nginx  # 리버스 프록시/로드밸런서 (Nginx)
```

- Nginx를 통한 프론트엔드/백엔드 통합 라우팅
- 멀티 스테이지 Docker 빌드로 이미지 크기 최적화
- 환경별(dev/staging/production) 설정 분리
- 외부 네트워크(`ai-network`)를 통한 서비스 간 통신

---

### 9. 프로덕션 안정성 확보

- **Graceful Lifecycle**: `@asynccontextmanager`를 활용한 8개 서비스 커넥션의 안전한 시작/종료
- **싱글톤 클라이언트**: `asyncio.Lock()` 기반의 스레드 세이프한 커넥션 풀 관리
- **에러 체계화**: `DBError`, `MemoryDBError`, `VectorDBError`, `LLMStreamingError` 등 커스텀 예외 계층 설계
- **장애 알림**: 프로덕션 환경에서 Slack Webhook을 통한 실시간 에러 알림
- **보안**: JWT 기반 인증(Access Token 1일 / Refresh Token 3일), 환경별 CORS 화이트리스트

---

## MongoDB 스키마 설계

### 컬렉션 구조 개요

스키마리스(Schemaless) 특성의 MongoDB를 사용하되, 애플리케이션 레벨에서 Pydantic과 포맷 함수를 통해 **일관된 도큐먼트 구조**를 유지하도록 설계했습니다. 총 9개의 컬렉션을 역할별로 분리하여 운영합니다.

```
MongoDB
├── solomonChatHistory       # 대화 이력 (질문/응답/평점)
├── solomonPromptHistory     # 시스템 프롬프트 버전 관리
├── baAIReportPrompt         # AI 리포트 프롬프트 조합 (역할 구성)
├── baAIReport               # AI 리포트 메타데이터 & 생성 상태
├── heatmapAIReport          # 히트맵 리포트
├── geoAIReport              # 지리정보 리포트
├── solomonModels            # LLM 모델 설정
├── solomonMCPServers        # MCP 서버 레지스트리
└── solomonMCPAgents         # MCP 에이전트/툴셋 정의
```

### 멀티 DB 인스턴스 구조

데이터 격리를 위해 2개의 독립 MongoDB 클라이언트를 싱글톤으로 운영합니다.

| 클라이언트 | 용도 | 환경 |
|-----------|------|------|
| `MongoClient` | 메인 서비스 DB | Staging |
| `ProductionMongoClient` | 메인 서비스 DB (SSL) | Production |


---

### 핵심 컬렉션 상세

#### 1. solomonChatHistory - 대화 이력

모든 사용자 질문과 AI 응답을 기록하는 핵심 컬렉션입니다. `sessionKey`로 사용자를 식별하고, `ask_id`로 질문-응답 쌍을 연결합니다.

```javascript
{
  // 식별
  "sessionKey": "uuid-session-key",     // 사용자 세션 식별자
  "ask_id": "uuid-ask-id",             // 질문-응답 쌍 연결 ID
  "cid": "ObjectId-as-string",         // 대화 스레드 연결 ID

  // 메시지 내용
  "role": "human" | "ai",              // 발화자 구분
  "message": "질문 또는 응답 텍스트",
  "rating": 0,                          // 사용자 평점 (0: 미평가)

  // 분류
  "category": "main",                   // 서비스 카테고리
  "kind": "result" | "query" | "refer", // 데이터 유형

  // LLM 정보
  "vendor": "openai",                   // 사용된 프로바이더
  "model": "gpt-4o",                    // 사용된 모델
  "token": 1523,                        // 소비 토큰 수

  // 참조 (AI 응답 시)
  "pid": "prompt-ObjectId",             // 사용된 프롬프트 참조
  "qid": "query-ObjectId",             // 쿼리 프롬프트 참조

  // AI 리포트 연결
  "aireportId": "report-ObjectId",      // 연관 리포트 ID
  "aireportType": "trend",             // 리포트 유형
  "filename": "uploaded-file.csv",      // 업로드 파일명

  // 메타
  "date": ISODate("2026-03-03T...")     // UTC 타임스탬프
}
```

**설계 의도**: 하나의 컬렉션에서 `role` 필드로 질문/응답을 구분하고, `ask_id`로 쌍을 매핑합니다. `kind` 필드를 통해 같은 컬렉션 내에서 결과(`result`), 쿼리 프롬프트(`query`), 참고 자료(`refer`) 등 다른 유형의 데이터를 통합 관리합니다.

---

#### 2. solomonPromptHistory - 프롬프트 버전 관리

시스템 프롬프트를 Blue-Green 배포 전략으로 관리하는 컬렉션입니다.

```javascript
{
  "prompt": "You are a UX analyst. Analyze the following data...",
  "memo": "Dashboard 분석용 메인 프롬프트 v3",
  "category": "dashboard",
  "kind": "prompt" | "query" | "refer",   // 프롬프트 유형

  // 버전 관리 (Blue-Green)
  "deployStatus": "green" | "blue" | 1,   // green=활성, blue=대기, 1=이전 버전

  // 다중 역할 지원
  "roleName": "data_analyzer",            // 역할명 (멀티 프롬프트 시)
  "order": 1,                              // 실행 순서

  "getResult": false,                      // 결과 생성 여부
  "date": ISODate("2026-03-03T...")
}
```

**Blue-Green 배포 플로우**:
```
1. 기존 blue 버전 → 1 (아카이브)
2. 기존 green 버전 → blue (대기)
3. 신규 프롬프트 → green (활성)
```

이를 통해 **프롬프트 변경 시 즉시 롤백이 가능**하고, 프로덕션 배포 전 blue 환경에서 검증할 수 있습니다.

---

#### 3. baAIReport - AI 리포트 상태 관리

AI 리포트의 전체 생성 라이프사이클을 추적하는 컬렉션입니다. 캡처 → 데이터 수집 → 리포트 생성 → 요약의 **4단계 파이프라인 상태**를 각각 독립적으로 관리합니다.

```javascript
{
  // 리포트 식별
  "userId": "user-123",
  "sid": "service-id",
  "domain": "example.com",
  "type": "single" | "mashup" | "compare",   // 리포트 유형
  "lang": "ko" | "en" | "ja",

  // 분석 조건
  "matchType": "url",
  "device": "mobile",
  "startDateStr": "2026-01-01",
  "endDateStr": "2026-01-31",

  // 4단계 파이프라인 상태
  "captureStatus": "pending" | "complete",    // 1단계: 캡처
  "captureS3Path": "s3://bucket/capture/...",
  "captureDate": ISODate("..."),

  "dataStatus": "pending" | "complete",       // 2단계: 데이터 수집
  "dataS3Path": "s3://bucket/data/...",
  "dataDate": ISODate("..."),

  "reportStatus": "ing" | "complete",         // 3단계: 리포트 생성
  "reportS3Path": "s3://bucket/report/...",
  "reportDate": ISODate("..."),

  "summaryStatus": "ing" | "complete",        // 4단계: 요약
  "summaryS3Path": "s3://bucket/summary/...",
  "summaryDate": ISODate("..."),

  // Mashup/Compare 관계
  "orgId": "parent-ObjectId",                 // 부모 리포트 (mashup 시)
  "refAid": ["ObjectId-1", "ObjectId-2"],     // 참조 리포트 목록

  // 관리
  "deleted": false,                            // Soft Delete
  "regDate": ISODate("...")
}
```

**설계 의도**: 하나의 도큐먼트 안에 4단계 상태를 독립 필드로 관리하여, 각 단계가 비동기로 진행되더라도 상태 추적이 가능합니다. `orgId`/`refAid`로 리포트 간 부모-자식 관계를 표현합니다.

---

#### 4. baAIReportPrompt - 프롬프트 역할 조합

AI 리포트 생성 시 어떤 역할(role)들을 조합하여 프롬프트를 구성할지 정의합니다.

```javascript
{
  "type": "trend",                                  // 리포트 유형
  "roleNameList": ["analyst", "summarizer"],        // 기본 역할 구성
  "roleNameListForPlus": ["analyst", "summarizer",  // 심화 분석 역할 구성
                           "critic", "advisor"],
  "deployStatus": "green" | "blue"                  // 배포 상태
}
```

**설계 의도**: 리포트 유형별로 LLM이 수행할 역할(분석가, 요약가, 비평가 등)을 조합하여 **멀티 역할 프롬프트 체이닝**을 구현합니다. `roleNameListForPlus`로 일반/심화 분석을 구분합니다.

---

#### 5. solomonMCPServers / solomonMCPAgents - MCP 에이전트 관리

```javascript
// solomonMCPServers - 서버 레지스트리
{
  "name": "data-analysis-server",
  "uri": "http://mcp-server:8080",
  "token": "auth-token",
  "desc": "데이터 분석용 MCP 서버"
}

// solomonMCPAgents - 툴셋 정의
{
  "category": "journeymap-mcp",
  "name": "JourneyMap Analyzer",
  "regDate": ISODate("..."),
  "mcpInfo": [                          // 서버-도구 매핑
    {
      "serverId": "server-ObjectId",
      "tools": ["analyze_path", "generate_heatmap", "export_report"]
    }
  ],
  "desc": "저니맵 분석 에이전트",
  "isService": true                     // 서비스 활성화 여부
}
```

---

### 컬렉션 간 관계도

```
solomonChatHistory ──pid──▶ solomonPromptHistory
        │                          │
        │ ask_id (Q&A 쌍)          │ roleName
        │                          ▼
        │              baAIReportPrompt
        │              (역할 조합 정의)
        │
        │ aireportId
        ▼
   baAIReport ──orgId──▶ baAIReport (부모-자식)
        │
        │ S3 경로 참조
        ▼
     AWS S3 (capture / data / report / summary)


solomonMCPServers ──serverId──▶ solomonMCPAgents
                                      │
                                      │ category
                                      ▼
                               solomonChatHistory
```

---

### 카테고리별 데이터 저장 전략

동일한 컬렉션이라도 카테고리에 따라 저장 경로가 다르게 라우팅됩니다.

| 데이터 유형 | AIReport 계열 | 기타 카테고리 |
|------------|--------------|-------------|
| **프롬프트(prompt)** | `solomonPromptHistory` | `solomonPromptHistory` |
| **쿼리(query)** | `solomonPromptHistory` | `solomonChatHistory` |
| **결과(result)** | `solomonChatHistory` | `solomonChatHistory` |
| **참고(refer)** | `solomonChatHistory` | `solomonChatHistory` |

AIReport 카테고리는 쿼리 프롬프트도 `solomonPromptHistory`에 저장하여 프롬프트와 쿼리를 함께 버전 관리합니다.

---

### Redis 캐시 계층 (보조 저장소)

MongoDB와 함께 Redis를 대화 컨텍스트 캐시로 활용합니다.

| 키 패턴 | 용도 | TTL |
|---------|------|-----|
| `rc:{sessionKey}` | 리포트 컨텐츠 캐시 | 1시간 |
| `rc_id:{sessionKey}` | 리포트 ID 캐시 | 1시간 |
| 대화 이력 리스트 | 멀티턴 대화 컨텍스트 | 1시간 |

**설계 의도**: 멀티턴 대화에서 매번 MongoDB를 조회하지 않고, Redis에 최근 대화 컨텍스트를 캐싱하여 응답 지연을 줄입니다. TTL 1시간으로 자동 만료되어 메모리 누수를 방지합니다.

---

## 프론트엔드 주요 구현

### AI 리포트 뷰어
- Chart.js 기반 인터랙티브 차트 렌더링 (Dashboard, Journey, Ranking, Trend 등)
- html2pdf.js를 활용한 리포트 PDF 내보내기
- CKEditor 5 통합 리치 텍스트 편집

### 실시간 채팅 인터페이스 (Playground)
- Fetch Streaming 기반 실시간 토큰 렌더링
- AbortController를 활용한 응답 중단 처리
- MCP 서버/툴셋 관리 UI
- 대화 이력 조회 및 평점 시스템

### 다국어 & 테마
- vue-i18n 기반 3개 언어 지원 (한국어, 영어, 일본어)
- 동적 컬러 테마 시스템 (localStorage 기반 영속화)

---

## 프로젝트 구조

```
solomon-docker/
├── api/                          # FastAPI 백엔드
│   ├── main.py                   # 앱 진입점 & 라이프사이클
│   ├── api/                      # API 라우터 (question, agent, operation, vector)
│   ├── auth/                     # JWT 인증 미들웨어
│   ├── client/                   # 인프라 클라이언트 (MongoDB, Redis, Pinecone, S3, Slack)
│   ├── helper/                   # 비즈니스 로직
│   ├── module/
│   │   ├── llm/                  # LLM 오케스트레이션 (activate, run, dto, args)
│   │   ├── mcp/                  # MCP 에이전트 (activate, run, dto)
│   │   ├── dashboard/            # 대시보드 분석 모듈
│   │   └── microagent/           # 마이크로에이전트 (검증)
│   ├── payload/                  # Pydantic 요청 스키마
│   └── utils/                    # 유틸리티 (에러, 상수, 응답 포맷)
├── ui/                           # Vue 3 프론트엔드
│   └── src/
│       ├── components/
│       │   ├── aireport/         # AI 리포트 (11개 서브 모듈)
│       │   ├── playground/       # 채팅 인터페이스 (8개 서브 모듈)
│       │   └── contactus/        # 고객 문의
│       ├── api/                  # API 클라이언트 (chat, connect, report, mcp)
│       ├── store/                # Vuex 상태 관리
│       ├── router/               # Vue Router
│       └── locales/              # i18n (ko, en, ja)
├── nginx/                        # Nginx 리버스 프록시
├── redis/                        # Redis 캐시
└── docker-compose.yml            # 컨테이너 오케스트레이션
```

---

## 기술적 의사결정 요약

| 결정 | 이유 |
|------|------|
| FastAPI + asyncio 전면 도입 | 다중 I/O 병렬 처리로 응답 지연 최소화 |
| LLM Proxy 추상화 레이어 | 6개 프로바이더 교체/추가의 유연성 확보 |
| 카테고리별 Pinecone 인덱스 분리 | 도메인 특화 검색 정확도 향상 + 환경 격리 |
| Streaming-First 설계 | 사용자 체감 응답 속도 극대화 |
| 싱글톤 + asyncio.Lock 패턴 | 비동기 환경에서의 스레드 안전한 커넥션 관리 |
| Docker Compose 멀티 서비스 | 일관된 개발/배포 환경 + 서비스 격리 |
| JWT 세션 기반 인증 | 무상태 서버 설계로 수평 확장 용이 |
| MCP 에이전트 통합 | 단순 Q&A를 넘어 도구 사용 가능한 AI 에이전트로 확장 |

---

## 배운 점

- **비동기 프로그래밍의 실전 적용**: `asyncio.gather()`를 통한 병렬 I/O가 실제 서비스 응답 시간에 미치는 영향을 체감하고, 비동기 환경에서의 커넥션 관리와 에러 핸들링 패턴을 깊이 익혔습니다.
- **LLM 서비스 설계의 복잡성**: 프롬프트 관리, 토큰 최적화, 스트리밍 처리, 멀티 프로바이더 지원 등 LLM을 프로덕션에 올리기 위해 필요한 인프라 수준의 고려사항들을 경험했습니다.
- **확장 가능한 아키텍처**: 24개 이상의 카테고리를 단일 코드베이스에서 관리하면서, 카테고리 추가 시 최소한의 코드 변경으로 대응할 수 있는 설계의 중요성을 배웠습니다.
- **엔드투엔드 시스템 설계**: 프론트엔드부터 백엔드, 인프라, AI 파이프라인까지 전체 스택을 설계하고 운영한 경험을 통해, 각 레이어 간의 연결과 트레이드오프를 종합적으로 판단하는 역량을 키웠습니다.
