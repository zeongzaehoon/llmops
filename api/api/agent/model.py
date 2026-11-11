"""Agent domain router: model (split from api/agent.py — paths/signatures unchanged)."""
from fastapi import APIRouter, Depends
from payload.agent import *
from helper.agent import *
from utils.error import *
from response import Res200
from client.mongo import MongoClient
from client import get_main_db


agent = APIRouter(prefix="/agent", tags=["Agent"])


@agent.get("/get_models", response_model=Res200)
@handle_errors()
async def _get_models(
    query_params:GetModelQueryParams=Depends(),
):
    data = {
        "modelList": MODEL_LIST
    }
    return Res200(
        message="success",
        data=data
    )


@agent.get("/get_current_model", response_model=Res200)
@handle_errors()
async def _get_current_model(
    query_params: GetCurrentModelQueryParams = Depends(),
    main_db_client: MongoClient = Depends(get_main_db),
):
    # # query_params  (원본 - 불필요한 중간 변수)
    # category = query_params.agent
    # data = await helper_get_current_model(main_db_client, category)
    data = await helper_get_current_model(main_db_client, query_params.agent)

    # make response and return
    return Res200(data=data)


@agent.post("/set_vendor_and_model", response_model=Res200)
@handle_errors()
async def _set_vendor_and_model(
    payload: SetVendorAndModelPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # insert & update
    await helper_set_vendor_and_model(main_db_client=main_db_client, payload=payload)

    # make response and return
    return Res200(message="success")
