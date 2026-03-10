import os

# stage
DEVELOPMENT = 'development'
STAGING = 'staging'
PRODUCTION = 'production'

# service constant for groxy
CS_STAGING = "cs-staging"
CS_PRODUCTION = "cs-production"
VOC_STAGING = "voc-staging"
VOC_PRODUCTION = "voc-production"
UXHEATMAP_AIREPORT_STAGING = "uxheatmap-aireport-staging"
UXHEATMAP_AIREPORT_PRODUCTION = "uxheatmap-aireport-production"
JOURNEYMAP_AIREPORT_STAGING = "journeymap-aireport-staging"
JOURNEYMAP_AIREPORT_PRODUCTION = "journeymap-aireport-production"
JOURNEYMAP_DASHBOARD = "journeymap-dashboard"
REPORTCHAT_STAGING = "reportchat-staging"
REPORTCHAT_PRODUCTION = "reportchat-production"
SCROLLCHAT_STAGING = "scrollchat-staging"
SCROLLCHAT_PRODUCTION = "scrollchat-production"
DASHBOARD_STAGING = "dashboard-staging"
DASHBOARD_PRODUCTION = "dashboard-production"
DASHBOARDHELL_STAGING="dashboardhell-staging"
DASHBOARDHELL_PRODUCTION="dashboardhell-production"
DASHBOARDCHAT_STAGING = "dashboardchat-staging"
DASHBOARDCHAT_PRODUCTION = "dashboardchat-production"
GEO_SIMPLE_STAGING = "geo-simple-staging"
GEO_SIMPLE_PRODUCTION = "geo-simple-production"
GEO_JSON_STAGING = "geo-json-staging"
GEO_JSON_PRODUCTION = "geo-json-production"
GEO_CHAT_STAGING = "geo-chat-staging"
GEO_CHAT_PRODUCTION = "geo-chat-production"
JOURNEYMAPMCP_STAGING = "journeymapmcp-staging"
JOURNEYMAPMCP_PRODUCTION = "journeymapmcp-production"
CXDATATRENDMCP_STAGING = "cxdatatrendmcp-staging"
CXDATATRENDMCP_PRODUCTION = "cxdatatrendmcp-production"
BIMCP_STAGING = "bimcp-staging"
BIMCP_PRODUCTION = "bimcp-production"

DEFAULT = "default"

# AI-api Provider
AZURE = "azure"
AWS = "aws"
OPENAI = "openai"
ANTHROPIC = "anthropic"
BEDROCK = "bedrock"
FOURGRIT = "4grit"
GOOGLE = "google"
XAI = "xai"
BASE_VENDOR = OPENAI
BASE_MODEL = "o3-mini"
DASHBOARD_VENDOR = ANTHROPIC
DASHBOARD_BASE_MODEL = "claude-sonnet-4-5"
DOCENT_BASE_VENDOR = OPENAI
DOCENT_BASE_MODEL = "o3-mini"
COMPANY_OPENAI = OPENAI
COMPANY_ANTHROPIC = ANTHROPIC
COMPANY_BEDROCK = BEDROCK
COMPANY_AZURE = AZURE
COMPANY_GOOGLE = GOOGLE
COMPANY_4GRIT = FOURGRIT
COMPANY_XAI = XAI
TIKTOKEN_MODEL_LIST = ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1", "o1-pro"]

OPENAI_MODEL_ARRAY_LIST = [
    {"name": "o3-mini", "disabled": False},
    {"name": "gpt-5.2", "disabled": False},
    {"name": "gpt-5.2-pro", "disabled": False},
    {"name": "gpt-5.1", "disabled": False},
    {"name": "gpt-5", "disabled": False},
    {"name": "gpt-5-mini", "disabled": False},
    {"name": "gpt-5-nano", "disabled": False},
    {"name": "gpt-4o", "disabled": False},
    {"name": "gpt-4o-mini", "disabled": False},
    {"name": "gpt-4.1", "disabled": False},
    {"name": "gpt-4.1-mini", "disabled": False},
    {"name": "o4", "disabled": False},
    {"name": "o4-mini", "disabled": False},
    {"name": "o3", "disabled": False},
    {"name": "o3-pro", "disabled": False},

]
ANTHROPIC_MODEL_ARRAY_LIST = [
    {"name": "claude-sonnet-4-6", "disabled": False},
    {"name": "claude-opus-4-6", "disabled": False},
    {"name": "claude-sonnet-4-5", "disabled": False},
    {"name": "claude-haiku-4-5", "disabled": False},
    {"name": "claude-opus-4-5", "disabled": False},
    {"name": "claude-sonnet-4", "disabled": False},
]
BEDROCK_MODEL_ARRAY_LIST = [
    {"name": "anthropic.claude-sonnet-4-6", "disabled": False},
    {"name": "anthropic.claude-opus-4-6-v1", "disabled": False},
    {"name": "global.anthropic.claude-sonnet-4-5-20250929-v1:0", "disabled": False},
    {"name": "global.anthropic.claude-haiku-4-5-20251001-v1:0", "disabled": False},
    {"name": "global.anthropic.claude-opus-4-5-20251101-v1:0", "disabled": False},
    {"name": "apac.anthropic.claude-sonnet-4-20250514-v1:0", "disabled": False}
]
GEMINI_MODEL_ARRAY_LIST = [
    {"name": "gemini-2.5-flash", "disabled": False},
    {"name": "gemini-2.5-flash-lite", "disabled": False},
    {"name": "gemini-2.5-pro", "disabled": False},
    {"name": "gemini-3-flash-preview", "disabled": False},
    {"name": "gemini-3.1-pro-preview", "disabled": False}
]
FOURGRIT_MODEL_ARRAY_LIST = [
    {"name": "gemma3-12b", "disabled": True},
    {"name": "gpt-oss-20b", "disabled": True},
    {"name": "gpt-oss-120b", "disabled": True}
]
XAI_MODEL_ARRAY_LIST = [
    {"name": "grok-4", "disabled": False},
    {"name": "grok-4-fast-non-reasoning", "disabled": False},
    {"name": "grok-4-fast-reasoning", "disabled": False},
    {"name": "grok-code-fast-1", "disabled": False},
    {"name": "grok-3-mini", "disabled": False}
]

MODEL_LIST = [
    {
        "company": COMPANY_ANTHROPIC,
        "models": ANTHROPIC_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_GOOGLE,
        "models": GEMINI_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_OPENAI,
        "models": OPENAI_MODEL_ARRAY_LIST,
    },
    {
        "company": COMPANY_XAI,
        "models": XAI_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_4GRIT,
        "models": FOURGRIT_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_BEDROCK,
        "models": BEDROCK_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_AZURE,
        "models": OPENAI_MODEL_ARRAY_LIST
    }
]
MCP_MODEL_LIST = [
    {
        "company": COMPANY_ANTHROPIC,
        "models": ANTHROPIC_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_BEDROCK,
        "models": BEDROCK_MODEL_ARRAY_LIST
    },
    {
        "company": COMPANY_4GRIT,
        "models": FOURGRIT_MODEL_ARRAY_LIST
    },
]

CONTEXT_WINDOWS_SIZE = {
    "gpt-4o": 110000,
    "gpt-4o-mini": 110000,
    "o1": 180000,
    "o1-pro": 180000,
    "o3-mini": 180000,
    "claude-3-7-sonnet-20250219": 180000,
    "claude-3-5-sonnet-20241022": 180000,
    "claude-3-5-haiku-20241022": 180000,
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 180000,
    "anthropic.claude-3-5-sonnet-20241022-v2:0": 180000,
    "anthropic.claude-3-7-sonnet-20250219-v1:0": 180000,
}

# AGENT NAME(aka. category) LIST
MAIN = "main"
CS = "cs"
CONTACTUS = "contactUs"
REPORTCHAT = "reportchat"
VOC = "voc"
SWCAG = "swcag"
ABTEST = "ab-test"
SCROLL = "scroll"
SCROLLCHAT = "scrollChat"
DASHBOARD = "dashboard"
DASHBOARDHELL = "dashboardHell"
DASHBOARDCHAT = "dashboardChat"
SCHEMATAG="schemaTag"
SCHEMAJSON = "schemaJSON"
SCHEMASIMPLE = "schemaSimple"
SCHEMACHAT = "schemaChat"
WHITEPAPER = "whitePaper"
CXTRENDS = "cxTrends"
JOURNEYMAPMCP = "journeymapMCP"
CXDATATRENDMCP = "cxDataTrendMCP"
DASHBOARDGA = "dashboardGa"
BIMCP="biMCP"


SERVICE_LIST = [
    MAIN, CS, CONTACTUS, REPORTCHAT, DASHBOARDCHAT, DASHBOARD, DASHBOARDHELL, ABTEST,
    SCROLLCHAT, JOURNEYMAPMCP, SCHEMAJSON, SCHEMASIMPLE, SCHEMACHAT, WHITEPAPER, CXTRENDS, CXDATATRENDMCP,
    DASHBOARDGA, BIMCP
]
ON_PRODUCTION_LIST = [SCHEMASIMPLE, CONTACTUS, REPORTCHAT, SCHEMACHAT, SCROLLCHAT, DASHBOARDCHAT, CXDATATRENDMCP, JOURNEYMAPMCP, BIMCP]
MCP_LIST = [SCHEMAJSON, SCHEMASIMPLE, CXDATATRENDMCP, JOURNEYMAPMCP, BIMCP]
MESSAGE_STRUCTURE_LIST = [CXDATATRENDMCP, JOURNEYMAPMCP, BIMCP]
JOURNEY_LIST = [REPORTCHAT, DASHBOARDCHAT, DASHBOARD, DASHBOARDHELL]
HEATMAP_LIST = [ABTEST, SCROLL, SCROLLCHAT]
GEO_LIST = [SCHEMAJSON, SCHEMASIMPLE, SCHEMACHAT]
UXGPT_LIST = [CS, CONTACTUS]
SWCAG_LIST = [SWCAG]
REPORT_LIST = [ABTEST, SCROLL, SCROLLCHAT]
TEST_LIST = ["test"]
CONV_HIST_LIST = [MAIN, CS, CONTACTUS, REPORTCHAT, DASHBOARDCHAT, SWCAG, SCROLLCHAT, SCHEMACHAT, WHITEPAPER, CXTRENDS]
DOCENT_LIST = [REPORTCHAT, DASHBOARDCHAT, SCROLLCHAT, SCHEMACHAT, WHITEPAPER, CXTRENDS]
DOCENT_JOURNEY_LIST = [REPORTCHAT, DASHBOARDCHAT]
DOCENT_HEATMAP_LIST = [SCROLLCHAT]
DOCENT_GEO_LIST = [SCHEMACHAT, WHITEPAPER]
DASHBOARD_LIST = [DASHBOARD, DASHBOARDHELL, DASHBOARDGA]

# role
ROLE_AI = "ai"
ROLE_HUMAN = "human"

