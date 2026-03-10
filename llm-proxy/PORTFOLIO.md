# LLM Proxy

> 다양한 LLM 벤더의 API를 단일 인터페이스로 통합하고, 장애 시 자동 전환(Failover)을 지원하는 프록시 서버

## 개요

LLM을 활용하는 여러 서비스에서 벤더마다 다른 SDK와 메시지 포맷을 직접 관리하는 대신,
**하나의 API 요청으로 원하는 벤더/모델을 동적으로 선택**할 수 있도록 만든 중간 계층 서버입니다.

## 해결한 문제

| 문제 | 해결 |
|------|------|
| 벤더마다 다른 SDK, 메시지 포맷, 스트리밍 방식 | 통합 인터페이스로 추상화하여 클라이언트 코드 변경 없이 벤더 교체 가능 |
| 특정 벤더 장애 시 서비스 중단 | 자동 Failover로 1차 실패 시 2차 벤더로 즉시 전환 |
| 서비스별 API Key 분리 관리의 어려움 | 서비스 이름 기반으로 API Key를 자동 라우팅 |
| LLM 스트리밍 응답의 지연 없는 전달 | 청크 단위 SSE 파이프라인으로 실시간 전달 |

## 아키텍처

```
Client → FastAPI → LLM Proxy → Vendor API (OpenAI, Anthropic, Google, AWS Bedrock, Azure, xAI)
                       │
                       ├─ Vendor 선택 (요청의 vendor 필드 기반)
                       ├─ Failover (1차 실패 → 2차 벤더 자동 전환)
                       └─ 응답 포맷 통일 (벤더별 응답 → 공통 JSON 구조)
```

### 요청/응답 흐름 (Streaming)

```
Vendor API → "H" → Proxy → "H" → Client    # 청크 단위로 지연 없이 전달
Vendor API → "e" → Proxy → "e" → Client
Vendor API → "l" → Proxy → "l" → Client
...
```

## 주요 기능

### 1. 멀티 벤더 지원
요청 시 `vendor`와 `model` 필드만 변경하면 6개 벤더의 LLM을 동적으로 사용할 수 있습니다.

- **OpenAI** - GPT-4o, GPT-5, o1, o3-mini, o4-mini 등
- **Anthropic** - Claude Sonnet 4, Claude Opus 4 등
- **Google** - Gemini 2.5 Flash/Pro, Gemini 3 등
- **AWS Bedrock** - Anthropic 모델의 AWS 호스팅 버전
- **Azure OpenAI** - OpenAI 모델의 Azure 호스팅 버전
- **xAI** - Grok 4 등

### 2. 자동 Failover
1차 벤더 호출 실패 시, 동일 역할의 2차 벤더로 자동 전환됩니다.

```
OpenAI 실패 → Azure로 전환
Anthropic 실패 → Bedrock으로 전환
Google 실패 → OpenAI로 전환
```

### 3. Streaming 파이프라인
- 벤더별로 다른 스트리밍 이벤트 타입을 통일된 JSON 포맷으로 변환
- SSE(Server-Sent Events) 기반의 청크 단위 실시간 전달
- 첫 번째 응답 수신 전 Timeout 감지 후, 수신 시작되면 Timeout 해제

### 4. MCP(Model Context Protocol) 연동
- 외부 MCP 서버와 연결하여 LLM이 외부 도구(Tool)를 사용할 수 있는 Agentic 워크플로우 지원
- 다중 MCP 서버 동시 연결 및 도구 이름 충돌 방지 (서버별 Prefix 부여)
- LLM ↔ Tool 반복 호출 루프 (최대 10회 iteration)

### 5. 서비스별 API Key 격리
- 요청의 `service` 필드 기반으로 서비스별 독립 API Key를 자동 매핑
- 서비스 간 사용량 추적 및 비용 분리 가능

### 6. 토큰 길이 검증
- 요청 전 입력 토큰 수를 사전 계산하여 Context Window 초과 방지
- 모델별 상이한 제한(128K / 200K)을 자동 적용

## 기술 스택

| 구분 | 기술 |
|------|------|
| Language | Python 3.12 |
| Framework | FastAPI (비동기) |
| Server | Gunicorn + Uvicorn |
| Serialization | orjson |
| LLM SDK | openai, anthropic, google-genai, aioboto3 (Bedrock), xai-sdk |
| MCP | fastmcp (Streamable HTTP) |
| Infra | Docker |

## API

| Endpoint | 설명 |
|----------|------|
| `POST /llm/chat` | LLM 채팅 (Streaming / Non-Streaming) |
| `POST /llm/chat_mcp` | MCP Tool 연동 채팅 (Agentic) |
| `POST /llm/embeddings` | 텍스트 임베딩 벡터 생성 |
| `POST /llm/ocr_chat` | 이미지 포함 채팅 (OCR) |

## 요청 예시

```json
{
  "service": "knitlog-production",
  "vendor": "anthropic",
  "model": "claude-sonnet-4-6",
  "question": "오늘 날씨 어때?",
  "systemMessage": "당신은 친절한 AI 어시스턴트입니다.",
  "stream": true
}
```

`vendor`를 `"openai"`, `model`을 `"gpt-4o"`로 바꾸면 동일 코드에서 OpenAI로 전환됩니다.