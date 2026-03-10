import datetime
from datetime import timedelta

from client.groxy import GroxyStreamingResponse

from .helper import *
from .dto import LLMArgs

from utils.constants import *
from utils.vector import get_token_length
from module.microagent.http_validate import agent_http_validate
from module.microagent.dashboard_data_validation import agent_dashboard_data_validate


async def run_llm(llmArgs:LLMArgs):
    try:
        # set user message
        is_report = llmArgs.agent in REPORT_LIST
        human_message = make_human_message(
            question=llmArgs.question,
            retrieval_data=llmArgs.retrieval_data,
            language_message=LANG_CHAT_PROMPT,
            image_data=llmArgs.images,
            is_report=is_report
        )

        # set all message for calculate token
        all_message_for_calculate_token = llmArgs.system_message + str(llmArgs.conversation_history) + human_message
        llmArgs.insert_mongo["token"] = get_token_length(all_message_for_calculate_token, llmArgs.model)

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - llmArgs.start_time))
        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # for debug message
        # write_log_for_debug_message(
        #     system_message=llmArgs.system_message,
        #     conversation_history=llmArgs.conversation_history,
        #     human_message=human_message
        # )

        is_first_chunk = True
        is_changing_vendor = False
        is_changing_model = False
        async for llmArgs.response in llmArgs.llm_proxy_client.stream(
            service=llmArgs.service or DEFAULT,
            vendor=llmArgs.vendor,
            model=llmArgs.model,
            system_message=llmArgs.system_message,
            conversation_history=llmArgs.conversation_history,
            human_message=human_message,
            time=float(llmArgs.start_time),
            session_key=llmArgs.session_key
        ):
            if llmArgs.response and isinstance(llmArgs.response, GroxyStreamingResponse):
                if is_first_chunk:
                    is_first_chunk = False
                    if llmArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=int(time_from_proxy - llmArgs.start_time))
                        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                text = getattr(llmArgs.response, "text", None)
                if text:
                    yield text
                    llmArgs.answer += text

                vendor = getattr(llmArgs.response, "vendor", None)
                if not is_changing_vendor and vendor:
                    llmArgs.vendor = vendor
                    is_changing_vendor = True

                model = getattr(llmArgs.response, "model", None)
                if not is_changing_model and model:
                    llmArgs.model = model
                    is_changing_model = True

                is_error = getattr(llmArgs.response, "is_error", None)
                if is_error:
                    llmArgs.answer = LANG_JA_ERR_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                    for word in llmArgs.answer:
                        yield word
                    llmArgs.is_error = True
                    err_message = "LLM-PROXY send Error. Both initial attempt and retry failed."
                    logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 LLMStreamingError: {err_message}")
                    if llmArgs.message_client:
                        message = f"🔴 session_key: {llmArgs.session_key}, category: {llmArgs.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
                        await llmArgs.message_client.send_message(channel='casual', message=message)


        # 완료 후 스테이징 모델 정보 전달
        finish_condition=os.getenv('SERVER_STAGE', None) != PRODUCTION and is_changing_vendor and is_changing_model and llmArgs.service not in [JOURNEYMAP_DASHBOARD, JOURNEYMAP_AIREPORT_STAGING]
        if finish_condition:
            added_message = f"\n\n![]('{llmArgs.vendor}:{llmArgs.model}')"
            for word in added_message:
                yield word

        # 콜백
        await callback(llmArgs)

    except DBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except VectorDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except AWSError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except LLMStreamingError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 LLMStreamingError: {e.message}")
        raise LLMStreamingError(e.message)
    except Exception as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_llm] 🔴 Exception: {e}")
        raise e