# PROMPT DEPLOY
CHAT_COLLECTION = "solomonChatHistory"
PROMPT_COLLECTION = "solomonPromptHistory"
MODEL_COLLECTION = "solomonModels"
MCP_SERVER_COLLECTION = "solomonMCPServers"
AGENT_COLLECTION = "solomonMCPAgents"
MULTI_AGENT_GRAPH_COLLECTION = "solomonMultiAgentGraphs"
HEATMAPAIREPORT_COLLECTION = "heatmapAIReport"

# MULTI AGENT GRAPH TYPES
GRAPH_TYPE_LINEAR = "linear"
GRAPH_TYPE_DEBATE = "debate"
GRAPH_TYPE_PARALLEL = "parallel"
GRAPH_TYPE_ROUTER = "router"
GRAPH_TYPE_CUSTOM = "custom"
GRAPH_TYPES = [GRAPH_TYPE_LINEAR, GRAPH_TYPE_DEBATE, GRAPH_TYPE_PARALLEL, GRAPH_TYPE_ROUTER, GRAPH_TYPE_CUSTOM]
GEOREPORT_COLLECTION = "geoAIReport"
PASSWORD = "4grit"
PINGPONG_INDEX = "PING-PONG SET"

# PINECONE
MAIN_INDEX = "solomon-main"
CONTACTUS_INDEX = "contactus"
REPORTCHAT_INDEX = "reportchat"
CONTACTUS_STAGING_INDEX = "contactus-staging"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_TIKTOKEN_MODEL = "cl100k_base"
EMBEDDING_MAX_TOKEN = 8192

# REDIS
SET_REPORT_REDIS_EXPIRE_TIME = 60 * 60 * 24 * 1 # 1 DAYS
REDIS_EXPIRE_TIME = 60 * 60 * 1 # 1 HOUR

# humanMessage Name
RAG_NAME = "참조 데이터"
USER_QUESTION_NAME = "사용자 질문"
LANG_NAME = "답변 언어"
SEGMENT_DATA_NAME = "사용자 세그먼트 정보"

# THE PROMPT OF CONV HISTORY
CONVERSATION_HISTORY = """<대화 이력>
이전 대화 내용 맥락을 읽고 사용자의 질문에 대해 자세히 알려주세요.
단, 가장 중요한건 사용자가 현재한 질문 내용입니다. 이 전에 같은 질문을 했다면 만족하지 못하고 다시 질문한 것일 수 있으니 이전 대화이력에 있는 대답을 똑같이 하지말고 다시 한번 생각해 대답해주시길 바랍니다.
</대화 이력>"""

# CONTACTUS RETRIEVAL PROMPT
RAG_PROMPT = f"""<{RAG_NAME}>
{RAG_NAME}는 Vector Store에서 사용자 질문에 알맞는 데이터 일부를 얻어온 결과입니다.
Vector Store엔 당신이 답변할 때 사용해야할 정보가 저장되어있습니다.
{RAG_NAME}는 Vector Store에서 질문에 적합한 데이터를 가져온 것이니 질문자의 현재 질문, 이전 대화 내용이 있는 질문에만 답변해주세요.
단, 글 내용 중 contentAdmin 내용은 비공개 내용이므로 활용하지 말아주세요. 또, 일반적인 상식에 대한 질문이 들어오더라도 {RAG_NAME}에 관련 내용이 없으면 답변하지 마시고 아래 사과문 예시 중 하나를 골라 답변해주시길 바랍니다.
'사과문' 예시
1. 죄송합니다. 제가 잘 알지 못하는 내용이에요. 질문주신 내용도 더 잘 답변할 수 있도록 열심히 공부할게요!
2. 제가 답변드리기 어려운 질문이네요.
</참조 데이터>"""

# 시간
TIME_PROMPT = f"""<날짜, 시간>
{RAG_NAME}에 '현재 UTC 시간'이란 title이 달린 데이터가 있습니다.
해당 데이터 content는 UTC 기준 사용자가 질문한 시간을 의미하며 hour는 0시부터 23시로 표현해 전달되니 참고바랍니다.
사용자가 시간 관련된 답변을 원할 시 활용해주시기 바랍니다.
사용자가 한국어로 질문했으면 한국시간, 일본어로 질문했으면 일본시간으로 바꿔서 답변해주세요. 
</날짜, 시간>"""

# LANG
LANG_KO = "ko"
LANG_EN = "en"
LANG_JA = "ja"
LANG_KO_MESSAGE = "한국어로 답변해주세요."
LANG_EN_MESSAGE = "Please respond in English"
LANG_JA_MESSAGE = "日本語で答えてください"
LANG_KO_PROMPT = "한글로 보고서를 작성해주세요."
LANG_EN_PROMPT = "I wrote the report format in Korean, but please translate it into English. Make sure to translate all titles marked with # or ##, column names, and any other content into English. Let me emphasize again: make sure to write the report in English."
LANG_JA_PROMPT = "レポートの形式を韓国語で作成しましたが、日本語に翻訳してください。#や##で指定されたタイトル、データ列名、その他のすべての内容を日本語に翻訳するようにしてください。もう一度強調しますが、レポートは必ず日本語で作成してください。"
LANG_KO_1ST_QUESTION = "한글로 작성해주세요.\n\n"
LANG_JA_1ST_QUESTION = "以下のデータに関するレポートを日本語で作成してください。\n\n"
LANG_EN_1ST_QUESTION = "Please write a report on the data below in English.\n\n"
LANG_KO_2ND_QUESTION = "한글로 작성해주세요.\n\n"
LANG_JA_2ND_QUESTION = "以下のデータとレポートに関する要約を日本語で作成してください。\n\n"
LANG_EN_2ND_QUESTION = "Please write a summary of the data and report below in English.\n\n"
LANG_CHAT_PROMPT = f"""{USER_QUESTION_NAME}が日本語の場合は、日本語で答えてください。
{USER_QUESTION_NAME}이 한국어이면 한국어로 답변해주세요.
Please respond in English if {USER_QUESTION_NAME} is English.
Please respond in {USER_QUESTION_NAME} Language If {USER_QUESTION_NAME} is not in English, Japanese, or Korean.
Please respond in Korean if you can not judge {USER_QUESTION_NAME} language."""
LANG_KO_ERR_MESSAGE = "현재 내부점검 중입니다. 불편을 드려 죄송합니다."
LANG_EN_ERR_MESSAGE = "We are currently undergoing internal maintenance. We apologize for the inconvenience."
LANG_JA_ERR_MESSAGE = "「ただいま内部点検中です。ご不便をおかけして申し訳ございません。」"

# FIXED ANSWER
FIRST_FIXED_QUESTION = "무통장 결제 방법을 알려주세요."
FIRST_FIXED_ANSWER = """무통장 결제를 진행하시려면 다음의 절차를 따라주시면 됩니다:

1. **무통장 결제 진행 방법**
    - 운영팀을 통해 세금계산서 발행을 통한 무통장 결제를 진행하실 수 있습니다.
    - 무통장 결제 시, 결제 금액은 동일합니다.
2. **무통장 결제 시 필요 정보**
    - 필요 서류: 사업자 등록증
    - 필요 정보: 서비스 아이디 / 플랜명(월 제공 PV) / 이용시작일(예정일) / 서비스 이용 기간
    - 세금계산서 발행을 위한 정보: 발행 요청일 / 세금계산서 수신 이메일 / 입금 예정일

이 정보를 준비하신 후, 뷰저블 운영팀으로 연락 부탁드립니다.
운영팀의 이메일 주소는 [beusable@4grit.com](mailto:beusable@4grit.com)입니다.

다른 궁금하신 사항이 또 있으실까요?
"""
SECOND_FIXED_QUESTION = "뷰저블에서는 어떤 플랜을 제공하고 있나요?"
SECOND_FIXED_ANSWER = """뷰저블은 두 가지 주요 서비스를 제공하며, 각각의 서비스에 따라 다양한 플랜을 보유하고 있습니다. 두 서비스를 함께 이용하실 수도 있고, 하나의 서비스만 선택하여 이용하실 수도 있습니다. 다만, 두 서비스를 모두 이용하실 경우 각각의 플랜을 구매하셔야 합니다. 아래는 각 서비스와 플랜에 대한 간단한 설명입니다:

1. **UX Heatmap**
    - 사용자의 UX 행동을 자세하게 분석하는 도구입니다.
    - [UX Heatmap의 플랜 자세히 알아보기](https://forum.beusable.net/ko/solomon/post/847)
2. **Journey Map**
    - 전체 사이트에서 발생하는 고객 여정의 데이터를 수집하여 분석하는 기능입니다.
    - [Journey Map의 플랜 자세히 알아보기](https://forum.beusable.net/ko/solomon/post/848)

각 서비스의 플랜을 잘 살펴보시고, 필요에 맞는 플랜을 선택하시길 바랍니다.

다른 궁금하신 사항이 또 있으실까요?
"""
THIRD_FIXED_QUESTION = "코드가 설치되어있는데 PV가 수집되지 않아요."
THIRD_FIXED_ANSWER = """코드가 설치되어 있지만 PV가 수집되지 않는 문제를 해결하기 위해 다음 사항들을 확인해보세요:

1. **코드 설치 확인**
   - 코드가 정상적으로 설치되었는지 확인하세요. 코드 설치 확인 방법은 [코드 설치 확인하기](https://forum.beusable.net/ko/solomon/post/883)를 참고하세요.
2. **PV 발생 여부**
   - 등록한 페이지에서 실제로 데이터를 발생시킨 후, 1-2시간 후에 리포트에 반영되는지 확인하세요. 데이터 수집에 문제가 없다면 매치 유형과 등록한 페이지의 URL을 검토해야 합니다.
3. **오탈자 확인**
   - 코드 내 오탈자가 있는지 확인하세요. 오탈자가 있을 경우, 코드가 정상적으로 동작하지 않을 수 있습니다. 대시보드에서 확인된 상태로 복사 & 붙여넣기를 통해 설치하는 것이 좋습니다.
4. **SPA 페이지 설정**
   - SPA 구조로 제작된 사이트라면 대시보드에서 SPA 토글을 켜야 합니다. 그래야만 페이지 단위로 발생한 데이터를 수집할 수 있습니다.
5. **매치 유형 설정**
   - 설정한 매치 유형이 제한적으로 데이터를 수집하도록 설정되어 있는지 검토하세요. [매치 유형 설정 가이드](https://forum.beusable.net/ko/solomon/post/732)를 참고하여 설정을 확인하세요.
6. **리포트 상태 확인**
   - 리포트가 분석 종료, 일시정지, 정지 상태라면 데이터를 수집하지 않으므로, 리포트 상태를 확인하고 필요 시 새로 등록하거나 PV 충전 혹은 플랜 갱신이 필요합니다.
7. **URL 슬래시 또는 www 확인**
    - URL 뒤에 슬래시(/) 또는 www 포함 여부를 확인하세요. 도메인은 슬래시 여부가 무방하지만, Path는 슬래시 여부를 체크합니다. 그리고 일부 매치유형의 경우 www 유무에 따라 수집 범위가 상이합니다.

위의 방법들을 모두 확인하신 후에도 문제가 해결되지 않는다면, 뷰저블의 CX 팀에 문의해 주세요. 추가적인 지원이 필요하실 경우, 뷰저블 운영팀의 이메일 주소는 [beusable@4grit.com](mailto:beusable@4grit.com)입니다.

다른 궁금하신 사항이 또 있으실까요?"""


