from dataclasses import dataclass, field

from client.aws import S3Client
from client.mongo import MongoClient
from client.redis import RedisClient
from client.slack import SlackClient
# from client.groxy import LLMProxyClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient, GroxyStreamingResponse, GroxyResponse



@dataclass
class MCPArgs:
    # server_stage
    server_stage: str

    # session info
    session_key: str
    service: str

    # vendor, model info
    vendor: str
    model: str

    # client
    main_db_client: MongoClient
    memory_db_client: RedisClient
    llm_proxy_client: LLMProxyClient
    s3_client: S3Client
    message_client: SlackClient

    # agent
    agent: str

    # segment data
    segment_data: dict | list[dict] | None = None

    # is_mcp
    is_mcp: bool = True
    toolset_id: str = None
    mcp_info: list = None

    # agent result
    lang: str = None
    language_message: str = None

    # groxy args
    question: str = None
    reference: dict = None
    system_message: str = None
    system_message_placeholder: dict = None
    retrieval_data: list = None
    conversation_history: list = None
    temperature: float = None
    callback: object = None
    callback_args: dict = None

    # callback args
    message: str = ""

    # db data
    info: dict | None = None
    chat_info: dict | None = None

    # response from llm-proxy
    response: GroxyStreamingResponse | GroxyResponse = None

    # redis data
    full_response: list = field(default_factory=list)

    # time for debug
    start_time: float | None = None