async def run_voc_llm(llmArgs:LLMArgs):
    try:
        is_report = llmArgs.agent in REPORT_LIST
        chat_language_prompt = LANG_JA_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_MESSAGE
        human_message = make_human_message(
            question=llmArgs.question,
            retrieval_data=llmArgs.retrieval_data,
            language_message=chat_language_prompt,
            references=llmArgs.references,
            mail=llmArgs.mail,
            is_report=is_report
        )

        # calculate token size
        all_message_for_calculate_token = llmArgs.system_message + str(llmArgs.conversation_history) + human_message
        llmArgs.insert_mongo["token"] = get_token_length(all_message_for_calculate_token, llmArgs.model)

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - llmArgs.start_time))
        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # for debug message
        # write_log_for_debug_message(
        #     system_message=llmArgs.system_message,
        #     conversation_history=llmArgs.conversation_history,
        #     human_message=human_message
        # )

        is_first_chunk = True
        is_changing_vendor = False
        is_changing_model = False
        async for llmArgs.response in llmArgs.llm_proxy_client.stream(
            service=llmArgs.service or DEFAULT,
            vendor=llmArgs.vendor,
            model=llmArgs.model,
            system_message=llmArgs.system_message,
            conversation_history=llmArgs.conversation_history,
            human_message=human_message,
            time=float(llmArgs.start_time),
            session_key=llmArgs.session_key
        ):
            if llmArgs.response and isinstance(llmArgs.response, GroxyStreamingResponse):
                if is_first_chunk:
                    is_first_chunk = False
                    if llmArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=int(time_from_proxy - llmArgs.start_time))
                        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                text = getattr(llmArgs.response, "text", None)
                if text:
                    yield text
                    llmArgs.answer += text

                vendor = getattr(llmArgs.response, "vendor", None)
                if not is_changing_vendor and vendor:
                    llmArgs.vendor = vendor
                    is_changing_vendor = True

                model = getattr(llmArgs.response, "model", None)
                if not is_changing_model and model:
                    llmArgs.model = model
                    is_changing_model = True

                is_error = getattr(llmArgs.response, "is_error", None)
                if is_error:
                    llmArgs.answer = LANG_JA_ERR_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                    for word in llmArgs.answer:
                        yield word
                    llmArgs.is_error = True
                    err_message = "LLM-PROXY send Error. Both initial attempt and retry failed."
                    logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 LLMStreamingError: {err_message}")
                    if llmArgs.message_client:
                        message = f"🔴 session_key: {llmArgs.session_key}, category: {llmArgs.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
                        await llmArgs.message_client.send_message(channel='casual', message=message)

        # 완료 후 스테이징 모델 정보 전달
        finish_condition=os.getenv('SERVER_STAGE', None) != PRODUCTION and is_changing_vendor and is_changing_model and llmArgs.service not in [JOURNEYMAP_DASHBOARD, JOURNEYMAP_AIREPORT_STAGING]
        if finish_condition:
            added_message = f"\n\n![]('{llmArgs.vendor}:{llmArgs.model}')"
            for word in added_message:
                yield word

        # 콜백
        await callback(llmArgs)

    except DBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except VectorDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except AWSError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except LLMStreamingError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 LLMStreamingError: {e.message}")
        raise LLMStreamingError(e.message)
    except Exception as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_voc_llm] 🔴 Exception: {e}")
        raise e



