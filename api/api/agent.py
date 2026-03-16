from fastapi import APIRouter, Depends
import json
import pytz
import tiktoken
from bson import ObjectId

from payload.agent import *
from helper.agent import *
from payload.agent import GetPromptVersionsPayload, GetPromptDataPayload
from helper.agent import helper_get_prompt_versions, helper_get_prompt_data
from utils.error import *
from utils.response import *
from client.mongo import MongoClient, ProductionMongoClient
from client.redis import RedisClient
from client.pinecone import PineconeClient
from client.fastmcp import FastMCPClient
from client import get_main_db, get_memory_db, get_production_db



agent = APIRouter(prefix="/agent", tags=["Agent"])




@agent.get("/get_models")
@handle_errors()
async def _get_models(
    query_params:GetModelQueryParams=Depends(),
):
    data = {
        "modelList": MODEL_LIST
    }
    return Response200(
        message="success",
        data=data
    ).to_dict()


@agent.get("/get_current_model")
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
    return Response200(data=data).to_dict()


@agent.post("/set_vendor_and_model")
@handle_errors()
async def _set_vendor_and_model(
    payload: SetVendorAndModelPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # insert & update
    await helper_set_vendor_and_model(main_db_client=main_db_client, payload=payload)

    # make response and return
    return Response200(message="success").to_dict()


@agent.post("/insert_prompt")
@handle_errors()
async def _insert_prompt(
    payload: InsertPromptPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # make insert data & insert data to Database
    await helper_insert_prompt_data(main_db_client=main_db_client, payload=payload)

    # make response and return response
    return Response200(
        message="success"
    ).to_dict()


@agent.post("/get_prompt_versions")
@handle_errors()
async def _get_prompt_versions(
    payload: GetPromptVersionsPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_prompt_versions(main_db_client=main_db_client, payload=payload)
    return Response200(data=data).to_dict()


@agent.post("/get_prompt_data")
@handle_errors()
async def _get_prompt_data(
    payload: GetPromptDataPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_prompt_data(main_db_client=main_db_client, payload=payload)
    return Response200(data=data).to_dict()



@agent.post("/get_version")
@handle_errors()
async def _get_version(
    payload: GetVersionPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_version(main_db_client=main_db_client, payload=payload)

    # make response
    return Response200(
        message="success",
        data=data
    ).to_dict()


@agent.post("/get_data")
@handle_errors()
async def _get_data(
    payload: GetDataPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # server stage
    stage = os.getenv("SERVER_STAGE", "development")

    # client
    vector_db_index_name = get_vector_db_index(category=payload.agent, server_stage=stage)
    vector_db_client = PineconeClient(index_name=vector_db_index_name)

    # business logic
    data = await helper_get_data(main_db_client=main_db_client, vector_db_client=vector_db_client, payload=payload)

    # make response
    return Response200(
        message="success",
        data=data
    ).to_dict()


@agent.post("/get_prompt")
@handle_errors()
async def _get_prompt(
    payload: GetPromptPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_prompt(main_db_client=main_db_client, payload=payload)
    return Response200(data=data).to_dict()


@agent.post("/get_token_size")
@handle_errors()
async def _get_token_size(
    payload: GetTokenSizePayload,
):
    content = payload.prompt
    if not content:
        return Response500(message="THERE ARE NOT CONTENT").to_dict()
    model_name = BASE_MODEL
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # fallback for older tiktoken versions that don't recognize newer model names
        fallback_encoding = "o200k_base" if model_name.startswith(("gpt-4o", "o1", "o3", "o4")) else "cl100k_base"
        encoding = tiktoken.get_encoding(fallback_encoding)
    tokens = encoding.encode(content)
    return len(tokens)


@agent.post("/update_memo")
@handle_errors()
async def _update_memo(
    payload: UpdateMemoPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # update memo to main_db
    await helper_update_memo(main_db_client=main_db_client, payload=payload)

    # make response and return response
    return Response200(
        message="success"
    ).to_dict()


@agent.post("/download_question")
@handle_errors()
async def _download_question(
    payload: DownloadQuestionPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # get request data from main_db
    response = await helper_download_question(main_db_client=main_db_client, id=payload.id)

    # return response
    return response


@agent.post("/deploy")
@handle_errors()
async def _deploy(
    payload: DeployPayload,
    staging_main_db_client: MongoClient = Depends(get_main_db),
    real_main_db_client: ProductionMongoClient = Depends(get_production_db),
):
    # payload & check stage, password
    logging.info("start to deploy prompt from staging to production")
    stage = payload.stage
    isStaging = stage == STAGING
    if not isStaging:
        logging.info("not isStaging")
        raise ForbiddenError()

    password = payload.password
    isPassword = password == PASSWORD
    if not isPassword:
        logging.info("not isPassword")
        raise ForbiddenError()

    # deploy prompt
    await helper_deploy_whole(
        production_main_db_client=real_main_db_client,
        staging_main_db_client=staging_main_db_client,
        category=payload.agent
    )

    # make response and return response
    return Response200(
        message="success"
    ).to_dict()


@agent.get("/get_deploy_list")
@handle_errors()
async def _get_deploy_list(
    staging_main_db_client: MongoClient = Depends(get_main_db),
    production_main_db_client: ProductionMongoClient = Depends(get_production_db),
):
    # get deploy list from production & staging
    data = await helper_get_deploy_list(production_main_db_client=production_main_db_client, staging_main_db_client=staging_main_db_client)

    # make response
    return Response200(
        message="success",
        data=data
    ).to_dict()


@agent.post("/rollback")
@handle_errors()
async def _rollback(
    payload: RollbackPayload,
    production_main_db_client: ProductionMongoClient = Depends(get_production_db),
):
    # business logic
    isStaging = payload.stage == STAGING
    server_stage = os.getenv("SERVER_STAGE", "development")
    isServerStaging = server_stage == STAGING
    if isStaging and isServerStaging:
        password = payload.password
        isPassword = password == PASSWORD
        if not isPassword:
            raise ForbiddenError("cannot rollback because Wrong Password")

        await helper_rollback_not_aireport(
            production_main_db_client=production_main_db_client,
            category=payload.agent
        )

    else:
        raise ForbiddenError("cannot rollback because Invalid request")

    # make response
    return Response200(message="success").to_dict()


@agent.post("/enroll_mcp_server")
@handle_errors()
async def enroll_mcp_server(
    payload: EnrollMCPServerPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    document = {
        'name': payload.name,
        'uri': payload.uri,
        'token': payload.token,
        'desc': payload.description,
    }
    await main_db_client.insert_one(collection=MCP_SERVER_COLLECTION, document=document)

    # make response and return
    return Response200().to_orjson()


@agent.post("/create_agent")
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
        return Response400(message=f"Agent '{payload.agent}' already exists").to_orjson()

    document = {
        'agent': payload.agent,
        'regDate': pytz.timezone('Asia/Seoul').localize(datetime.now()),
    }
    if payload.description:
        document['desc'] = payload.description

    await main_db_client.insert_one(collection=AGENT_COLLECTION, document=document)
    return Response200().to_orjson()


@agent.get("/get_agents")
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
    return Response200(data=result).to_orjson()


@agent.post("/update_agent")
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
    return Response200().to_orjson()


@agent.post("/delete_agent")
@handle_errors()
async def delete_agent(
    payload: DeleteAgentPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    await main_db_client.delete_one(collection=AGENT_COLLECTION, filter={"_id": ObjectId(payload.id)})
    return Response200().to_orjson()


@agent.post("/create_mcp_toolset")
@handle_errors()
async def create_mcp_toolset(
    payload: CreateMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    document = {
        'agent': payload.agent,
        'name': payload.name,
        'regDate': pytz.timezone('Asia/Seoul').localize(datetime.now()),
        'mcpInfo': payload.mcp_info,
        'isService': False
    }
    if payload.description:
        document['desc'] = payload.description

    await main_db_client.insert_one(collection=MCP_TOOLSET_COLLECTION, document=document)

    # make response and return
    return Response200().to_orjson()


@agent.get("/get_mcp_server")
@handle_errors()
async def get_mcp_server(
    main_db_client: MongoClient = Depends(get_main_db),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # business logic
    documents = await main_db_client.find(collection=MCP_SERVER_COLLECTION, filter={})

    result = []
    for document in documents:
        server_id = str(document['_id'])
        # uri = document["uri"]   # (원본 - 미사용, 아래 server_info에서 직접 참조)
        # token = document["token"]  # (원본 - 미사용, 아래 FastMCPClient에서 직접 참조)

        server_info = {
            'id': server_id,
            'name': document['name'],
            'uri': document['uri'],
            'description': document.get('desc', ''),
        }
        logging.info(f"[agent.get_mcp_server] server_info: {server_info}")
        logging.info(f"[agent.get_mcp_server] document: {document}")

        # check Redis cache first
        cache_key = f"mcp_health:{server_id}"
        cached = await memory_db_client.get(cache_key)

        if cached:
            tools = json.loads(cached)
            server_info['live'] = True
            server_info['tools'] = tools
        else:
            tools = await FastMCPClient(document["uri"], document["token"]).list_tools()
            if tools:
                server_info['live'] = True
                server_info['tools'] = [{'toolName': tool['name'], 'description': tool['description']} for tool in tools]
                # cache in Redis with 30s TTL
                await memory_db_client.set_with_expire(cache_key, json.dumps(server_info['tools']), 30)
            else:
                server_info['live'] = False
                server_info['tools'] = []

        result.append(server_info)

    return Response200(data=result).to_orjson()


@agent.post("/get_mcp_server_tools")
@handle_errors()
async def get_mcp_server_tools(
    payload: GetMCPServerToolsPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    document = await main_db_client.find_one(collection=MCP_SERVER_COLLECTION, filter={"_id": ObjectId(payload.id)})
    mcp_server_uri = document.get('uri', None)
    mcp_server_token = document.get('token', None)
    list_tools = await FastMCPClient(mcp_server_uri, mcp_server_token).list_tools()
    result = [{'toolName': tool['name'], 'description': tool['description']} for tool in list_tools]

    # make response and result
    return Response200(data=result).to_orjson()


@agent.post("/get_mcp_toolset")
@handle_errors()
async def get_mcp_toolset(
    payload: GetMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    _filter = {'agent': payload.agent} if payload.agent else {}
    documents = await main_db_client.find(
        collection=MCP_TOOLSET_COLLECTION,
        filter=_filter,
        sort=[('regDate', -1)]
    )
    result = []
    if not documents:
        return Response200(data=result).to_orjson()
    mcp_server_ids = [_id['serverId'] for document in documents for _id in document['mcpInfo']]
    server_name_documents = await main_db_client.find(collection=MCP_SERVER_COLLECTION, filter={'_id': {'$in': mcp_server_ids}})
    server_names = {str(document['_id']): document['name'] for document in server_name_documents}

    # make response and return
    for document in documents:
        if document.get("mcpInfo"):
            for mcp_info in document["mcpInfo"]:
                if mcp_info.get('serverId') and mcp_info['serverId'] in server_names:
                    mcp_info['serverName'] = server_names[mcp_info['serverId']]
        document['id'] = str(document['_id'])
        document.pop('_id', None)
        document['description'] = document.get('desc', '')
        document.pop('desc', None)
        result.append(document)
    return Response200(data=result).to_orjson()


@agent.post("/update_mcp_server")
@handle_errors()
async def update_mcp_server(
    payload: UpdateMCPServerPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    _filter = {"_id": ObjectId(payload.id)}
    update = {"$set": {}}
    if payload.name:
        update["$set"]["name"] = payload.name
    if payload.uri:
        update["$set"]["uri"] = payload.uri
    if payload.description:
        update["$set"]["desc"] = payload.description
    await main_db_client.update_one(collection=MCP_SERVER_COLLECTION, filter=_filter, update=update)

    # make response and return
    return Response200().to_orjson()


@agent.post("/update_mcp_toolset")
@handle_errors()
async def update_mcp_agent(
    payload: UpdateMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    mcp_info = [{'serverId': info['serverId'], 'tools': info['tools']} for info in payload.mcp_info] if payload.mcp_info else None # 프론트에 내려준 serverName은 mcpInfo에 담지 않기
    _filter = {"_id": ObjectId(payload.id)}
    update = {"$set": {"mcpInfo": mcp_info}}
    if payload.name:
        update["$set"]["name"] = payload.name
    if payload.description:
        update["$set"]["desc"] = payload.description
    await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=_filter, update=update)

    # make response and return
    return Response200().to_orjson()


@agent.post("/adapt_toolset_on_service")
@handle_errors()
async def adapt_agent_on_service(
    payload: AdaptToolsetOnServicePayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # verify target toolset exists
    target = await main_db_client.find_one(collection=MCP_TOOLSET_COLLECTION, filter={"_id": ObjectId(payload.id)})
    if not target:
        return Response400(message="Target toolset not found").to_orjson()

    # step 1: deactivate current active toolset
    false_filter = {"agent": payload.agent, "isService": True}
    false_update = {"$set": {"isService": False}}
    await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=false_filter, update=false_update)

    # step 2: activate target toolset, with compensating rollback on failure
    try:
        _filter = {"_id": ObjectId(payload.id)}
        update = {"$set": {"isService": True}}
        await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=_filter, update=update)
    except Exception:
        # rollback: re-activate the previously active toolset
        rollback_update = {"$set": {"isService": True}}
        await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=false_filter, update=rollback_update)
        raise

    # make response and return
    return Response200().to_orjson()


@agent.post("/delete_mcp_server")
@handle_errors()
async def delete_mcp_server(
    payload: DeleteMCPServerPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # check if any toolsets reference this server
    referencing_toolsets = await main_db_client.find(
        collection=AGENT_COLLECTION,
        filter={"mcpInfo.serverId": payload.id}
    )
    if referencing_toolsets:
        affected_names = [toolset.get('name', 'unknown') for toolset in referencing_toolsets]
        return Response400(
            message=f"Cannot delete server. Referenced by toolsets: {', '.join(affected_names)}"
        ).to_orjson()

    # business logic
    delete_filter = {"_id": ObjectId(payload.id)}
    await main_db_client.delete_one(collection=MCP_SERVER_COLLECTION, filter=delete_filter)

    # make response and return
    return Response200().to_orjson()


@agent.post("/delete_mcp_toolset")
@handle_errors()
async def delete_mcp_toolset(
    payload: DeleteMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    delete_filter = {"_id": ObjectId(payload.id)}
    await main_db_client.delete_one(collection=MCP_TOOLSET_COLLECTION, filter=delete_filter)

    # make response and return
    return Response200().to_orjson()


# ==================== Multi Agent Graph ====================

def _serialize_edges(edges) -> list[dict]:
    """EdgeNodePayload 리스트 → DB 저장용 dict 리스트"""
    return [
        {'from': e.source, 'to': e.target, 'condition': e.condition,
         'onFailure': e.on_failure, 'maxRetries': e.max_retries}
        for e in edges
    ]

@agent.post("/create_multi_agent_graph")
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
    # if payload.edges:  # (원본 - _serialize_edges로 추출)
    #     document['edges'] = [
    #         {'from': e.source, 'to': e.target, 'condition': e.condition, 'onFailure': e.on_failure, 'maxRetries': e.max_retries}
    #         for e in payload.edges
    #     ]
    if payload.edges:
        document['edges'] = _serialize_edges(payload.edges)
    if payload.description:
        document['desc'] = payload.description

    await main_db_client.insert_one(collection=MULTI_AGENT_GRAPH_COLLECTION, document=document)
    return Response200().to_orjson()


@agent.get("/get_multi_agent_graphs")
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
    return Response200(data=result).to_orjson()


@agent.post("/get_multi_agent_graph")
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
    return Response200(data=document).to_orjson()


@agent.post("/update_multi_agent_graph")
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
    # if payload.edges is not None:  # (원본 - _serialize_edges로 추출)
    #     update["$set"]["edges"] = [
    #         {'from': e.source, 'to': e.target, ...}
    #         for e in payload.edges
    #     ]
    if payload.edges is not None:
        update["$set"]["edges"] = _serialize_edges(payload.edges)
    if payload.description:
        update["$set"]["desc"] = payload.description
    if payload.max_iterations is not None:
        update["$set"]["config.maxIterations"] = payload.max_iterations
    await main_db_client.update_one(
        collection=MULTI_AGENT_GRAPH_COLLECTION, filter=_filter, update=update
    )
    return Response200().to_orjson()


@agent.post("/delete_multi_agent_graph")
@handle_errors()
async def delete_multi_agent_graph(
    payload: DeleteMultiAgentGraphPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    delete_filter = {"_id": ObjectId(payload.id)}
    await main_db_client.delete_one(collection=MULTI_AGENT_GRAPH_COLLECTION, filter=delete_filter)
    return Response200().to_orjson()
