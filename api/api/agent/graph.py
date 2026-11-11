"""Agent domain router: graph (split from api/agent.py — paths/signatures unchanged)."""
from fastapi import APIRouter, Depends
import pytz
from bson import ObjectId
from payload.agent import *
from helper.agent import *
from utils.error import *
from response import Res200
from client.mongo import MongoClient
from client import get_main_db


agent = APIRouter(prefix="/agent", tags=["Agent"])


def _serialize_edges(edges) -> list[dict]:
    """EdgeNodePayload 리스트 → DB 저장용 dict 리스트"""
    return [
        {'from': e.source, 'to': e.target, 'condition': e.condition,
         'onFailure': e.on_failure, 'maxRetries': e.max_retries}
        for e in edges
    ]


@agent.post("/create_multi_agent_graph", response_model=Res200)
@handle_errors()
async def create_multi_agent_graph(
    payload: CreateMultiAgentGraphPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    document = {
        'name': payload.name,
        'graphType': payload.graph_type,
        'agents': [{'agent': a.agent, 'role': a.role} for a in payload.agents],
        'config': {
            'maxIterations': payload.max_iterations,
        },
        'regDate': pytz.timezone('Asia/Seoul').localize(datetime.now()),
    }
    if payload.edges:
        document['edges'] = _serialize_edges(payload.edges)
    if payload.description:
        document['desc'] = payload.description

    await main_db_client.insert_one(collection=MULTI_AGENT_GRAPH_COLLECTION, document=document)
    return Res200()


@agent.get("/get_multi_agent_graphs", response_model=Res200)
@handle_errors()
async def get_multi_agent_graphs(
    main_db_client: MongoClient = Depends(get_main_db),
):
    documents = await main_db_client.find(
        collection=MULTI_AGENT_GRAPH_COLLECTION,
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


@agent.post("/get_multi_agent_graph", response_model=Res200)
@handle_errors()
async def get_multi_agent_graph(
    payload: GetMultiAgentGraphPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    document = await main_db_client.find_one(
        collection=MULTI_AGENT_GRAPH_COLLECTION,
        filter={"_id": ObjectId(payload.id)}
    )
    if document:
        document['id'] = str(document['_id'])
        document.pop('_id', None)
        document['description'] = document.get('desc', '')
        document.pop('desc', None)
    return Res200(data=document)


@agent.post("/update_multi_agent_graph", response_model=Res200)
@handle_errors()
async def update_multi_agent_graph(
    payload: UpdateMultiAgentGraphPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    _filter = {"_id": ObjectId(payload.id)}
    update = {"$set": {}}
    if payload.name:
        update["$set"]["name"] = payload.name
    if payload.graph_type:
        update["$set"]["graphType"] = payload.graph_type
    if payload.agents:
        update["$set"]["agents"] = [{'agent': a.agent, 'role': a.role} for a in payload.agents]
    if payload.edges is not None:
        update["$set"]["edges"] = _serialize_edges(payload.edges)
    if payload.description:
        update["$set"]["desc"] = payload.description
    if payload.max_iterations is not None:
        update["$set"]["config.maxIterations"] = payload.max_iterations
    await main_db_client.update_one(
        collection=MULTI_AGENT_GRAPH_COLLECTION, filter=_filter, update=update
    )
    return Res200()


@agent.post("/delete_multi_agent_graph", response_model=Res200)
@handle_errors()
async def delete_multi_agent_graph(
    payload: DeleteMultiAgentGraphPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    delete_filter = {"_id": ObjectId(payload.id)}
    await main_db_client.delete_one(collection=MULTI_AGENT_GRAPH_COLLECTION, filter=delete_filter)
    return Res200()