async def run_docent_llm(llmArgs:LLMArgs):
    try:
        is_report = llmArgs.agent in REPORT_LIST

        # multi Language: question is set on api layer, side
        if llmArgs.is_report_chat_init and llmArgs.lang:
            chat_language_prompt = LANG_JA_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_MESSAGE
        else:
            chat_language_prompt = LANG_CHAT_PROMPT

        # set user_message
        human_message = make_human_message(
            question=llmArgs.question,
            retrieval_data=llmArgs.retrieval_data,
            language_message=chat_language_prompt,
            selected_report_data=llmArgs.selected_report_data,
            is_report=is_report
        )

        # calculate token size
        all_message_for_calculate_token = llmArgs.system_message + str(llmArgs.conversation_history) + human_message
        llmArgs.insert_mongo["token"] = get_token_length(all_message_for_calculate_token, llmArgs.model or BASE_MODEL)

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - llmArgs.start_time))
        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # for debug message
        # write_log_for_debug_message(
        #     system_message=llmArgs.system_message,
        #     conversation_history=llmArgs.conversation_history,
        #     human_message=human_message
        # )

        is_first_chunk = True
        is_changing_vendor = False
        is_changing_model = False
        async for llmArgs.response in llmArgs.llm_proxy_client.stream(
            service=llmArgs.service or DEFAULT,
            vendor=llmArgs.vendor or OPENAI,
            model=llmArgs.model or BASE_MODEL,
            system_message=llmArgs.system_message,
            conversation_history=llmArgs.conversation_history,
            human_message=human_message,
            time=float(llmArgs.start_time),
            session_key=llmArgs.session_key
        ):
            if llmArgs.response and isinstance(llmArgs.response, GroxyStreamingResponse):
                if is_first_chunk:
                    is_first_chunk = False
                    if not getattr(llmArgs.response, "is_error", None):
                        filter_query = {"_id": llmArgs.insert_id}
                        update_query = {"$set": {"answeredStartDate": datetime.now(timezone.utc)}}
                        await llmArgs.main_db_client.update_one(collection="solomonChatHistory", filter=filter_query, update=update_query)
                    if llmArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=int(time_from_proxy - llmArgs.start_time))
                        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                text = getattr(llmArgs.response, "text", None)
                if text:
                    yield text
                    llmArgs.answer += text

                vendor = getattr(llmArgs.response, "vendor", None)
                if not is_changing_vendor and vendor:
                    llmArgs.vendor = vendor
                    is_changing_vendor = True

                model = getattr(llmArgs.response, "model", None)
                if not is_changing_model and model:
                    llmArgs.model = model
                    is_changing_model = True

                is_error = getattr(llmArgs.response, "is_error", None)
                if is_error:
                    llmArgs.answer = LANG_JA_ERR_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                    for word in llmArgs.answer:
                        yield word
                    llmArgs.is_error = True
                    err_message = "LLM-PROXY send Error. Both initial attempt and retry failed."
                    logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 LLMStreamingError: {err_message}")
                    if llmArgs.message_client:
                        message = f"🔴 session_key: {llmArgs.session_key}, category: {llmArgs.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
                        await llmArgs.message_client.send_message(channel='casual', message=message)


        # 완료 후 스테이징 모델 정보 전달
        finish_condition=os.getenv('SERVER_STAGE', None) != PRODUCTION and is_changing_vendor and is_changing_model and llmArgs.service not in [JOURNEYMAP_DASHBOARD, JOURNEYMAP_AIREPORT_STAGING]
        if finish_condition:
            added_message = f"\n\n![]('{llmArgs.vendor}:{llmArgs.model}')"
            for word in added_message:
                yield word

        # 콜백
        await callback(llmArgs)

    except DBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except VectorDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except AWSError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except LLMStreamingError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 LLMStreamingError: {e.message}")
        raise LLMStreamingError(e.message)
    except Exception as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_docent_llm] 🔴 Exception: {e}")
        raise e


