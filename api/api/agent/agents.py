"""Agent domain router: agents (split from api/agent.py — paths/signatures unchanged)."""
from fastapi import APIRouter, Depends
import pytz
from bson import ObjectId
from payload.agent import *
from helper.agent import *
from utils.error import *
from response import Res200, Res400
from client.mongo import MongoClient
from client import get_main_db


agent = APIRouter(prefix="/agent", tags=["Agent"])


@agent.post("/create_agent", response_model=Res200)
@handle_errors()
async def create_agent(
    payload: CreateAgentPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # 동일 agent 식별자 중복 체크
    existing = await main_db_client.find_one(
        collection=AGENT_COLLECTION,
        filter={'agent': payload.agent}
    )
    if existing:
        return Res400(message=f"Agent '{payload.agent}' already exists").to_response()

    document = {
        'agent': payload.agent,
        'regDate': pytz.timezone('Asia/Seoul').localize(datetime.now()),
    }
    if payload.description:
        document['desc'] = payload.description

    await main_db_client.insert_one(collection=AGENT_COLLECTION, document=document)
    return Res200()


@agent.get("/get_agents", response_model=Res200)
@handle_errors()
async def get_agents(
    main_db_client: MongoClient = Depends(get_main_db),
):
    documents = await main_db_client.find(
        collection=AGENT_COLLECTION,
        filter={},
        sort=[('regDate', -1)]
    )
    result = []
    for doc in documents:
        doc['id'] = str(doc['_id'])
        doc.pop('_id', None)
        doc['description'] = doc.get('desc', '')
        doc.pop('desc', None)
        result.append(doc)
    return Res200(data=result)


@agent.post("/update_agent", response_model=Res200)
@handle_errors()
async def update_agent(
    payload: UpdateAgentPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    _filter = {"_id": ObjectId(payload.id)}
    update = {"$set": {}}
    if payload.name:
        update["$set"]["name"] = payload.name
    if payload.description:
        update["$set"]["desc"] = payload.description
    await main_db_client.update_one(collection=AGENT_COLLECTION, filter=_filter, update=update)
    return Res200()


@agent.post("/delete_agent", response_model=Res200)
@handle_errors()
async def delete_agent(
    payload: DeleteAgentPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    await main_db_client.delete_one(collection=AGENT_COLLECTION, filter={"_id": ObjectId(payload.id)})
    return Res200()
