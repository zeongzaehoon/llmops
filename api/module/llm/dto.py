from dataclasses import dataclass
from bson import ObjectId

from client.aws import S3Client
from client.mongo import MongoClient
from client.redis import RedisClient
from client.pinecone import PineconeClient
from client.slack import SlackClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient, GroxyStreamingResponse, GroxyResponse



@dataclass
class LLMArgs:
    # server stage
    server_stage: str

    # session info
    session_key: str
    question: str
    agent: str
    service: str

    # client
    llm_proxy_client: LLMProxyClient
    main_db_client: MongoClient
    memory_db_client: RedisClient
    vector_db_client: PineconeClient = None
    s3_client: S3Client = None
    message_client: SlackClient = None

    # vendor, model info
    vendor: str = None
    model: str = None

    # prompt & history
    system_message: str | list = None
    conversation_history: str | list = None
    retrieval_data: str = None
    selected_report_data: str = None

    # settings
    redis_save: bool = True
    indepth: bool = False
    streaming: bool = True

    # language
    lang: str = None

    # aireport
    aireportId: str = None
    aireportType: str = None
    roleNameList: list = None
    roleNameListForPlus: list = None
    docent_mode: bool = False
    test: bool = False
    capture_status: bool = None
    s3_save: dict = None

    # dashboard
    dashboard_data: str = None

    # time
    start_time: float = None
    init_date: object = None

    # extra data
    images: list = None
    filename: str = None
    references: str = None
    mail: str = None
    insert_id: ObjectId = None
    is_report_chat_init: bool = False
    ask_id: str = None

    # info
    info_eagle: dict = None
    info_user: dict = None
    keyword_for_vector: str = None

    # db insert data
    insert_mongo: dict = None

    # response
    answer: str = str()
    response: GroxyStreamingResponse | GroxyResponse = None
    is_error: bool = False
