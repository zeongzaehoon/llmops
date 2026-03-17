import os
import asyncio
import logging

from fastapi import APIRouter, Depends

from payload.vector import *
from helper.vector import *
from utils.error import *
from response import Res200
from client.pinecone import PineconeClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from client import get_llm_proxy, get_vector_db



vector = APIRouter(prefix="/vector", tags=["Vector"])



@vector.post("/upsert", response_model=Res200)
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
    return Res200(message="success")


@vector.post("/search", response_model=Res200)
@handle_errors()
async def _search(
    payload: searchPayload,
    vector_db_client = Depends(get_vector_db)
):
    """QUERY VECTOR DATA AND RETURN TEXT AND POSTID"""
    # set client (payload 의존적)
    matches = await vector_db_client.find(vector=payload.query, k=payload.k, filter=payload.filter)
    data = reform_pc_search(matches)
    return Res200(
        message="success",
        data=data
    )


@vector.post("/delete_id", response_model=Res200)
@handle_errors()
async def _delete_id(
    payload: deleteIdPayload,
    vector_db_client = Depends(get_vector_db)
):
    """DELETE SINGLE VECTOR DATA"""
    await vector_db_client.remove(id=payload.id)
    return Res200(message="success")


@vector.post("/delete_filter", response_model=Res200)
@handle_errors()
async def _delete_filter(
    payload: deleteFilterPayload,
    vector_db_client = Depends(get_vector_db)
):
    """
    DELETE MULTIPLE VECTOR DATA BY FILTER
    BE ABLE TO USE ONLY PRO
    """
    await vector_db_client.remove(delete_all=True, filter=payload.filter)
    return Res200(message="success")