# error answer
NOT_SCHEMA_URL_KR = """Beusable AI : GEO는 무료 진단용 챗봇입니다.\n스키마 무료 진단을 위한 URL만 정확히 입력해 주세요."""
NOT_SCHEMA_URL_EN = """Beusable AI : GEO is a free diagnostic chatbot.\nPlease enter only the URL for the free schema diagnosis."""
NOT_SCHEMA_URL_JP = """Beusable AI : GEOは無料診断用のチャットボットです。\nスキーマ無料診断のためのURLのみを正確に入力してください。"""
ERR_REPORT_CHAT_KR = "인증이 만료되었습니다. 레포트창을 껐다가 다시 열어주세요. 만약, 창을 껐다 켰는데도 계속 같은 메세지를 받으신다면 담당자에게 문의주시면 신속히 도와드리겠습니다. 감사합니다."
ERR_REPORT_CHAT_EN = "Your session has expired. Please close and reopen the report window. If you continue to see this message after reopening, please contact the administrator for assistance. Thank you."
ERR_REPORT_CHAT_JA = "認証が期限切れになりました。レポート画面を閉じてから再度開いてください。もし、画面を閉じて開き直しても同じメッセージが表示される場合は、担当者にお問い合わせいただければ迅速に対応させていただきます。ありがとうございます。"


# OPERATION CONSTANTS
RESULT = "result"
PROMPT = "prompt"
QUERY = "query"
REFER = "refer"
CHAT_KIND_HISTORY_LIST = [RESULT]
PROM_KIND_HISTORY_LIST = [PROMPT, QUERY]
REFER_KIND_HISTROY_LIST = [REFER]
QUERY_CATEGORY_PROMPT_LIST = []
QUERY_CHAT_CATEGORY_LIST = [MAIN, CS]

# JWT CONSTANTS
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 3
REFRESH_TOKEN_EXPIRE_DAYS = 7

# S3 CONSTANTS
BA_AWS_BUCKET_NAME = 'beusable-ai-report'