async def run_schematag_llm(llmArgs:LLMArgs):
    try:
        is_report = llmArgs.agent in REPORT_LIST

        # set user message
        chat_language_prompt = LANG_JA_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_MESSAGE
        human_message = make_human_message(
            question=llmArgs.question,
            retrieval_data=llmArgs.retrieval_data,
            language_message=chat_language_prompt,
            is_report=is_report
        )

        # calculate token size
        all_message_for_calculate_token = llmArgs.system_message + str(llmArgs.conversation_history) + human_message
        llmArgs.insert_mongo["token"] = get_token_length(all_message_for_calculate_token, llmArgs.model)

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - llmArgs.start_time))
        logging.info(f"[TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # for debug message
        # write_log_for_debug_message(
        #     system_message=llmArgs.system_message,
        #     conversation_history=llmArgs.conversation_history,
        #     human_message=human_message
        # )

        is_first_chunk = True
        is_changing_vendor = False
        is_changing_model = False
        async for llmArgs.response in llmArgs.llm_proxy_client.stream(
                service=llmArgs.service or DEFAULT,
                vendor=llmArgs.vendor,
                model=llmArgs.model,
                system_message=llmArgs.system_message,
                conversation_history=llmArgs.conversation_history,
                human_message=human_message,
                time=float(llmArgs.start_time),
                session_key=llmArgs.session_key,
        ):
            if llmArgs.response and isinstance(llmArgs.response, GroxyStreamingResponse):
                if is_first_chunk:
                    is_first_chunk = False
                    if llmArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=int(time_from_proxy - llmArgs.start_time))
                        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                text = getattr(llmArgs.response, "text", None)
                if text:
                    yield text
                    llmArgs.answer += text

                vendor = getattr(llmArgs.response, "vendor", None)
                if not is_changing_vendor and vendor:
                    llmArgs.vendor = vendor
                    is_changing_vendor = True

                model = getattr(llmArgs.response, "model", None)
                if not is_changing_model and model:
                    llmArgs.model = model
                    is_changing_model = True

                is_error = getattr(llmArgs.response, "is_error", None)
                if is_error:
                    llmArgs.answer = LANG_JA_ERR_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                    for word in llmArgs.answer:
                        yield word
                    llmArgs.is_error = True
                    err_message = "LLM-PROXY send Error. Both initial attempt and retry failed."
                    logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_schematag_llm] 🔴 LLMStreamingError: {err_message}")
                    if llmArgs.message_client:
                        message = f"🔴 session_key: {llmArgs.session_key}, category: {llmArgs.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
                        await llmArgs.message_client.send_message(channel='casual', message=message)

        # 완료 후 스테이징 모델 정보 전달
        finish_condition=os.getenv('SERVER_STAGE', None) != PRODUCTION and is_changing_vendor and is_changing_model and llmArgs.service not in [JOURNEYMAP_DASHBOARD, JOURNEYMAP_AIREPORT_STAGING]
        if finish_condition:
            added_message = f"\n\n![]('{llmArgs.vendor}:{llmArgs.model}')"
            for word in added_message:
                yield word

        # 콜백
        await callback(llmArgs)

    except DBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_schematag_llm] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_schematag_llm] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except VectorDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_schematag_llm] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except AWSError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_schematag_llm] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except LLMStreamingError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_schematag_llm] 🔴 LLMStreamingError: {e.message}")
        raise LLMStreamingError(e.message)
    except Exception as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 Exception: {e}")
        raise e


async def run_abtest_llm(llmArgs:LLMArgs):
    try:
        is_report = llmArgs.agent in REPORT_LIST

        # set user message
        chat_language_prompt = LANG_JA_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_MESSAGE
        human_message = make_human_message(
            question=llmArgs.question,
            retrieval_data=llmArgs.retrieval_data,
            language_message=chat_language_prompt,
            is_report=is_report
        )

        # calculate token size
        all_message_for_calculate_token = llmArgs.system_message + str(llmArgs.conversation_history) + human_message
        llmArgs.insert_mongo["token"] = get_token_length(all_message_for_calculate_token, llmArgs.model)

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - llmArgs.start_time))
        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # for debug message
        # write_log_for_debug_message(
        #     system_message=llmArgs.system_message,
        #     conversation_history=llmArgs.conversation_history,
        #     human_message=human_message
        # )

        is_first_chunk = True
        is_changing_vendor = False
        is_changing_model = False
        async for llmArgs.response in llmArgs.llm_proxy_client.stream(
            service=llmArgs.service or DEFAULT,
            vendor=llmArgs.vendor,
            model=llmArgs.model,
            system_message=llmArgs.system_message,
            conversation_history=llmArgs.conversation_history,
            human_message=human_message,
            time=float(llmArgs.start_time),
            session_key=llmArgs.session_key
        ):
            if llmArgs.response and isinstance(llmArgs.response, GroxyStreamingResponse):
                if is_first_chunk:
                    is_first_chunk = False
                    if llmArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=int(time_from_proxy - llmArgs.start_time))
                        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                text = getattr(llmArgs.response, "text", None)
                if text:
                    yield text
                    llmArgs.answer += text

                vendor = getattr(llmArgs.response, "vendor", None)
                if not is_changing_vendor and vendor:
                    llmArgs.vendor = vendor
                    is_changing_vendor = True

                model = getattr(llmArgs.response, "model", None)
                if not is_changing_model and model:
                    llmArgs.model = model
                    is_changing_model = True

                is_error = getattr(llmArgs.response, "is_error", None)
                if is_error:
                    llmArgs.answer = LANG_JA_ERR_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                    for word in llmArgs.answer:
                        yield word
                    llmArgs.is_error = True
                    err_message = "LLM-PROXY send Error. Both initial attempt and retry failed."
                    logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 LLMStreamingError: {err_message}")
                    if llmArgs.message_client:
                        message = f"🔴 session_key: {llmArgs.session_key}, category: {llmArgs.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
                        await llmArgs.message_client.send_message(channel='casual', message=message)

        # 완료 후 스테이징 모델 정보 전달
        finish_condition=os.getenv('SERVER_STAGE', None) != PRODUCTION and is_changing_vendor and is_changing_model and llmArgs.service not in [JOURNEYMAP_DASHBOARD, JOURNEYMAP_AIREPORT_STAGING]
        if finish_condition:
            added_message = f"\n\n![]('{llmArgs.vendor}:{llmArgs.model}')"
            for word in added_message:
                yield word

        # 콜백
        await callback(llmArgs)

    except DBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except VectorDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except AWSError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except LLMStreamingError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 LLMStreamingError: {e.message}")
        raise LLMStreamingError(e.message)
    except Exception as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_abtest_llm] 🔴 Exception: {e}")
        raise e


