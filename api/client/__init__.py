"""
FastAPI Dependency Injection
- lifespan에서 초기화된 클라이언트를 app.state에서 꺼내 주입
- Route에서는 Depends(get_xxx)로 받아 사용
"""
from fastapi import Request

from client.mongo import MongoClient, ProductionMongoClient
from client.redis import RedisClient
from client.aws import S3Client
from client.slack import SlackClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from client.milvus import MilvusClient



def get_main_db(request: Request) -> MongoClient:
    return request.app.state.main_db


def get_production_db(request: Request) -> ProductionMongoClient:
    return request.app.state.production_db


def get_memory_db(request: Request) -> RedisClient:
    return request.app.state.memory_db


def get_s3(request: Request) -> S3Client:
    return request.app.state.s3


def get_llm_proxy(request: Request) -> LLMProxyClient:
    return request.app.state.llm_proxy


def get_message_client(request: Request) -> SlackClient | None:
    return request.app.state.message_client


def get_vector_db(request: Request) -> MilvusClient:
    return request.app.state.vector_db