# sample data
DASHBOARD_SAMPLE = """{
    "traffic": [
        {
            "dt": "2026-01-30",
            "pv": 496,
            "session": 388,
            "initSessCnt": 387
        },
        {
            "dt": "2026-01-31",
            "pv": 483,
            "session": 431,
            "initSessCnt": 431
        },
        {
            "dt": "2026-02-01",
            "pv": 550,
            "session": 502,
            "initSessCnt": 502
        },
        {
            "dt": "2026-02-02",
            "pv": 1090,
            "session": 679,
            "initSessCnt": 679
        },
        {
            "dt": "2026-02-03",
            "pv": 762,
            "session": 388,
            "initSessCnt": 388
        },
        {
            "dt": "2026-02-04",
            "pv": 566,
            "session": 378,
            "initSessCnt": 378
        },
        {
            "dt": "2026-02-05",
            "pv": 174,
            "session": 129,
            "initSessCnt": 129
        }
    ],
    "session": {
        "total": {
            "totalPv": 4121,
            "intervalSum": 148516627,
            "sessionSum": 2894,
            "pvPerSession": 1.424,
            "intvlPerSession": 51318.8068,
            "avgInterval": 121139.17373572594
        },
        "daily": {
            "2026-01-30": {
                "totalPv": 496,
                "intervalSum": 6892008,
                "sessionSum": 387,
                "pvPerSession": 1.2817,
                "intvlPerSession": 17808.8062,
                "avgInterval": 63814.88888888889
            },
            "2026-01-31": {
                "totalPv": 483,
                "intervalSum": 4100878,
                "sessionSum": 431,
                "pvPerSession": 1.1206,
                "intvlPerSession": 9514.7981,
                "avgInterval": 78863.03846153847
            },
            "2026-02-01": {
                "totalPv": 550,
                "intervalSum": 4253160,
                "sessionSum": 502,
                "pvPerSession": 1.0956,
                "intvlPerSession": 8472.4303,
                "avgInterval": 88607.5
            },
            "2026-02-02": {
                "totalPv": 1090,
                "intervalSum": 42967220,
                "sessionSum": 679,
                "pvPerSession": 1.6053,
                "intvlPerSession": 63280.1473,
                "avgInterval": 104543.11435523114
            },
            "2026-02-03": {
                "totalPv": 762,
                "intervalSum": 48602496,
                "sessionSum": 388,
                "pvPerSession": 1.9639,
                "intvlPerSession": 125264.1649,
                "avgInterval": 129953.19786096257
            },
            "2026-02-04": {
                "totalPv": 566,
                "intervalSum": 33161972,
                "sessionSum": 378,
                "pvPerSession": 1.4974,
                "intvlPerSession": 87730.0847,
                "avgInterval": 176393.46808510637
            },
            "2026-02-05": {
                "totalPv": 174,
                "intervalSum": 8538893,
                "sessionSum": 129,
                "pvPerSession": 1.3488,
                "intvlPerSession": 66192.969,
                "avgInterval": 189753.17777777778
            }
        }
    },
    "geo": [
        {
            "country": "KR",
            "countryFullname": "Korea",
            "count": 2544
        },
        {
            "country": "US",
            "countryFullname": "United States",
            "count": 201
        },
        {
            "country": "IE",
            "countryFullname": "Ireland",
            "count": 76
        },
        {
            "country": "VN",
            "countryFullname": "Vietnam",
            "count": 19
        },
        {
            "country": "SG",
            "countryFullname": "Singapore",
            "count": 10
        },
        {
            "country": "CA",
            "countryFullname": "Canada",
            "count": 6
        },
        {
            "country": "IN",
            "countryFullname": "India",
            "count": 5
        },
        {
            "country": "JP",
            "countryFullname": "Japan",
            "count": 5
        },
        {
            "country": "SE",
            "countryFullname": "Sweden",
            "count": 5
        },
        {
            "country": "TH",
            "countryFullname": "Thailand",
            "count": 4
        },
        {
            "country": "AU",
            "countryFullname": "Australia",
            "count": 2
        },
        {
            "country": "KH",
            "countryFullname": "Cambodia",
            "count": 2
        },
        {
            "country": "BD",
            "countryFullname": "Bangladesh",
            "count": 1
        },
        {
            "country": "HK",
            "countryFullname": "Hong Kong",
            "count": 1
        },
        {
            "country": "ID",
            "countryFullname": "Indonesia",
            "count": 1
        },
        {
            "country": "IL",
            "countryFullname": "Israel",
            "count": 1
        },
        {
            "country": "MY",
            "countryFullname": "Malaysia",
            "count": 1
        },
        {
            "country": "NP",
            "countryFullname": "Nepal",
            "count": 1
        },
        {
            "country": "PH",
            "countryFullname": "Philippines",
            "count": 1
        },
        {
            "country": "PK",
            "countryFullname": "Pakistan",
            "count": 1
        },
        {
            "country": "PT",
            "countryFullname": "Portugal",
            "count": 1
        },
        {
            "country": "RU",
            "countryFullname": "Russia",
            "count": 1
        }
    ],
    "exist": {
        "total": {
            "revisit": 462,
            "new": 2433
        },
        "daily": {
            "2026-01-30": {
                "revisit": 70,
                "new": 317
            },
            "2026-01-31": {
                "revisit": 61,
                "new": 370
            },
            "2026-02-01": {
                "revisit": 55,
                "new": 447
            },
            "2026-02-02": {
                "revisit": 91,
                "new": 588
            },
            "2026-02-03": {
                "revisit": 93,
                "new": 296
            },
            "2026-02-04": {
                "revisit": 72,
                "new": 306
            },
            "2026-02-05": {
                "revisit": 20,
                "new": 109
            }
        },
        "cache": false
    },
    "refer": {
        "total": [
            {
                "Direct": 1226
            },
            {
                "m.facebook.com": 1052
            },
            {
                "instagram.com": 382
            },
            {
                "www.facebook.com": 62
            },
            {
                "www.google.com": 40
            },
            {
                "l.facebook.com": 31
            },
            {
                "search.naver.com": 23
            },
            {
                "m.search.naver.com": 12
            },
            {
                "ad-creative.gfa.naver.com/widget/*": 11
            },
            {
                "staging-orders.monki.net/tableorder": 7
            }
        ],
        "daily": {
            "2026-01-30": [
                {
                    "Direct": 163
                },
                {
                    "m.facebook.com": 113
                },
                {
                    "instagram.com": 82
                },
                {
                    "www.google.com": 7
                },
                {
                    "www.facebook.com": 0
                }
            ],
            "2026-01-31": [
                {
                    "Direct": 212
                },
                {
                    "m.facebook.com": 122
                },
                {
                    "instagram.com": 89
                },
                {
                    "www.facebook.com": 1
                },
                {
                    "www.google.com": 0
                }
            ],
            "2026-02-01": [
                {
                    "Direct": 248
                },
                {
                    "m.facebook.com": 168
                },
                {
                    "instagram.com": 77
                },
                {
                    "www.facebook.com": 0
                },
                {
                    "www.google.com": 0
                }
            ],
            "2026-02-02": [
                {
                    "m.facebook.com": 332
                },
                {
                    "Direct": 215
                },
                {
                    "www.facebook.com": 55
                },
                {
                    "instagram.com": 42
                },
                {
                    "www.google.com": 10
                }
            ],
            "2026-02-03": [
                {
                    "Direct": 175
                },
                {
                    "m.facebook.com": 125
                },
                {
                    "instagram.com": 39
                },
                {
                    "www.google.com": 15
                },
                {
                    "www.facebook.com": 0
                }
            ],
            "2026-02-04": [
                {
                    "Direct": 163
                },
                {
                    "m.facebook.com": 142
                },
                {
                    "instagram.com": 39
                },
                {
                    "www.google.com": 8
                },
                {
                    "www.facebook.com": 1
                }
            ],
            "2026-02-05": [
                {
                    "Direct": 50
                },
                {
                    "m.facebook.com": 50
                },
                {
                    "instagram.com": 14
                },
                {
                    "www.facebook.com": 5
                },
                {
                    "www.google.com": 0
                }
            ]
        },
        "cache": false
    },
    "pvTopData": {
        "dropOff": {
            "avg": 70.38,
            "max": 97.2,
            "min": 0
        },
        "reload": {
            "avg": 7.81,
            "max": 66.67,
            "min": 0
        },
        "rollback": {
            "avg": 0.71,
            "max": 25,
            "min": 0
        },
        "interval": {
            "avg": 123061.58,
            "max": 1800000,
            "min": 9190
        }
    },
    "pvTopList": [
        {
            "subDomSid": "f715b5f64f",
            "urlId": 20,
            "gUrlId": 31,
            "url": "https://orders.monki.net/tableorder?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch&utm_term={query}&utm_content=news",
            "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1474,
            "dropOff": 1047,
            "rollback": 6,
            "stayInCount": 427,
            "reloadCount": 150,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 127075.981264637,
            "baApply": null,
            "listUrl": "orders.monki.net/tableorder"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 1,
            "gUrlId": 2,
            "url": "https://orders.monki.net/mktableorder_landing?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch_tenant&utm_term=먼키&utm_content=mainimage_tableorder&n_media=27758&n_query=먼키&n_rank=1&n_ad_group=grp-a001-04-000000041822398&n_ad=nad-a001-04-000000327818590&n_keyword_id=nkw-a001-04-000006182226415&n_keyword=먼키&n_campaign_type=4&n_contract=tct-a001-04-000000001011996&n_ad_group_type=5&NaPm=ct=m4rrwvrk|ci=0yC00002Ok1ByS6rTvpx|tr=brnd|hk=ed562c083bdc05219629ed8080b0d0ca9d5d1b5b|nacn=87DQBUAZ05AN",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "purchase",
            "AICategory2": [
                "cta",
                "form"
            ],
            "count": 1036,
            "dropOff": 1007,
            "rollback": 0,
            "stayInCount": 29,
            "reloadCount": 18,
            "tagInfo": {
                "1": {
                    "colorHex": "#e8b600",
                    "tagName": "orders.monki.net > mktableorder_landing",
                    "tagId": 1
                }
            },
            "avgStay": 146550,
            "baApply": null,
            "listUrl": "orders.monki.net/mktableorder_landing"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 3,
            "gUrlId": 4,
            "url": "https://orders.monki.net/",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "cta",
                "form"
            ],
            "count": 392,
            "dropOff": 142,
            "rollback": 10,
            "stayInCount": 250,
            "reloadCount": 36,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 87331.236,
            "baApply": null,
            "listUrl": "orders.monki.net/"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 4,
            "gUrlId": 5,
            "url": "https://orders.monki.net/mktableorder",
            "title": "테이블오더 먼키오더 | 무약정 · AI 고객 맞춤 홍보로 단골·매출 상승",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "cta",
                "form"
            ],
            "count": 288,
            "dropOff": 217,
            "rollback": 1,
            "stayInCount": 71,
            "reloadCount": 26,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 126126.87323943662,
            "baApply": null,
            "listUrl": "orders.monki.net/mktableorder"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 21,
            "gUrlId": 36,
            "url": "https://orders.monki.net/aisellup?utm_source=meta&utm_medium=display&utm_campaign=Meta_테이블오더(무약정)_잠재고객_Lv2_251002&utm_content=NON_25&fbclid=IwZXh0bgNhZW0CMTEAc3J0YwZhcHBfaWQMMjU2MjgxMDQwNTU4AAEe_0L3WyFROcJY1rWaOlvCyjvhNDsPInlpteXPBP668FiYmXlUqnoKC0p4R80_aem_HnlSh7PjENvRTikW2J2kJA",
            "title": "먼키 AI 매출UP | 매출 올려주는 매장 운영 자동화 AI CRM",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 276,
            "dropOff": 154,
            "rollback": 3,
            "stayInCount": 122,
            "reloadCount": 13,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 74466.77868852459,
            "baApply": null,
            "listUrl": "orders.monki.net/aisellup"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 18,
            "gUrlId": 19,
            "url": "https://orders.monki.net/crm",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "pricing",
            "AICategory2": [
                "cta",
                "form"
            ],
            "count": 248,
            "dropOff": 234,
            "rollback": 0,
            "stayInCount": 14,
            "reloadCount": 5,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 54109.42857142857,
            "baApply": null,
            "listUrl": "orders.monki.net/crm"
        },
        {
            "subDomSid": "497a1fe1fd",
            "urlId": 2,
            "gUrlId": 24,
            "url": "https://staging-orders.monki.net/tableorder",
            "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "pricing",
            "AICategory2": [
                "main",
                "cta",
                "detail"
            ],
            "count": 117,
            "dropOff": 22,
            "rollback": 4,
            "stayInCount": 95,
            "reloadCount": 36,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 228849.4842105263,
            "baApply": null,
            "listUrl": "staging-orders.monki.net/tableorder"
        },
        {
            "subDomSid": "497a1fe1fd",
            "urlId": 1,
            "gUrlId": 23,
            "url": "https://staging-orders.monki.net/",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "cta"
            ],
            "count": 80,
            "dropOff": 13,
            "rollback": 2,
            "stayInCount": 67,
            "reloadCount": 17,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 145524.14925373133,
            "baApply": null,
            "listUrl": "staging-orders.monki.net/"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 19,
            "gUrlId": 20,
            "url": "https://orders.monki.net/ai-sellup",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "pricing",
            "AICategory2": [
                "main",
                "cta",
                "form"
            ],
            "count": 62,
            "dropOff": 29,
            "rollback": 2,
            "stayInCount": 33,
            "reloadCount": 7,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 26466.696969696968,
            "baApply": null,
            "listUrl": "orders.monki.net/ai-sellup"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 22,
            "gUrlId": 37,
            "url": "https://orders.monki.net/support",
            "title": "먼키오더 고객지원 | 365일 운영·온보딩 지원",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 40,
            "dropOff": 8,
            "rollback": 0,
            "stayInCount": 32,
            "reloadCount": 3,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 52661.28125,
            "baApply": null,
            "listUrl": "orders.monki.net/support"
        },
        {
            "subDomSid": "497a1fe1fd",
            "urlId": 3,
            "gUrlId": 25,
            "url": "https://staging-orders.monki.net/aisellup",
            "title": "먼키 AI 매출UP | 매출 올려주는 똑똑한 AI 매니저",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 29,
            "dropOff": 2,
            "rollback": 0,
            "stayInCount": 27,
            "reloadCount": 2,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 134145.62962962964,
            "baApply": null,
            "listUrl": "staging-orders.monki.net/aisellup"
        },
        {
            "subDomSid": "8cecae7430",
            "urlId": 2,
            "gUrlId": 28,
            "url": "https://orders-eks.monki.net/tableorder",
            "title": "먼키 AI 오더 | 국내 최초 무약정 AI 테이블오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "cta"
            ],
            "count": 11,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 11,
            "reloadCount": 3,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 112101.63636363637,
            "baApply": null,
            "listUrl": "orders-eks.monki.net/tableorder"
        },
        {
            "subDomSid": "497a1fe1fd",
            "urlId": 4,
            "gUrlId": 26,
            "url": "https://staging-orders.monki.net/support",
            "title": "먼키오더 고객지원 | 365일 운영·온보딩 지원",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 11,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 10,
            "reloadCount": 1,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 89434.7,
            "baApply": null,
            "listUrl": "staging-orders.monki.net/support"
        },
        {
            "subDomSid": "8cecae7430",
            "urlId": 3,
            "gUrlId": 29,
            "url": "https://orders-eks.monki.net/aisellup",
            "title": "먼키 AI 매출UP | 매출 올려주는 똑똑한 AI 매니저",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 8,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 8,
            "reloadCount": 1,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 245699.125,
            "baApply": null,
            "listUrl": "orders-eks.monki.net/aisellup"
        },
        {
            "subDomSid": "8cecae7430",
            "urlId": 1,
            "gUrlId": 27,
            "url": "https://orders-eks.monki.net/",
            "title": "먼키 AI | AI 매장 운영 자동화 솔루션",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "cta"
            ],
            "count": 8,
            "dropOff": 3,
            "rollback": 0,
            "stayInCount": 5,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 340715.4,
            "baApply": null,
            "listUrl": "orders-eks.monki.net/"
        },
        {
            "subDomSid": "fad7b03fd7",
            "urlId": 1,
            "gUrlId": 38,
            "url": "https://orders-backup.monki.net/",
            "title": "먼키 테이블오더 – 완전무선 테이블 오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 5,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 4,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 364928,
            "baApply": null,
            "listUrl": "orders-backup.monki.net/"
        },
        {
            "subDomSid": "b0c8609af9",
            "urlId": 1,
            "gUrlId": 32,
            "url": "https://orders2.monki.net/",
            "title": "먼키오더 | 테이블오더·AI 매출UP 기반 매장 자동화 솔루션",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 4,
            "dropOff": 0,
            "rollback": 1,
            "stayInCount": 4,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 9190,
            "baApply": null,
            "listUrl": "orders2.monki.net/"
        },
        {
            "subDomSid": "497a1fe1fd",
            "urlId": 6,
            "gUrlId": 47,
            "url": "https://staging-orders.monki.net/sitemap",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 3,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 2,
            "reloadCount": 2,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 123730,
            "baApply": null,
            "listUrl": "staging-orders.monki.net/sitemap"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 8,
            "gUrlId": 9,
            "url": "https://orders.monki.net/pos/landing",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "list",
                "cta",
                "form"
            ],
            "count": 3,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 2,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 14817.5,
            "baApply": null,
            "listUrl": "orders.monki.net/pos/landing"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 25,
            "gUrlId": 41,
            "url": "https://orders.monki.net/robots.txt",
            "title": "먼키 AI | AI 매장 운영 자동화 솔루션",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 3,
            "dropOff": 2,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/robots.txt"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 12,
            "gUrlId": 13,
            "url": "https://orders.monki.net/kiosk",
            "title": "먼키 테이블오더 – 완전무선 테이블 오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "list",
                "cta"
            ],
            "count": 3,
            "dropOff": 2,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 5693,
            "baApply": null,
            "listUrl": "orders.monki.net/kiosk"
        },
        {
            "subDomSid": "fad7b03fd7",
            "urlId": 2,
            "gUrlId": 43,
            "url": "https://orders-backup.monki.net/mktableorder",
            "title": "테이블오더 먼키오더 | 무약정 · AI 고객 맞춤 홍보로 단골·매출 상승",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 2,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 2,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 912895,
            "baApply": null,
            "listUrl": "orders-backup.monki.net/mktableorder"
        },
        {
            "subDomSid": "b0c8609af9",
            "urlId": 2,
            "gUrlId": 33,
            "url": "https://orders2.monki.net/tableorder",
            "title": "먼키 AI 오더 | 국내 최초 무약정 AI 테이블오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 2,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 2,
            "reloadCount": 1,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 4484.5,
            "baApply": null,
            "listUrl": "orders2.monki.net/tableorder"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 24,
            "gUrlId": 40,
            "url": "https://orders.monki.net/sitemap.xml",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 2,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 219578,
            "baApply": null,
            "listUrl": "orders.monki.net/sitemap.xml"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 10,
            "gUrlId": 11,
            "url": "https://orders.monki.net/cat/landing",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "pricing",
            "AICategory2": [
                "main",
                "list",
                "cta",
                "form"
            ],
            "count": 2,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 8770,
            "baApply": null,
            "listUrl": "orders.monki.net/cat/landing"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 7,
            "gUrlId": 8,
            "url": "https://orders.monki.net/kiosk/landing",
            "title": "먼키 테이블오더 – 완전무선 테이블 오더",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "cta",
                "form"
            ],
            "count": 2,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 8252,
            "baApply": null,
            "listUrl": "orders.monki.net/kiosk/landing"
        },
        {
            "subDomSid": "b0c8609af9",
            "urlId": 4,
            "gUrlId": 35,
            "url": "https://orders2.monki.net/support",
            "title": "먼키오더 | 고객지원센터 365일 운영",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 214618,
            "baApply": null,
            "listUrl": "orders2.monki.net/support"
        },
        {
            "subDomSid": "8cecae7430",
            "urlId": 4,
            "gUrlId": 30,
            "url": "https://orders-eks.monki.net/support",
            "title": "먼키오더 | 고객지원센터 365일 운영",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 36933,
            "baApply": null,
            "listUrl": "orders-eks.monki.net/support"
        },
        {
            "subDomSid": "497a1fe1fd",
            "urlId": 5,
            "gUrlId": 46,
            "url": "https://staging-orders.monki.net/sitemap.xml",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 3182,
            "baApply": null,
            "listUrl": "staging-orders.monki.net/sitemap.xml"
        },
        {
            "subDomSid": "b0c8609af9",
            "urlId": 3,
            "gUrlId": 34,
            "url": "https://orders2.monki.net/aisellup",
            "title": "먼키 AI 매출UP | 매출 올려주는 똑똑한 AI 매니저",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 0,
            "rollback": 0,
            "stayInCount": 1,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1637,
            "baApply": null,
            "listUrl": "orders2.monki.net/aisellup"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 5,
            "gUrlId": 6,
            "url": "https://orders.monki.net/company",
            "title": "먼키 AI | AI 매장 운영 자동화 솔루션",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "main",
            "AICategory2": [
                "main",
                "info"
            ],
            "count": 1,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 0,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/company"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 13,
            "gUrlId": 14,
            "url": "https://orders.monki.net/event?utm_source=meta&utm_medium=display&utm_campaign=Meta_프로모션_트래픽_LV1(단일)&utm_content=AD+&utm_term=이미지_프로모션_혜택(홍보영상)&fbclid=IwZXh0bgNhZW0BMABhZGlkAaseFJTmJsMBHeQLJcWHmb2J11c5bgv1SBVLJGm4b-gLE1iEjI60V92Y_r_7lNfAtLxAMg_aem_E2zVqiV2URf-feySoDOC5Q&utm_id=120222872839680483",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "event",
            "AICategory2": [
                "list",
                "detail",
                "cta",
                "form"
            ],
            "count": 1,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 0,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/event"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 23,
            "gUrlId": 39,
            "url": "https://orders.monki.net/favicon.ico",
            "title": "먼키 AI | AI 매장 운영 자동화 솔루션",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 0,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/favicon.ico"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 26,
            "gUrlId": 42,
            "url": "https://orders.monki.net/naverc14010b9ab3fa759db5001cbd7f717eb.html",
            "title": "먼키 AI | AI 매장 운영 자동화 솔루션",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 0,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/naverc14010b9ab3fa759db5001cbd7f717eb.html"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 27,
            "gUrlId": 44,
            "url": "https://orders.monki.net/static/assets/mkorders/kor/images/tableorder/mk_video.mp4",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 0,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/static/assets/mkorders/kor/images/tableorder/mk_video.mp4"
        },
        {
            "subDomSid": "f715b5f64f",
            "urlId": 28,
            "gUrlId": 45,
            "url": "https://orders.monki.net/mktab",
            "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
            "customId": null,
            "customValue": null,
            "customColor": null,
            "bookmark": false,
            "AICategory1": "",
            "AICategory2": [],
            "count": 1,
            "dropOff": 1,
            "rollback": 0,
            "stayInCount": 0,
            "reloadCount": 0,
            "tagInfo": {
                "1": {
                    "colorHex": null,
                    "tagName": null,
                    "tagId": -1
                }
            },
            "avgStay": 1800000,
            "baApply": null,
            "listUrl": "orders.monki.net/mktab"
        }
    ],
    "trend": [
        {
            "seq": 0,
            "seqSessCnt": 2894,
            "rank1Node": {
                "nodeId": 2,
                "gUrlId": 2,
                "sessCnt": 1014,
                "urlCount": 1030,
                "nodeMeta": {
                    "baApply": null,
                    "dom": "orders.monki.net",
                    "path": "/mktableorder_landing",
                    "url": "https://orders.monki.net/mktableorder_landing?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch_tenant&utm_term=먼키&utm_content=mainimage_tableorder&n_media=27758&n_query=먼키&n_rank=1&n_ad_group=grp-a001-04-000000041822398&n_ad=nad-a001-04-000000327818590&n_keyword_id=nkw-a001-04-000006182226415&n_keyword=먼키&n_campaign_type=4&n_contract=tct-a001-04-000000001011996&n_ad_group_type=5&NaPm=ct=m4rrwvrk|ci=0yC00002Ok1ByS6rTvpx|tr=brnd|hk=ed562c083bdc05219629ed8080b0d0ca9d5d1b5b|nacn=87DQBUAZ05AN",
                    "title": "먼키AI | 먼키AI오더 테이블오더·AI 매출UP",
                    "tagInfo": {
                        "1": {
                            "colorHex": "#e8b600",
                            "tagName": "orders.monki.net > mktableorder_landing",
                            "tagId": 1
                        }
                    },
                    "bookmark": false,
                    "AICategory1": "purchase",
                    "AICategory2": [
                        "cta",
                        "form"
                    ]
                }
            }
        },
        {
            "seq": 1,
            "seqSessCnt": 248,
            "rank1Node": {
                "nodeId": 31,
                "gUrlId": 31,
                "sessCnt": 105,
                "urlCount": 142,
                "nodeMeta": {
                    "baApply": null,
                    "dom": "orders.monki.net",
                    "path": "/tableorder",
                    "url": "https://orders.monki.net/tableorder?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch&utm_term={query}&utm_content=news",
                    "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
                    "tagInfo": {
                        "1": {
                            "colorHex": null,
                            "tagName": null,
                            "tagId": -1
                        }
                    },
                    "bookmark": false,
                    "AICategory1": "",
                    "AICategory2": []
                }
            }
        },
        {
            "seq": 2,
            "seqSessCnt": 142,
            "rank1Node": {
                "nodeId": 31,
                "gUrlId": 31,
                "sessCnt": 54,
                "urlCount": 66,
                "nodeMeta": {
                    "baApply": null,
                    "dom": "orders.monki.net",
                    "path": "/tableorder",
                    "url": "https://orders.monki.net/tableorder?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch&utm_term={query}&utm_content=news",
                    "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
                    "tagInfo": {
                        "1": {
                            "colorHex": null,
                            "tagName": null,
                            "tagId": -1
                        }
                    },
                    "bookmark": false,
                    "AICategory1": "",
                    "AICategory2": []
                }
            }
        },
        {
            "seq": 3,
            "seqSessCnt": 82,
            "rank1Node": {
                "nodeId": 31,
                "gUrlId": 31,
                "sessCnt": 24,
                "urlCount": 29,
                "nodeMeta": {
                    "baApply": null,
                    "dom": "orders.monki.net",
                    "path": "/tableorder",
                    "url": "https://orders.monki.net/tableorder?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch&utm_term={query}&utm_content=news",
                    "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
                    "tagInfo": {
                        "1": {
                            "colorHex": null,
                            "tagName": null,
                            "tagId": -1
                        }
                    },
                    "bookmark": false,
                    "AICategory1": "",
                    "AICategory2": []
                }
            }
        },
        {
            "seq": 4,
            "seqSessCnt": 60,
            "rank1Node": {
                "nodeId": 31,
                "gUrlId": 31,
                "sessCnt": 17,
                "urlCount": 23,
                "nodeMeta": {
                    "baApply": null,
                    "dom": "orders.monki.net",
                    "path": "/tableorder",
                    "url": "https://orders.monki.net/tableorder?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch&utm_term={query}&utm_content=news",
                    "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
                    "tagInfo": {
                        "1": {
                            "colorHex": null,
                            "tagName": null,
                            "tagId": -1
                        }
                    },
                    "bookmark": false,
                    "AICategory1": "",
                    "AICategory2": []
                }
            }
        },
        {
            "seq": 5,
            "seqSessCnt": 47,
            "rank1Node": {
                "nodeId": 31,
                "gUrlId": 31,
                "sessCnt": 20,
                "urlCount": 27,
                "nodeMeta": {
                    "baApply": null,
                    "dom": "orders.monki.net",
                    "path": "/tableorder",
                    "url": "https://orders.monki.net/tableorder?utm_source=naver&utm_medium=cpc&utm_campaign=brandsearch&utm_term={query}&utm_content=news",
                    "title": "먼키오더 테이블오더 | 국내 최초 무약정 먼키AI오더",
                    "tagInfo": {
                        "1": {
                            "colorHex": null,
                            "tagName": null,
                            "tagId": -1
                        }
                    },
                    "bookmark": false,
                    "AICategory1": "",
                    "AICategory2": []
                }
            }
        }
    ],
    "device": {
        "session": 2895,
        "total": {
            "phone": 2593,
            "tablet": 51,
            "desktop": 251
        },
        "daily": {
            "2026-01-30": {
                "phone": 356,
                "tablet": 5,
                "desktop": 26
            },
            "2026-01-31": {
                "phone": 418,
                "tablet": 7,
                "desktop": 6
            },
            "2026-02-01": {
                "phone": 489,
                "tablet": 6,
                "desktop": 7
            },
            "2026-02-02": {
                "phone": 577,
                "tablet": 9,
                "desktop": 93
            },
            "2026-02-03": {
                "phone": 311,
                "tablet": 14,
                "desktop": 64
            },
            "2026-02-04": {
                "phone": 328,
                "tablet": 8,
                "desktop": 42
            },
            "2026-02-05": {
                "phone": 114,
                "tablet": 2,
                "desktop": 13
            }
        },
        "cache": false
    }
}"""


