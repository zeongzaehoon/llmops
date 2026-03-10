from dataclasses import dataclass, field

from client.mongo import MongoClient
from client.redis import RedisClient
from client.slack import SlackClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient



@dataclass
class AgentNode:
    """그래프 내 개별 에이전트 노드"""
    agent: str
    role: str = ""
    # _load_agent_config에서 DB 조회 후 설정
    vendor: str | None = None
    model: str | None = None
    system_message: str | None = None


@dataclass
class EdgeNode:
    """에이전트 간 연결 엣지"""
    source: str               # 출발 에이전트명
    target: str               # 도착 에이전트명
    condition: str = None     # 조건 (LLM 평가용 프롬프트, None이면 무조건 통과)
    on_failure: str = "end"   # "retry" | "end" | 에이전트명(분기)
    max_retries: int = 2


@dataclass
class MultiAgentArgs:
    """멀티 에이전트 실행에 필요한 인자"""
    # server
    server_stage: str

    # session
    session_key: str
    question: str

    # graph info
    graph_id: str
    graph_type: str  # "linear" | "debate" | "parallel" | "router" | "custom"
    agents: list[AgentNode] = field(default_factory=list)
    edges: list[EdgeNode] = field(default_factory=list)

    # config
    max_iterations: int = 3  # debate용 최대 라운드
    streaming: bool = True

    # clients
    llm_proxy_client: LLMProxyClient | None = None
    main_db_client: MongoClient | None = None
    memory_db_client: RedisClient | None = None
    message_client: SlackClient | None = None

    # language
    lang: str | None = None
