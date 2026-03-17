from fastapi import APIRouter, Depends, File, UploadFile
from auth.jwt import create_token

from payload.question import *
from helper.question import *
from auth.dependencies import get_current_user, get_optional_user
from client.mongo import MongoClient
from client.redis import RedisClient
from client.pinecone import PineconeClient
from client.aws import S3Client
from client.slack import SlackClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from client import get_main_db, get_memory_db, get_s3, get_llm_proxy, get_message_client

from utils.date import *
from utils.error import *
from utils.streaming import get_response_queue
from response import Res200, Res400, Res500, TokenRes


from module.llm.activate import RunLLM as RunLLMProxy
from module.multi_agent.activate import RunMultiAgent



question = APIRouter(prefix="/question", tags=["Question"])



@question.post("/ask", response_model=Res200)
@handle_errors()
async def _ask(
    payload: askPayload,
    session_key: str = Depends(get_current_user),
    response = Depends(get_response_queue),
    main_db_client: MongoClient = Depends(get_main_db),
    memory_db_client: RedisClient = Depends(get_memory_db),
    s3_client: S3Client = Depends(get_s3),
    llm_proxy_client: LLMProxyClient = Depends(get_llm_proxy),
    message_client: SlackClient | None = Depends(get_message_client),
):
    # server stage
    server_stage = os.getenv("SERVER_STAGE", "development")
    try:
        # time test
        start_time = time.time()

        # set Client (payload 의존적인 클라이언트만 라우터에서 생성)
        vector_db_index_name = get_vector_db_index(category=payload.agent, server_stage=server_stage)
        vector_db_client = PineconeClient(index_name=vector_db_index_name)

        # business logic
        # multi agent graph
        if payload.graph_id:
            graph_doc = await main_db_client.find_one(
                collection=MULTI_AGENT_GRAPH_COLLECTION,
                filter={"_id": ObjectId(payload.graph_id)}
            )
            if not graph_doc:
                return Res400(message="Multi agent graph not found").to_response()

            multi_agent_args = {
                "server_stage": server_stage,
                "session_key": session_key,
                "question": payload.question,
                "graph_id": payload.graph_id,
                "graph_type": graph_doc["graphType"],
                "agents": graph_doc["agents"],
                "edges": graph_doc.get("edges", []),
                "max_iterations": graph_doc.get("config", {}).get("maxIterations", 3),
                "streaming": payload.streaming,
                "llm_proxy_client": llm_proxy_client,
                "main_db_client": main_db_client,
                "memory_db_client": memory_db_client,
                "message_client": message_client,
                "lang": payload.lang,
            }
            generator = RunMultiAgent(args=multi_agent_args).activate()
            if payload.streaming:
                return await streaming_response(
                    response=response,
                    generator=generator,
                    ask_id=f"multi_agent:{payload.graph_id}",
                    start_time=start_time,
                    session_key=session_key
                )
            else:
                answer = ""
                async for chunk in generator:
                    answer += chunk
                return Res200(data=answer)

        # make args
        if payload.is_mcp:
            args = make_mcp_args(session_key=session_key, payload=payload, server_stage=server_stage)
        elif payload.agent == SCHEMATAG:
            args = make_args_for_schematag(session_key=session_key, payload=payload, server_stage=server_stage)
        elif payload.agent in DOCENT_LIST:
            args = await make_args_for_docent(memory_db_client=memory_db_client, session_key=session_key, payload=payload, server_stage=server_stage)
            insert_id = await insert_chat_history(main_db_client=main_db_client, args=args)
            args["insert_id"] = insert_id
            payload.docent_document_id = insert_id
        elif payload.agent in HEATMAP_LIST:
            args = make_args_for_heatmap(session_key=session_key, payload=payload, server_stage=server_stage)
        elif payload.agent == VOC:
            args = await make_args_for_voc(main_db_client=main_db_client, session_key=session_key, payload=payload, server_stage=server_stage)
        elif payload.agent in DASHBOARD_LIST:
            args = make_args_for_dashboard(session_key=session_key, payload=payload, server_stage=server_stage)
        elif payload.agent in UXGPT_LIST:
            if payload.fixed_answer:
                await save_fixed_message(payload.fixed_answer, memory_db_client, main_db_client, session_key, payload.info)
                generator = make_fixed_message(payload.fixed_answer)
                return await streaming_response(response=response, generator=generator, ask_id=f"fixed_answer:{payload.fixed_answer}")
            else:
                args = make_args_for_contactus(session_key=session_key, payload=payload, server_stage=server_stage)
        else:
            args = make_args(session_key=session_key, payload=payload, server_stage=server_stage)

        # set common args
        args["server_stage"] = server_stage
        args["vector_db_client"] = vector_db_client
        args["main_db_client"] = main_db_client
        args["memory_db_client"] = memory_db_client
        args["s3_client"] = s3_client
        args["llm_proxy_client"] = llm_proxy_client
        args["service_type"] = payload.service_type
        args["start_time"] = start_time
        args["init_date"] = get_utc_now()
        if server_stage == PRODUCTION and message_client:
            args["message_client"] = message_client

        # error message or set client in args
        if args.get("agent") == SCHEMASIMPLE:
            is_url_error = await check_url_valid(args)
            args["error"] = is_url_error # {"error_key": True} or None

        if args.get("error") and payload.streaming:
            generator = make_error_message(streaming=payload.streaming, **args["error"])
            return await streaming_response(response=response, generator=generator, ask_id=args.get("ask_id"), is_error=True)
        elif args.get("error") and not payload.streaming:
            return Res500(data=make_error_message(streaming=payload.streaming, **args["error"])).to_response()

        # run LLM
        logging.info(f"session_key: {session_key} | ==================== START Analysis agent: {args.get('agent')}")
        logging.info(f"session_key: {session_key} | ==================== START Analysis is_mcp: {payload.is_mcp or False}")
        llm_generator = RunMCPProxy(args=args) if payload.is_mcp else RunLLMProxy(args=args)

        # return response on streaming
        if payload.streaming:
            return await streaming_response(
                response=response,
                generator=llm_generator.activate(),
                ask_id=args.get("ask_id"),
                start_time=start_time,
                session_key=session_key
            )
        else:
            answer = str()
            async for chunk in llm_generator.activate():
                answer += chunk
            return Res200(data=answer)

    # asyncio tasks에서 에러가 발생했을 때, handle error decorator에서 except 처리 불가
    except Exception as e:
        logging.error(f"session_key: {session_key} | [api.question._ask] 🔴 Exception")
        tasks = []
        if server_stage == PRODUCTION and payload.agent in ON_PRODUCTION_LIST and message_client:
            message = f"🔴 session_key: {session_key}, agent: {payload.agent} | [solomon-api] API router Error: Exception"
            tasks.append(message_client.send_message(channel="casual", message=message))
        if payload.docent_document_id:
            tasks.append(main_db_client.delete_one(CHAT_COLLECTION, {"_id": payload.docent_document_id}))
        tasks.append(helper_insert_error_document(main_db_client=main_db_client, session_key=session_key, payload=payload))
        await asyncio.gather(*tasks)
        return await streaming_response(
            response=response,
            generator=make_error_message(streaming=payload.streaming, agent=payload.agent, **{"LLMError": True}),
            is_error=True
        ) if payload.streaming else Res500(data=await make_error_message(**{"LLMError": True})).to_response()


