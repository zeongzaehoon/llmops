"""Agent domain router: prompt (split from api/agent.py — paths/signatures unchanged)."""
from fastapi import APIRouter, Depends
from payload.agent import *
from helper.agent import *
from payload.agent import GetPromptVersionsPayload, GetPromptDataPayload
from helper.agent import helper_get_prompt_versions, helper_get_prompt_data
from utils.error import *
from response import Res200
from client.mongo import MongoClient
from client import get_main_db


agent = APIRouter(prefix="/agent", tags=["Agent"])


@agent.post("/insert_prompt", response_model=Res200)
@handle_errors()
async def _insert_prompt(
    payload: InsertPromptPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # make insert data & insert data to Database
    await helper_insert_prompt_data(main_db_client=main_db_client, payload=payload)

    # make response and return response
    return Res200(message="success")


@agent.post("/get_prompt_versions", response_model=Res200)
@handle_errors()
async def _get_prompt_versions(
    payload: GetPromptVersionsPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_prompt_versions(main_db_client=main_db_client, payload=payload)
    return Res200(data=data)


@agent.post("/get_prompt_data", response_model=Res200)
@handle_errors()
async def _get_prompt_data(
    payload: GetPromptDataPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_prompt_data(main_db_client=main_db_client, payload=payload)
    return Res200(data=data)
