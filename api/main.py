# default lib
import os
import logging
from uuid import uuid4
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# fast-api
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# route
from api.agent import agent
from api.operation import operation
from api.vector import vector
from api.question import question

# local lib
from auth.jwt import create_token
from auth.dependencies import get_refresh_user
from client.slack import SlackClient
from utils.constants import STAGING, PRODUCTION
from response import Res200, TokenRes
from client.mongo import MongoClient, ProductionMongoClient
from client.redis import RedisClient
from client.milvus import MilvusClient
from client.aws import S3Client
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from auth.dependencies import get_optional_user
from utils.error import handle_errors, token_exception_handler


# LOAD .ENV & SET ROOT PATH
APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path, override=True)

# SET UP LOGGING
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)


# LIFESPAN: STARTUP & SHUTDOWN
@asynccontextmanager
async def lifespan(app: FastAPI):
    server_stage = os.getenv("SERVER_STAGE")

    # 인스턴스 생성 → 연결 초기화 → app.state에 보관
    main_db = MongoClient()
    await main_db.initialize()

    memory_db = RedisClient()
    await memory_db.connect()

    s3 = S3Client()
    await s3.initialize()

    vector_db = MilvusClient()
    await vector_db.connect()

    llm_proxy = LLMProxyClient()
    await llm_proxy.connect()
    await llm_proxy.add_connection()

    # app.state에 등록 → Depends(Request)로 주입
    app.state.main_db = main_db
    app.state.memory_db = memory_db
    app.state.s3 = s3
    app.state.llm_proxy = llm_proxy
    app.state.production_db = None
    app.state.message_client = None

    if server_stage == STAGING:
        production_db = ProductionMongoClient()
        await production_db.initialize()
        app.state.production_db = production_db

    if server_stage == PRODUCTION:
        slack = SlackClient()
        await slack.connect()
        app.state.message_client = slack

    yield

    # Shutdown: 역순으로 해제
    if server_stage == PRODUCTION and app.state.message_client:
        await app.state.message_client.disconnect()
    if server_stage == STAGING and app.state.production_db:
        await app.state.production_db.disconnect()
    await llm_proxy.disconnect()
    await vector_db.disconnect()
    await s3.close()
    await memory_db.disconnect()
    await main_db.disconnect()


# API SETTING
app = FastAPI(
    title="Solomon API",
    version="1.0.0",
    description="LLM service API",
    root_path="/solomon-api",
    lifespan=lifespan
)
app.include_router(agent)
app.include_router(operation)
app.include_router(vector)
app.include_router(question)
token_exception_handler(app)

# CORS
if os.getenv("SERVER_STAGE") == STAGING:
    allow_origins = [
        "http://localhost:3333",
        "http://localhost:5173",
        "http://localhost:8550",
        "http://localhost:8810",
        "http://localhost:8540",
        "https://staging-solomon.beusable.net",
        "https://staging-analytics.beusable.net",
        "https://staging-eagle.beusable.net",
        "https://dream.beusable.net",
        "https://dev-solomon.beusable.net",
        "https://dev-analytics.beusable.net"
    ]
elif os.getenv("SERVER_STAGE") == PRODUCTION:
    allow_origins = [
        "https://solomon.beusable.net",
        "https://analytics.beusable.net",
        "https://eagle.beusable.net",
        "https://tool.beusable.net",
    ]
else:
    allow_origins = ["http://localhost:3333"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Id", "askCode"]
)


# 엔드포인트 정의
@app.get("/check", response_model=Res200)
async def check():
    """CHECK SERVER IS LIVING"""
    return Res200(message="I AM LIVING")


@app.get("/get_token", response_model=TokenRes)
@handle_errors()
async def get_token(
    session_key: str = Depends(get_optional_user)
):
    """CREATE SESSION"""
    if not session_key:
        session_key = str(uuid4())
    access_token, refresh_token = create_token(session_key)
    return TokenRes(
        res=Res200(message="access"),
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.get("/get_new_session_token", response_model=TokenRes)
@handle_errors()
async def get_new_token():
    session_key = str(uuid4())
    access_token, refresh_token = create_token(session_key)
    return TokenRes(
        res=Res200(message="access"),
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.get("/refresh", response_model=TokenRes)
@handle_errors()
async def refresh(
    session_key: str = Depends(get_refresh_user)
):
    """REFRESH SESSION"""
    access_token, refresh_token = create_token(session_key)
    return TokenRes(
        res=Res200(message="refresh"),
        access_token=access_token,
        refresh_token=refresh_token
    )


# Run API server
if __name__ == "__main__":
    uvicorn.run(
        "main:app", # app=app,
        host="0.0.0.0",
        port=8888,
        timeout_keep_alive=180,
        limit_concurrency=1000,
        limit_max_requests=1000,
        loop="asyncio",
        http="httptools",
        log_level="info",
        reload=True
    )