from client.pinecone import PineconeClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from utils.error import *
from payload.vector import upsertPayload



async def helper_upsert(vector_db_client:PineconeClient, llm_proxy_client:LLMProxyClient, payload:upsertPayload, server_stage:str):
    try:
        # parse payload
        logging.info(f"[helper.vector.helper_upsert] 3. parse payload")
        id:str = payload.id
        content:str = payload.content
        metadata:dict = payload.metadata

        # translate metadata int to boolean. isOn, isShow
        logging.info(f"[helper.vector.helper_upsert] 4. translate metadata int to boolean. isOn, isShow")
        has_isOn = True if metadata.get('isOn') is not None and isinstance(metadata['isOn'], (int, bool)) else False
        has_isShow = True if metadata.get('isShow') is not None and isinstance(metadata['isShow'], (int, bool)) else False

        # input boolean to metadata
        if has_isOn:
            metadata['isOn'] = bool(metadata['isOn'])
        if has_isShow:
            metadata['isShow'] = bool(metadata['isShow'])

        service = CS_PRODUCTION if server_stage == PRODUCTION else CS_STAGING
        value = await llm_proxy_client.embeddings(content, service=service)

        # insert to vector db
        logging.info(f"[helper.vector.helper_upsert] 7. start to insert to vector db")
        await vector_db_client.insert(id=id, value=value, metadata=metadata)
        logging.info(f"[helper.vector.helper_upsert] 8. end to insert to vector db")

    except VectorDBError as e:
        logging.info(f"[helper.vector.helper_upsert] 🔴 Failed to upsert vector: {e}")
        raise VectorDBError(e)
    except Exception as e:
        logging.info(f"[helper.vector.helper_upsert] 🔴 Failed to upsert vector: {e}")
        raise Exception(e)






class PageSplitter:
    def __init__(self, page_delimiter):
        self.page_delimiter = page_delimiter

    def split(self, text):
        return text.split(self.page_delimiter)

class Page:
    def __init__(self, content, metadata):
        self.page_content = content
        self.metadata = metadata


def reform_pc_autocomplete(matches:list):
    results = [
            {
                "subject": str(match['metadata']['subject'] if not match['metadata'].get('replyId', None) else match['metadata']['text']),
                "postId": int(match['metadata']['postId']),
            }
        for match in matches]
    return results


def reform_pc_search(matches:list):
    results = [
            {
                "postId": int(match['metadata']['postId']),
                "postGroupingCodeId": int(match['metadata']['postGroupingCodeId']),
            }
        for match in matches]
    return results