async def run_dashboard_llm(llmArgs:LLMArgs):
    try:
        # question
        human_message = make_human_message(question=llmArgs.question, dashboard_data=llmArgs.dashboard_data)

        # calculate token size
        token_length = llmArgs.system_message + str(llmArgs.conversation_history) + human_message
        llmArgs.insert_mongo["token"] = get_token_length(token_length, llmArgs.model)

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - llmArgs.start_time))
        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # write_log_for_debug_message(
        #     system_message=llmArgs.system_prompt,
        #     conversation_history=llmArgs.conversation_history,
        #     question=human_message
        # )

        is_first_chunk = True
        is_changing_vendor = False
        is_changing_model = False
        async for llmArgs.response in llmArgs.llm_proxy_client.stream(
                service=llmArgs.service,
                vendor=llmArgs.vendor,
                model=llmArgs.model,
                system_message=llmArgs.system_message,
                human_message=human_message,
                time=float(llmArgs.start_time),
                session_key=llmArgs.session_key,
        ):
            if llmArgs.response and isinstance(llmArgs.response, GroxyStreamingResponse):
                if is_first_chunk:
                    is_first_chunk = False
                    if llmArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=int(time_from_proxy - llmArgs.start_time))
                        logging.info(f"session_key: {llmArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                text = getattr(llmArgs.response, "text", None)
                if text:
                    yield text
                    llmArgs.answer += text

                vendor = getattr(llmArgs.response, "vendor", None)
                if not is_changing_vendor and vendor:
                    llmArgs.vendor = vendor
                    is_changing_vendor = True

                model = getattr(llmArgs.response, "model", None)
                if not is_changing_model and model:
                    llmArgs.model = model
                    is_changing_model = True

                is_error = getattr(llmArgs.response, "is_error", None)
                if is_error:
                    llmArgs.answer = LANG_JA_ERR_MESSAGE if llmArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if llmArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                    for word in llmArgs.answer:
                        yield word
                    llmArgs.is_error = True
                    err_message = "LLM-PROXY send Error. Both initial attempt and retry failed."
                    logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 LLMStreamingError: {err_message}")
                    if llmArgs.message_client:
                        message = f"🔴 session_key: {llmArgs.session_key}, category: {llmArgs.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
                        await llmArgs.message_client.send_message(channel='casual', message=message)

        # 완료 후 스테이징 모델 정보 전달
        finish_condition=os.getenv('SERVER_STAGE', None) != PRODUCTION and is_changing_vendor and is_changing_model and llmArgs.service not in [JOURNEYMAP_DASHBOARD, JOURNEYMAP_AIREPORT_STAGING]
        if finish_condition:
            added_message = f"\n\n![]('{llmArgs.vendor}:{llmArgs.model}')"
            for word in added_message:
                yield word

        # 결과 변환
        remove_code_blocks(llmArgs)
        remove_escape_in_html_str(llmArgs)

        # 엣지 에이전트 테스트 중
        # edge_tasks = [agent_http_validate(llmArgs), agent_dashboard_data_validate(llmArgs)]
        # await asyncio.gather(*edge_tasks)

        # 콜백 실행
        await callback(llmArgs)

    except DBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 DBError: {e}")
        raise DBError(e)
    except MemoryDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 MemoryDBError: {e}")
        raise MemoryDBError(e)
    except VectorDBError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 VectorDBError: {e}")
        raise VectorDBError(e)
    except AWSError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 AWSError: {e}")
        raise AWSError(e)
    except LLMStreamingError as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 LLMStreamingError: {e}")
        raise LLMStreamingError(e)
    except Exception as e:
        logging.error(f"session_key: {llmArgs.session_key} | [module.llm.run.run_dashboard_llm] 🔴 Exception: {e}")
        raise e


async def callback(args:LLMArgs):
    try:
        # time
        end_time = time.time()
        elapsed = timedelta(seconds=int(end_time - args.start_time))
        logging.info(f"[TIMETEST] ⏱️ TIME to callback: {elapsed}")

        # err check
        if args.is_error:
            args.insert_mongo["isError"] = True
            args.insert_mongo["llmProxyError"] = True

        # question io
        question_task = []
        data_mongo = mongo_format(args.session_key, ROLE_HUMAN, args.question, args.insert_mongo)
        if args.agent in DOCENT_LIST:
            update = {"$set": data_mongo}
            if args.is_error:
                unset_field_name = "baAIReportId" if args.agent in DOCENT_JOURNEY_LIST else "geoAIReportId" if args.agent in DOCENT_GEO_LIST else "beusAIReportId"
                data_mongo.pop(unset_field_name, None)
                data_mongo.pop("answeredStartDate", None)
                update["$unset"] = {unset_field_name: "", "answeredStartDate": ""}
            question_task.append(args.main_db_client.update_one(collection=CHAT_COLLECTION, filter={"_id": args.insert_id}, update=update))
        else:
            question_task.append(args.main_db_client.insert_one(collection=CHAT_COLLECTION, document=data_mongo))
        if args.redis_save:
            question_task.append(save_to_memory_db(args.memory_db_client, args.session_key, args.question, "human"))
        result = await asyncio.gather(*question_task)
        args.insert_mongo["cid"] = str(args.insert_id) if args.agent in DOCENT_LIST else str(result[0].inserted_id)

        # answer io
        enum = args.insert_mongo.get("order", None) if args.s3_save else None
        args.insert_mongo['vendor'] = args.vendor
        args.insert_mongo['model'] = args.model

        answer_task = [save_answer_to_main_db(args.main_db_client, args.session_key, args.answer, args.model, args.insert_mongo, args.indepth, "ai", args.ask_id)]
        if args.redis_save:
            answer_task.append(save_to_memory_db(args.memory_db_client, args.session_key, args.answer, "ai", args.ask_id))
        if args.s3_save:
            answer_task.append(save_s3(main_db_client=args.main_db_client, s3_client=args.s3_client, s3_save=args.s3_save, data=args.answer, enum=enum))
        await asyncio.gather(*answer_task)

    except DBError as e:
        logging.error(f"session_key: {args.session_key} | [module.llm.run.callback] 🔴 DBError: {e.message}")
    except MemoryDBError as e:
        logging.error(f"session_key: {args.session_key} | [module.llm.run.callback] 🔴 MemoryDBError: {e.message}")
    except AWSError as e:
        logging.error(f"session_key: {args.session_key} | [module.llm.run.callback] 🔴 AWSError: {e.message}")
    except Exception as e:
        logging.error(f"session_key: {args.session_key} | [module.llm.run.callback] 🔴 Exception: {e}")