DASHBOARDGA_SAMPLE = """{
        "events": [
            {
                "__id": "1611210000000000|1605951.6059719725|page_view|-307340413",
                "event_date": 20210121,
                "event_timestamp": 1611210000000000,
                "event_name": "page_view",
                "user_pseudo_id": 1605951.6059719725,
                "traffic_medium": "(none)",
                "device_category": "mobile",
                "browser": "Safari",
                "device_detail": "mobile / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 13,
                    "debug_mode": 1,
                    "ga_session_number": 1,
                    "page_location": "https://www.googlemerchandisestore.com/",
                    "ga_session_id": 2725571477,
                    "session_engaged": 1,
                    "engaged_session_event": 1,
                    "page_title": "Google Online Store"
                },
                "ga_session_id": 2725571477
            },
            {
                "__id": "1611210000000000|1605951.6059719725|page_view|-311704457",
                "event_date": 20210121,
                "event_timestamp": 1611210000000000,
                "event_name": "page_view",
                "user_pseudo_id": 1605951.6059719725,
                "traffic_medium": "(none)",
                "device_category": "mobile",
                "browser": "Safari",
                "device_detail": "mobile / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "clean_event": "gtm.js",
                    "entrances": 1,
                    "session_engaged": 0,
                    "ga_session_id": 2725571477,
                    "page_title": "Google Online Store",
                    "engaged_session_event": 1,
                    "ga_session_number": 1,
                    "campaign": "(direct)",
                    "term": "<obfuscated>",
                    "debug_mode": 1,
                    "source": "(direct)",
                    "page_location": "https://www.googlemerchandisestore.com/",
                    "medium": "(none)"
                },
                "ga_session_id": 2725571477
            },
            {
                "__id": "1611960000000000|2163283.4364849087|view_promotion|-6653755973",
                "event_date": 20210129,
                "event_timestamp": 1611960000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 2163283.4364849087,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_number": 1,
                    "engagement_time_msec": 46,
                    "page_title": "Home",
                    "engaged_session_event": 1,
                    "debug_mode": 1,
                    "ga_session_id": 9278676056,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "session_engaged": 1
                },
                "ga_session_id": 9278676056
            },
            {
                "__id": "1609700000000000|3886972.1560030556|session_start|-6411002457",
                "event_date": 20210103,
                "event_timestamp": 1609700000000000,
                "event_name": "session_start",
                "user_pseudo_id": 3886972.1560030556,
                "traffic_medium": "<Other>",
                "device_category": "desktop",
                "browser": "Safari",
                "device_detail": "desktop / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel",
                    "ga_session_number": 1,
                    "ga_session_id": 4344470266,
                    "page_title": "Apparel | Google Merchandise Store",
                    "engaged_session_event": 1
                },
                "ga_session_id": 4344470266
            },
            {
                "__id": "1610550000000000|5057241.750802934|first_visit|1236656593",
                "event_date": 20210113,
                "event_timestamp": 1610550000000000,
                "event_name": "first_visit",
                "user_pseudo_id": 5057241.750802934,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel",
                    "engaged_session_event": 1,
                    "session_engaged": 1,
                    "page_title": "Apparel | Google Merchandise Store",
                    "ga_session_id": 9009371496,
                    "ga_session_number": 1
                },
                "ga_session_id": 9009371496
            },
            {
                "__id": "1610910000000000|6475141.654587744|page_view|-5200104759",
                "event_date": 20210117,
                "event_timestamp": 1610910000000000,
                "event_name": "page_view",
                "user_pseudo_id": 6475141.654587744,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Safari",
                "device_detail": "desktop / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "entrances": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/signin.html",
                    "debug_mode": 1,
                    "engaged_session_event": 1,
                    "ga_session_number": 1,
                    "ga_session_id": 9627797947,
                    "page_title": "The Google Merchandise Store - Log In",
                    "session_engaged": 0,
                    "clean_event": "gtm.js"
                },
                "ga_session_id": 9627797947
            },
            {
                "__id": "1610780000000000|7048148.009594872|user_engagement|-2956234537",
                "event_date": 20210116,
                "event_timestamp": 1610780000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 7048148.009594872,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "session_engaged": 0,
                    "medium": "referral",
                    "debug_mode": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/google+redesign/apparel/google+dino+game+tee",
                    "ga_session_number": 2,
                    "page_title": "Page Unavailable",
                    "source": "shop.googlemerchandisestore.com",
                    "campaign": "(referral)",
                    "ga_session_id": 2634310464
                },
                "ga_session_id": 2634310464
            },
            {
                "__id": "1612080000000000|11717984.943483878|session_start|-9705040760",
                "event_date": 20210131,
                "event_timestamp": 1612080000000000,
                "event_name": "session_start",
                "user_pseudo_id": 11717984.943483878,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_id": 1085011694,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel",
                    "page_title": "Apparel | Google Merchandise Store",
                    "ga_session_number": 1,
                    "engaged_session_event": 1
                },
                "ga_session_id": 1085011694
            },
            {
                "__id": "1610080000000000|30900021.323378697|view_promotion|-2904941205",
                "event_date": 20210108,
                "event_timestamp": 1610080000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 30900021.323378697,
                "traffic_medium": "(none)",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "session_engaged": 1,
                    "engagement_time_msec": 13,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "engaged_session_event": 1,
                    "page_title": "Home",
                    "debug_mode": 1,
                    "ga_session_number": 9,
                    "ga_session_id": 3003908783
                },
                "ga_session_id": 3003908783
            },
            {
                "__id": "1611880000000000|51332807.24462119|scroll|-6399212118",
                "event_date": 20210128,
                "event_timestamp": 1611880000000000,
                "event_name": "scroll",
                "user_pseudo_id": 51332807.24462119,
                "traffic_medium": "<Other>",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "source": "shop.googlemerchandisestore.com",
                    "engaged_session_event": 1,
                    "medium": "referral",
                    "page_referrer": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel?",
                    "ga_session_id": 6465097438,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel/Womens",
                    "page_title": "Womens | Apparel | Google Merchandise Store",
                    "debug_mode": 1,
                    "ga_session_number": 1,
                    "campaign": "(referral)",
                    "session_engaged": 1,
                    "percent_scrolled": 90,
                    "engagement_time_msec": 12285
                },
                "ga_session_id": 6465097438
            },
            {
                "__id": "1610900000000000|61031472.87103895|scroll|-2892981018",
                "event_date": 20210117,
                "event_timestamp": 1610900000000000,
                "event_name": "scroll",
                "user_pseudo_id": 61031472.87103895,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_number": 3,
                    "debug_mode": 1,
                    "ga_session_id": 1027719877,
                    "percent_scrolled": 90,
                    "session_engaged": 1,
                    "engagement_time_msec": 21145,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "engaged_session_event": 1,
                    "page_title": "Home"
                },
                "ga_session_id": 1027719877
            },
            {
                "__id": "1610870000000000|61031472.87103895|first_visit|7788820090",
                "event_date": 20210117,
                "event_timestamp": 1610870000000000,
                "event_name": "first_visit",
                "user_pseudo_id": 61031472.87103895,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "page_title": "Home",
                    "engaged_session_event": 1,
                    "session_engaged": 1,
                    "ga_session_id": 6832949273,
                    "ga_session_number": 1
                },
                "ga_session_id": 6832949273
            },
            {
                "__id": "1610870000000000|61031472.87103895|scroll|8772829560",
                "event_date": 20210117,
                "event_timestamp": 1610870000000000,
                "event_name": "scroll",
                "user_pseudo_id": 61031472.87103895,
                "traffic_medium": "(data deleted)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Stationery",
                    "engagement_time_msec": 19564,
                    "engaged_session_event": 1,
                    "percent_scrolled": 90,
                    "page_title": "Stationery | Google Merchandise Store",
                    "ga_session_id": 4609872843,
                    "page_referrer": "https://shop.googlemerchandisestore.com/Google+Redesign/Lifestyle?",
                    "ga_session_number": 2,
                    "debug_mode": 1,
                    "session_engaged": 1
                },
                "ga_session_id": 4609872843
            },
            {
                "__id": "1610900000000000|61031472.87103895|view_promotion|6686383341",
                "event_date": 20210117,
                "event_timestamp": 1610900000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 61031472.87103895,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "debug_mode": 1,
                    "page_title": "Home",
                    "ga_session_number": 3,
                    "session_engaged": 1,
                    "ga_session_id": 1027719877,
                    "engagement_time_msec": 72,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "engaged_session_event": 1
                },
                "ga_session_id": 1027719877
            },
            {
                "__id": "1610910000000000|73168181.25516365|first_visit|8371356105",
                "event_date": 20210117,
                "event_timestamp": 1610910000000000,
                "event_name": "first_visit",
                "user_pseudo_id": 73168181.25516365,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Safari",
                "device_detail": "desktop / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "engaged_session_event": 1,
                    "ga_session_id": 9604048120,
                    "page_title": "Home",
                    "page_location": "https://shop.googlemerchandisestore.com/store.html",
                    "session_engaged": 1,
                    "ga_session_number": 1
                },
                "ga_session_id": 9604048120
            },
            {
                "__id": "1610910000000000|73168181.25516365|session_start|8371356105",
                "event_date": 20210117,
                "event_timestamp": 1610910000000000,
                "event_name": "session_start",
                "user_pseudo_id": 73168181.25516365,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Safari",
                "device_detail": "desktop / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_number": 1,
                    "ga_session_id": 9604048120,
                    "page_location": "https://shop.googlemerchandisestore.com/store.html",
                    "engaged_session_event": 1,
                    "page_title": "Home"
                },
                "ga_session_id": 9604048120
            },
            {
                "__id": "1610490000000000|78087117.25633365|page_view|-3249182755",
                "event_date": 20210112,
                "event_timestamp": 1610490000000000,
                "event_name": "page_view",
                "user_pseudo_id": 78087117.25633365,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engaged_session_event": 1,
                    "page_title": "Google Chrome Dino Light Up Water Bottle",
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Google+Chrome+Dino+Light+Up+Water+Bottle",
                    "debug_mode": 1,
                    "session_engaged": 1,
                    "clean_event": "gtm.js",
                    "ga_session_number": 1,
                    "ga_session_id": 2556756031
                },
                "ga_session_id": 2556756031
            },
            {
                "__id": "1610490000000000|78087117.25633365|scroll|8291792353",
                "event_date": 20210112,
                "event_timestamp": 1610490000000000,
                "event_name": "scroll",
                "user_pseudo_id": 78087117.25633365,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Lifestyle/Drinkware",
                    "percent_scrolled": 90,
                    "debug_mode": 1,
                    "session_engaged": 1,
                    "engaged_session_event": 1,
                    "medium": "organic",
                    "source": "google",
                    "ga_session_number": 1,
                    "engagement_time_msec": 23100,
                    "page_referrer": "https://shop.googlemerchandisestore.com/Google+Redesign/Shop+by+Brand/Google?",
                    "campaign": "(organic)",
                    "page_title": "Drinkware | Lifestyle | Google Merchandise Store",
                    "ga_session_id": 2556756031
                },
                "ga_session_id": 2556756031
            },
            {
                "__id": "1611700000000000|1009676.4905193951|page_view|9448114128",
                "event_date": 20210126,
                "event_timestamp": 1611700000000000,
                "event_name": "page_view",
                "user_pseudo_id": 1009676.4905193951,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_id": 7808177356,
                    "engaged_session_event": 1,
                    "debug_mode": 1,
                    "engagement_time_msec": 5,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Bags",
                    "session_engaged": 1,
                    "page_title": "Page Unavailable",
                    "ga_session_number": 2
                },
                "ga_session_id": 7808177356
            },
            {
                "__id": "1611700000000000|1009676.4905193951|user_engagement|1548952687",
                "event_date": 20210126,
                "event_timestamp": 1611700000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 1009676.4905193951,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 1622,
                    "ga_session_id": 7808177356,
                    "debug_mode": 1,
                    "engaged_session_event": 1,
                    "page_title": "Page Unavailable",
                    "session_engaged": 1,
                    "ga_session_number": 2,
                    "page_location": "https://shop.googlemerchandisestore.com/google+redesign/apparel/google+womens+tee+fc+black"
                },
                "ga_session_id": 7808177356
            },
            {
                "__id": "1611710000000000|1009676.4905193951|view_promotion|3263207752",
                "event_date": 20210127,
                "event_timestamp": 1611710000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 1009676.4905193951,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "session_engaged": 1,
                    "engaged_session_event": 1,
                    "engagement_time_msec": 51,
                    "ga_session_number": 3,
                    "debug_mode": 1,
                    "ga_session_id": 571195322,
                    "page_title": "Home",
                    "page_location": "https://shop.googlemerchandisestore.com/"
                },
                "ga_session_id": 571195322
            },
            {
                "__id": "1610050000000000|1172211.4577928963|scroll|-3141672357",
                "event_date": 20210107,
                "event_timestamp": 1610050000000000,
                "event_name": "scroll",
                "user_pseudo_id": 1172211.4577928963,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engaged_session_event": 1,
                    "debug_mode": 1,
                    "ga_session_number": 1,
                    "page_referrer": "https://shop.googlemerchandisestore.com/register.html?",
                    "page_location": "https://shop.googlemerchandisestore.com/registersuccess.html",
                    "engagement_time_msec": 237,
                    "session_engaged": 1,
                    "percent_scrolled": 90,
                    "page_title": "The Google Merchandise Store - Log In",
                    "ga_session_id": 5815112154
                },
                "ga_session_id": 5815112154
            },
            {
                "__id": "1610440000000000|1235093.1800599373|scroll|-8586581006",
                "event_date": 20210112,
                "event_timestamp": 1610440000000000,
                "event_name": "scroll",
                "user_pseudo_id": 1235093.1800599373,
                "traffic_medium": "<Other>",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "debug_mode": 1,
                    "page_location": "https://googlemerchandisestore.com/",
                    "page_title": "Google Online Store",
                    "session_engaged": 1,
                    "engaged_session_event": 1,
                    "percent_scrolled": 90,
                    "ga_session_number": 1,
                    "ga_session_id": 1594094923,
                    "engagement_time_msec": 1373
                },
                "ga_session_id": 1594094923
            },
            {
                "__id": "1610700000000000|1580194.1306638243|scroll|-429085143",
                "event_date": 20210115,
                "event_timestamp": 1610700000000000,
                "event_name": "scroll",
                "user_pseudo_id": 1580194.1306638243,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 23930,
                    "page_referrer": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel?",
                    "engaged_session_event": 1,
                    "percent_scrolled": 90,
                    "page_title": "Bags | Lifestyle | Google Merchandise Store",
                    "ga_session_number": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Lifestyle/Bags",
                    "debug_mode": 1,
                    "session_engaged": 1,
                    "ga_session_id": 1882783048
                },
                "ga_session_id": 1882783048
            },
            {
                "__id": "1609620000000000|1621047.1809785713|session_start|-4446408852",
                "event_date": 20210102,
                "event_timestamp": 1609620000000000,
                "event_name": "session_start",
                "user_pseudo_id": 1621047.1809785713,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_title": "Google Online Store",
                    "ga_session_number": 1,
                    "page_location": "https://googlemerchandisestore.com/",
                    "engaged_session_event": 1,
                    "ga_session_id": 3823848748
                },
                "ga_session_id": 3823848748
            },
            {
                "__id": "1610530000000000|1708340.3854978106|user_engagement|7862834581",
                "event_date": 20210113,
                "event_timestamp": 1610530000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 1708340.3854978106,
                "traffic_medium": "referral",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_title": "Bags | Lifestyle | Google Merchandise Store",
                    "engagement_time_msec": 9145,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Lifestyle/Bags",
                    "engaged_session_event": 1,
                    "ga_session_id": 9813682590,
                    "source": "shop.googlemerchandisestore.com",
                    "debug_mode": 1,
                    "campaign": "(referral)",
                    "ga_session_number": 2,
                    "medium": "referral",
                    "session_engaged": 1
                },
                "ga_session_id": 9813682590
            },
            {
                "__id": "1610530000000000|1708340.3854978106|scroll|-7288217621",
                "event_date": 20210113,
                "event_timestamp": 1610530000000000,
                "event_name": "scroll",
                "user_pseudo_id": 1708340.3854978106,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "percent_scrolled": 90,
                    "session_engaged": 1,
                    "ga_session_number": 1,
                    "page_title": "Google Online Store",
                    "page_location": "https://googlemerchandisestore.com/",
                    "ga_session_id": 2449606776,
                    "debug_mode": 1,
                    "engagement_time_msec": 43,
                    "engaged_session_event": 1
                },
                "ga_session_id": 2449606776
            },
            {
                "__id": "1611310000000000|1865955.6072229585|page_view|1941546005",
                "event_date": 20210122,
                "event_timestamp": 1611310000000000,
                "event_name": "page_view",
                "user_pseudo_id": 1865955.6072229585,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_id": 2558933406,
                    "page_title": "Men's T-Shirts | Apparel | Google Merchandise Store",
                    "engaged_session_event": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel/Mens/Mens+T+Shirts",
                    "debug_mode": 1,
                    "campaign": "(organic)",
                    "engagement_time_msec": 4,
                    "medium": "organic",
                    "session_engaged": 1,
                    "ga_session_number": 1,
                    "source": "google",
                    "term": "<obfuscated>"
                },
                "ga_session_id": 2558933406
            },
            {
                "__id": "1611310000000000|1865955.6072229585|page_view|-2956879375",
                "event_date": 20210122,
                "event_timestamp": 1611310000000000,
                "event_name": "page_view",
                "user_pseudo_id": 1865955.6072229585,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "debug_mode": 1,
                    "session_engaged": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Campus+Collection",
                    "engaged_session_event": 1,
                    "ga_session_id": 2558933406,
                    "page_title": "Campus Collection | Google Merchandise Store",
                    "engagement_time_msec": 3,
                    "ga_session_number": 1
                },
                "ga_session_id": 2558933406
            },
            {
                "__id": "1611310000000000|1865955.6072229585|view_item|3197187060",
                "event_date": 20210122,
                "event_timestamp": 1611310000000000,
                "event_name": "view_item",
                "user_pseudo_id": 1865955.6072229585,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel/Mens/Mens+T+Shirts",
                    "debug_mode": 1,
                    "ga_session_id": 2558933406,
                    "page_title": "Men's T-Shirts | Apparel | Google Merchandise Store",
                    "ga_session_number": 1,
                    "engagement_time_msec": 502,
                    "session_engaged": 1,
                    "engaged_session_event": 1
                },
                "ga_session_id": 2558933406
            },
            {
                "__id": "1609570000000000|1989653.0310679977|session_start|-7745393035",
                "event_date": 20210102,
                "event_timestamp": 1609570000000000,
                "event_name": "session_start",
                "user_pseudo_id": 1989653.0310679977,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engaged_session_event": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel",
                    "ga_session_number": 1,
                    "ga_session_id": 6149139412,
                    "page_title": "Apparel | Google Merchandise Store"
                },
                "ga_session_id": 6149139412
            },
            {
                "__id": "1610450000000000|2093349.3276106748|page_view|5033289653",
                "event_date": 20210112,
                "event_timestamp": 1610450000000000,
                "event_name": "page_view",
                "user_pseudo_id": 2093349.3276106748,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "campaign": "Data Share Promo",
                    "medium": "affiliate",
                    "clean_event": "gtm.js",
                    "ga_session_id": 3659737217,
                    "session_engaged": 0,
                    "source": "Partners",
                    "engaged_session_event": 1,
                    "debug_mode": 1,
                    "ga_session_number": 3,
                    "page_title": "Home",
                    "entrances": 1
                },
                "ga_session_id": 3659737217
            },
            {
                "__id": "1611660000000000|2126401.40854538|page_view|2243610303",
                "event_date": 20210126,
                "event_timestamp": 1611660000000000,
                "event_name": "page_view",
                "user_pseudo_id": 2126401.40854538,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 6,
                    "ga_session_number": 2,
                    "engaged_session_event": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Shop+by+Brand/Google+Cloud",
                    "session_engaged": 1,
                    "debug_mode": 1,
                    "ga_session_id": 3426007513,
                    "page_title": "Google Cloud | Shop by Brand | Google Merchandise Store"
                },
                "ga_session_id": 3426007513
            },
            {
                "__id": "1611840000000000|2126401.40854538|scroll|6307239440",
                "event_date": 20210128,
                "event_timestamp": 1611840000000000,
                "event_name": "scroll",
                "user_pseudo_id": 2126401.40854538,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "percent_scrolled": 90,
                    "engagement_time_msec": 3865,
                    "page_title": "Home",
                    "page_location": "https://shop.googlemerchandisestore.com/store.html",
                    "debug_mode": 1,
                    "ga_session_number": 3,
                    "ga_session_id": 9157144569,
                    "engaged_session_event": 1,
                    "session_engaged": 1
                },
                "ga_session_id": 9157144569
            },
            {
                "__id": "1609920000000000|2219098.9178831126|view_promotion|-9056962888",
                "event_date": 20210106,
                "event_timestamp": 1609920000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 2219098.9178831126,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/store.html",
                    "ga_session_number": 1,
                    "session_engaged": 1,
                    "page_title": "Home",
                    "ga_session_id": 716804610,
                    "engaged_session_event": 1,
                    "page_referrer": "https://shop.googlemerchandisestore.com/registersuccess.html?",
                    "engagement_time_msec": 108,
                    "debug_mode": 1
                },
                "ga_session_id": 716804610
            },
            {
                "__id": "1611740000000000|2230905.7046198924|scroll|8949707093",
                "event_date": 20210127,
                "event_timestamp": 1611740000000000,
                "event_name": "scroll",
                "user_pseudo_id": 2230905.7046198924,
                "traffic_medium": "(none)",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "campaign": "(organic)",
                    "ga_session_id": 1109039738,
                    "term": "<obfuscated>",
                    "source": "google",
                    "debug_mode": 1,
                    "engagement_time_msec": 9216,
                    "engaged_session_event": 1,
                    "medium": "organic",
                    "ga_session_number": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "page_title": "Home",
                    "session_engaged": 1,
                    "percent_scrolled": 90
                },
                "ga_session_id": 1109039738
            },
            {
                "__id": "1611350000000000|2325507.2899863417|session_start|-3633593671",
                "event_date": 20210122,
                "event_timestamp": 1611350000000000,
                "event_name": "session_start",
                "user_pseudo_id": 2325507.2899863417,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_id": 5474366524,
                    "ga_session_number": 1,
                    "page_title": "YouTube | Shop by Brand | Google Merchandise Store",
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Shop+by+Brand/YouTube",
                    "engaged_session_event": 1
                },
                "ga_session_id": 5474366524
            },
            {
                "__id": "1611350000000000|2325507.2899863417|user_engagement|5415803729",
                "event_date": 20210122,
                "event_timestamp": 1611350000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 2325507.2899863417,
                "traffic_medium": "organic",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "session_engaged": 1,
                    "page_referrer": "https://shop.googlemerchandisestore.com/store.html?",
                    "source": "shop.googlemerchandisestore.com",
                    "page_title": "YouTube 25 oz Gear Cap Bottle Black",
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Drinkware/Youtube+25oz+gear+cap+bottle+black",
                    "engaged_session_event": 1,
                    "debug_mode": 1,
                    "medium": "referral",
                    "campaign": "(referral)",
                    "ga_session_id": 5474366524,
                    "engagement_time_msec": 49817,
                    "ga_session_number": 1
                },
                "ga_session_id": 5474366524
            },
            {
                "__id": "1610610000000000|2351306.620910962|user_engagement|8188584095",
                "event_date": 20210114,
                "event_timestamp": 1610610000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 2351306.620910962,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Safari",
                "device_detail": "mobile / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "campaign": "(organic)",
                    "page_location": "https://googlemerchandisestore.com/",
                    "debug_mode": 1,
                    "engagement_time_msec": 5641,
                    "engaged_session_event": 1,
                    "term": "<obfuscated>",
                    "ga_session_number": 1,
                    "page_title": "Google Online Store",
                    "medium": "organic",
                    "session_engaged": 1,
                    "source": "google",
                    "ga_session_id": 9622942430
                },
                "ga_session_id": 9622942430
            },
            {
                "__id": "1610610000000000|2351306.620910962|scroll|-6635522960",
                "event_date": 20210114,
                "event_timestamp": 1610610000000000,
                "event_name": "scroll",
                "user_pseudo_id": 2351306.620910962,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Safari",
                "device_detail": "mobile / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 761,
                    "session_engaged": 1,
                    "ga_session_number": 1,
                    "page_location": "https://googlemerchandisestore.com/",
                    "ga_session_id": 9622942430,
                    "percent_scrolled": 90,
                    "debug_mode": 1,
                    "engaged_session_event": 1,
                    "page_title": "Google Online Store"
                },
                "ga_session_id": 9622942430
            },
            {
                "__id": "1610980000000000|2384954.218745844|session_start|5870747255",
                "event_date": 20210118,
                "event_timestamp": 1610980000000000,
                "event_name": "session_start",
                "user_pseudo_id": 2384954.218745844,
                "traffic_medium": "<Other>",
                "device_category": "desktop",
                "browser": "Edge",
                "device_detail": "desktop / Edge",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_number": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel",
                    "engaged_session_event": 1,
                    "ga_session_id": 4533886078,
                    "page_title": "Apparel | Google Merchandise Store"
                },
                "ga_session_id": 4533886078
            },
            {
                "__id": "1609880000000000|2510026.345211138|select_promotion|-5114053075",
                "event_date": 20210105,
                "event_timestamp": 1609880000000000,
                "event_name": "select_promotion",
                "user_pseudo_id": 2510026.345211138,
                "traffic_medium": "referral",
                "device_category": "mobile",
                "browser": "<Other>",
                "device_detail": "mobile / <Other>",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 2,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "debug_mode": 1,
                    "session_engaged": 1,
                    "engaged_session_event": 1,
                    "ga_session_number": 1,
                    "page_title": "Home",
                    "ga_session_id": 9763169697
                },
                "ga_session_id": 9763169697
            },
            {
                "__id": "1609930000000000|2589768.439253248|first_visit|6782987357",
                "event_date": 20210106,
                "event_timestamp": 1609930000000000,
                "event_name": "first_visit",
                "user_pseudo_id": 2589768.439253248,
                "traffic_medium": "<Other>",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engaged_session_event": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Accessories/Google+See+no+hear+no+set",
                    "page_title": "Google See-No Hear-No Set",
                    "ga_session_id": 1372810478,
                    "session_engaged": 1,
                    "ga_session_number": 1
                },
                "ga_session_id": 1372810478
            },
            {
                "__id": "1610430000000000|2889241.838178414|view_item|-4974109382",
                "event_date": 20210112,
                "event_timestamp": 1610430000000000,
                "event_name": "view_item",
                "user_pseudo_id": 2889241.838178414,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 392,
                    "engaged_session_event": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Accessories/Android+Techie+3D+Framed+Art",
                    "ga_session_id": 5898277976,
                    "session_engaged": 1,
                    "ga_session_number": 1,
                    "debug_mode": 1,
                    "page_title": "Android Techie 3D Framed Art"
                },
                "ga_session_id": 5898277976
            },
            {
                "__id": "1610430000000000|2889241.838178414|first_visit|3875282035",
                "event_date": 20210112,
                "event_timestamp": 1610430000000000,
                "event_name": "first_visit",
                "user_pseudo_id": 2889241.838178414,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "ga_session_number": 1,
                    "page_title": "Android Iconic Notebook",
                    "ga_session_id": 5898277976,
                    "engaged_session_event": 1,
                    "session_engaged": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Office/Android+Iconic+Notebook"
                },
                "ga_session_id": 5898277976
            },
            {
                "__id": "1610430000000000|2889241.838178414|view_item|-9435026179",
                "event_date": 20210112,
                "event_timestamp": 1610430000000000,
                "event_name": "view_item",
                "user_pseudo_id": 2889241.838178414,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_title": "Google Campus Bike Carry Pouch",
                    "session_engaged": 1,
                    "debug_mode": 1,
                    "engagement_time_msec": 770,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Bags/Google+Google+Campus+Bike+Carry+Pouch",
                    "ga_session_id": 5898277976,
                    "ga_session_number": 1,
                    "engaged_session_event": 1
                },
                "ga_session_id": 5898277976
            },
            {
                "__id": "1610430000000000|2889241.838178414|page_view|3306541317",
                "event_date": 20210112,
                "event_timestamp": 1610430000000000,
                "event_name": "page_view",
                "user_pseudo_id": 2889241.838178414,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "session_engaged": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Office/Google+Recycled+Writing+Set",
                    "engaged_session_event": 1,
                    "ga_session_id": 5898277976,
                    "clean_event": "gtm.js",
                    "ga_session_number": 1,
                    "page_title": "Google Recycled Writing Set",
                    "debug_mode": 1
                },
                "ga_session_id": 5898277976
            },
            {
                "__id": "1611600000000000|3531543.061725483|view_promotion|-3952606910",
                "event_date": 20210125,
                "event_timestamp": 1611600000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 3531543.061725483,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Safari",
                "device_detail": "mobile / Safari",
                "event_value_in_usd": 0,
                "params": {
                    "page_title": "Home",
                    "ga_session_id": 3702926601,
                    "session_engaged": 1,
                    "debug_mode": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "engaged_session_event": 1,
                    "ga_session_number": 1,
                    "engagement_time_msec": 83
                },
                "ga_session_id": 3702926601
            },
            {
                "__id": "1610970000000000|4011791.2269121925|view_promotion|-38960471",
                "event_date": 20210118,
                "event_timestamp": 1610970000000000,
                "event_name": "view_promotion",
                "user_pseudo_id": 4011791.2269121925,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engagement_time_msec": 196,
                    "ga_session_number": 2,
                    "engaged_session_event": 1,
                    "page_title": "Home",
                    "session_engaged": 1,
                    "ga_session_id": 2175581168,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "debug_mode": 1
                },
                "ga_session_id": 2175581168
            },
            {
                "__id": "1609670000000000|4239675.220679819|page_view|-6268452253",
                "event_date": 20210103,
                "event_timestamp": 1609670000000000,
                "event_name": "page_view",
                "user_pseudo_id": 4239675.220679819,
                "traffic_medium": "referral",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "page_title": "Home",
                    "session_engaged": 1,
                    "clean_event": "gtm.js",
                    "engaged_session_event": 1,
                    "ga_session_id": 77729219,
                    "ga_session_number": 1,
                    "debug_mode": 1
                },
                "ga_session_id": 77729219
            },
            {
                "__id": "1611340000000000|5188370.382780906|session_start|5822567921",
                "event_date": 20210122,
                "event_timestamp": 1611340000000000,
                "event_name": "session_start",
                "user_pseudo_id": 5188370.382780906,
                "traffic_medium": "<Other>",
                "device_category": "desktop",
                "browser": "Chrome",
                "device_detail": "desktop / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "engaged_session_event": 1,
                    "ga_session_number": 1,
                    "ga_session_id": 9674589155,
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel",
                    "page_title": "Apparel | Google Merchandise Store"
                },
                "ga_session_id": 9674589155
            },
            {
                "__id": "1609600000000000|5428986.989179107|user_engagement|-895549809",
                "event_date": 20210102,
                "event_timestamp": 1609600000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 5428986.989179107,
                "traffic_medium": "organic",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "debug_mode": 1,
                    "session_engaged": 1,
                    "ga_session_number": 1,
                    "engagement_time_msec": 3421,
                    "ga_session_id": 3704594243,
                    "page_title": "Google Dino Game Tee",
                    "page_location": "https://shop.googlemerchandisestore.com/Google+Redesign/Apparel/Google+Dino+Game+Tee",
                    "engaged_session_event": 1
                },
                "ga_session_id": 3704594243
            },
            {
                "__id": "1609900000000000|5612330.689277568|page_view|-6171734046",
                "event_date": 20210106,
                "event_timestamp": 1609900000000000,
                "event_name": "page_view",
                "user_pseudo_id": 5612330.689277568,
                "traffic_medium": "cpc",
                "device_category": "desktop",
                "browser": "Edge",
                "device_detail": "desktop / Edge",
                "event_value_in_usd": 0,
                "params": {
                    "page_title": "Home",
                    "debug_mode": 1,
                    "engaged_session_event": 1,
                    "engagement_time_msec": 12,
                    "page_location": "https://shop.googlemerchandisestore.com/",
                    "ga_session_number": 1,
                    "ga_session_id": 5060149289,
                    "session_engaged": 1
                },
                "ga_session_id": 5060149289
            },
            {
                "__id": "1610800000000000|5733492.116239125|page_view|3693075657",
                "event_date": 20210116,
                "event_timestamp": 1610800000000000,
                "event_name": "page_view",
                "user_pseudo_id": 5733492.116239125,
                "traffic_medium": "(none)",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "entrances": 1,
                    "clean_event": "gtm.js",
                    "page_title": "Home",
                    "debug_mode": 1,
                    "ga_session_number": 1,
                    "ga_session_id": 6478020992,
                    "engaged_session_event": 1,
                    "page_location": "https://shop.googlemerchandisestore.com/store.html",
                    "session_engaged": 0
                },
                "ga_session_id": 6478020992
            },
            {
                "__id": "1611140000000000|5971348.017087772|user_engagement|8778019628",
                "event_date": 20210120,
                "event_timestamp": 1611140000000000,
                "event_name": "user_engagement",
                "user_pseudo_id": 5971348.017087772,
                "traffic_medium": "(none)",
                "device_category": "mobile",
                "browser": "Chrome",
                "device_detail": "mobile / Chrome",
                "event_value_in_usd": 0,
                "params": {
                    "campaign": "(direct)",
                    "session_engaged": 1,
                    "medium": "(none)",
                    "debug_mode": 1,
                    "engaged_session_event": 1
                }
            }
        ],
        "device": {}
    },
    "reportPaymentId": "698066f101095138fa14c7ca",
    "reportPaymentType": "jam",
    "paid": true,
    "segment": {
        "sid": "56e7142775",
        "matchType": "simple",
        "device": null,
        "exist": null,
        "refer": null,
        "granularity": "day",
        "utm": null,
        "survey": null,
        "start": "2021-01-02",
        "end": "2021-01-31",
        "parentSid": "s56e7142775",
        "domain": "GA4 Sample",
        "lang": "ko"
    }
}"""
