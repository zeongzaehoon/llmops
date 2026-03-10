import os
import asyncio
import logging

from fastapi import APIRouter, Depends

from payload.vector import *
from helper.vector import *
from utils.error import *
from client.pinecone import PineconeClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from client import get_llm_proxy, get_vector_db



vector = APIRouter(prefix="/vector", tags=["Vector"])



@vector.post("/upsert")
@handle_errors()
async def _upsert(
    payload: upsertPayload,
    vector_db_client: PineconeClient = Depends(get_vector_db),
    llm_proxy_client: LLMProxyClient = Depends(get_llm_proxy),
):
    """CREATE & UPDATE VECTOR DATA"""
    server_stage = os.getenv("SERVER_STAGE")
    # business logic
    await helper_upsert(vector_db_client, llm_proxy_client, payload, server_stage)
    # make response and return response
    return Response200(
        message="success"
    ).to_dict()


@vector.post("/search")
@handle_errors()
async def _search(payload: searchPayload):
    """QUERY VECTOR DATA AND RETURN TEXT AND POSTID"""
    # set client (payload 의존적)
    vector_db_client = PineconeClient(index_name=payload.index_name)
    matches = await vector_db_client.find(vector=payload.query, k=payload.k, filter=payload.filter)
    data = reform_pc_search(matches)
    return Response200(
        message="success",
        data=data
    ).to_dict()


@vector.post("/delete_id")
@handle_errors()
async def _delete_id(payload: deleteIdPayload):
    """DELETE SINGLE VECTOR DATA"""
    vector_db_client = PineconeClient(index_name=payload.index_name)
    await vector_db_client.remove(id=payload.id)
    return Response200(
        message="success"
    ).to_dict()


@vector.post("/delete_filter")
@handle_errors()
async def _delete_filter(payload: deleteFilterPayload):
    """
    DELETE MULTIPLE VECTOR DATA BY FILTER
    BE ABLE TO USE ONLY PRO
    """
    vector_db_client = PineconeClient(index_name=payload.index_name)
    await vector_db_client.remove(delete_all=True, filter=payload.filter)
    return Response200(
        message="success"
    ).to_dict()