@question.post("/set_report", response_model=Res200)
async def _set_report(
    payload: setReportPayload,
    session_key: str = Depends(get_current_user),
    main_db_client: MongoClient = Depends(get_main_db),
    s3_client: S3Client = Depends(get_s3),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    """
    reportchat, dashboardChat, scrollChat 등
    레포트 기반 대화 시, 레포트 등록하는 라우터
    """
    # business logic
    await helper_set_report(
        main_db_client=main_db_client,
        s3_client=s3_client,
        memory_db_client=memory_db_client,
        session_key=session_key,
        report_id=payload.report_id,
        category=payload.agent,
        service_type=payload.service_type
    )

    # make response and return
    return Res200(message="success to set report")


@question.post("/insert_init_reportchat_row", response_model=Res200)
@handle_errors()
async def _insert_init_reportchat_row(
    payload: insertInitReportchatRowPayload,
    session_key: str = Depends(get_current_user),
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    await helper_insert_init_reportchat_row(main_db_client=main_db_client, session_key=session_key, payload=payload)

    # make response
    return Res200(message="success to insert init reportchat row")



@question.get("/reset_report", response_model=TokenRes)
@handle_errors()
async def _reset_report(
    session_key: str = Depends(get_current_user),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # business logic
    new_session_key = str(uuid4())
    access_token, refresh_token = create_token(new_session_key)

    await helper_reset_report(
        memory_db_client=memory_db_client,
        old_session_key=session_key,
        new_session_key=new_session_key
    )

    # make response
    return TokenRes(
        res=Res200(message="success to reset report", data=new_session_key),
        access_token=access_token,
        refresh_token=refresh_token
    )


@question.get("/remove_session_key", response_model=Res200)
async def _remove_session_key(
    session_key: str = Depends(get_optional_user),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # business logic
    if session_key is not None:
        await memory_db_client.delete(key=session_key)
        await memory_db_client.delete(key=f"rc:{session_key}")
        await memory_db_client.delete(key=f"rc_id:{session_key}")

    # make response
    return Res200(message="success to remove session key")


@question.post("/get_reportchat_datas", response_model=Res200)
async def _get_reportchat_data(
    payload: getReportChatDatasPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_reportchat_data(main_db_client=main_db_client, payload=payload)

    # make response
    return Res200(
        message="success to get reportchat datas",
        data=data
    )


@question.get("/get_current_set_report", response_model=Res200)
async def _get_current_set_report(
    session_key: str = Depends(get_current_user),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # business logic
    data = await memory_db_client.get(key=f"rc:{session_key}")

    # make response
    return Res200(
        message="success to get current set report",
        data=data
    )


@question.get("/get_current_set_report_id", response_model=Res200)
async def _get_current_set_report_id(
    session_key: str = Depends(get_current_user),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # business logic
    data = await memory_db_client.get(key=f"rc_id:{session_key}")

    # make response
    return Res200(
        message="success",
        data=data
    )


@question.get("/model", response_model=Res200)
@handle_errors()
async def _model(
    query_params: GetModelQueryParams = Depends(),
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    vendor = None
    model = None
    is_set = False
    if query_params.agent:
        # get vendor and model from database and change status
        vendor, model, is_set = await helper_get_vendor_and_model_from_database(
            main_db_client=main_db_client,
            category=query_params.agent
        )

    # make response
    data = {
            "baseCompany": vendor or BASE_VENDOR,
            "baseModel": model or BASE_MODEL,
            "isSet": is_set,
            "modelList": MCP_MODEL_LIST if query_params.agent in MCP_LIST else MODEL_LIST,
    }

    # return response
    return Res200(
        message="success",
        data=data
    )


@question.post("/refer", response_model=Res200)
async def _refer(
    payload: referPayload,
    session_key: str = Depends(get_optional_user),
    main_db_client: MongoClient = Depends(get_main_db),
    memory_db_client: RedisClient = Depends(get_memory_db),
    llm_proxy_client: LLMProxyClient = Depends(get_llm_proxy),
):
    # get server stage
    server_stage = os.getenv("SERVER_STAGE", "development")

    # seperator
    category = payload.agent

    # client (payload 의존적)
    vector_db_index_name = get_vector_db_index(category=category, server_stage=server_stage)
    vector_db_client = PineconeClient(index_name=vector_db_index_name)

    # business logic
    if category in DOCENT_LIST or category in DASHBOARD_LIST:
        retrieval_data = []

    elif category == REPORTCHAT:
        retrieval_data = await RunLLMProxy.get_retrieval_data_for_report_chat(
                memory_db_client=memory_db_client,
                session_key=session_key
            )
    else:
        service = helper_refer_get_service(category=category, server_stage=server_stage)
        retrieval_data = await RunLLMProxy.get_retrieval_data_for_view(llm_proxy_client=llm_proxy_client, vector_db_client=vector_db_client, question=payload.question, service=service)

    # make response and return
    return Res200(
        message="success",
        data={"refer":retrieval_data}
    )


@question.get("/get", response_model=Res200)
async def _get_report_chat_datas(
    session_key: str = Depends(get_optional_user),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # get history data
    data = [] if not session_key else await helper_get_conversation_history_from_redis(memory_db_client=memory_db_client, session_key=session_key)

    # make response
    return Res200(
        message="success",
        data=data
    )


@question.post("/update_rating", response_model=Res200)
@handle_errors()
async def _update_rating(
    payload: updateRatingPayload,
    session_key: str = Depends(get_current_user),
    main_db_client: MongoClient = Depends(get_main_db),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # payload
    rating = payload.rating or 0 # 0: none, 1: dislike, 5: like
    ask_id = payload.id

    # business logic
    await helper_update_rating_to_main_db(main_db_client=main_db_client, ask_id=ask_id, rating=rating)
    history_data = await helper_get_conversation_history_from_redis(memory_db_client=memory_db_client, session_key=session_key)
    if history_data:
        await helper_update_rating_to_memory_db(memory_db_client=memory_db_client, session_key=session_key, rating=rating, ask_id=ask_id, history_data=history_data)

    # make response
    return Res200(message="success")


@question.get("/get_token_for_reportchat", response_model=Res200)
@handle_errors()
async def _get_token_for_reportchat(
    Id: str,
    session_key: str = Depends(get_current_user),
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_token_for_docent(main_db_client=main_db_client, Id=Id)

    # make response
    return Res200(
        message="success",
        data=data
    )


@question.get("/checking_schema_simple", response_model=Res200)
@handle_errors()
async def checking_schema_simple(
    session_key: str = Depends(get_current_user),
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    document = await main_db_client.find_one(
        collection=CHAT_COLLECTION,
        filter={
            'sessionKey': session_key,
            "agent": SCHEMASIMPLE,
            "is_mcp": True,
            "llmProxyError": {"$ne": True}
        },
        projection={'_id': 1}
    )
    is_success = True if document else False

    # make result and response
    data = {"is_success": is_success}
    return Res200(data=data)