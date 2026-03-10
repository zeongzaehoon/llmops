from fastapi import APIRouter

from client.google import GoogleFileSearchClient
from client.bedrock import S3Client
from helper.file import *
from models.file import *
from utils.error import *
from utils.response import *
from utils.paths import TMP_DIR



file = APIRouter(prefix="/file")



@file.post("/create_store")
@handle_errors()
async def create_store(payload: CreateStorePayload):
    try:
        # client
        google_client = GoogleFileSearchClient(file_data=payload)

        # request to google for creating FileSearch store
        store_name = await google_client.create_file_search_store(display_name=payload.display_name)

        # response
        data = {"storeName": store_name}
        return Response200(data=data).to_orjson()

    except Exception as e:
        logging.error(f"[api.file.create_store] ERROR: {e}")
        raise FileError


@file.post("/get_stores")
@handle_errors()
async def get_stores(payload: GetStoresPayload):
    try:
        # client
        google_client = GoogleFileSearchClient(file_data=payload)

        # request to google for getting FileSearch store list
        stores:list = await google_client.get_list_file_search_store()

        # response
        data = {"stores": stores}
        return Response200(data=data).to_orjson()

    except Exception as e:
        logging.error(f"[api.file.get_stores] ERROR: {e}")
        raise FileError


@file.post("/import_files")
@handle_errors()
async def import_files(payload: ImportFilePayload):
    try:
        # before getting data
        if not payload.buckets and not payload.keys and not (len(payload.buckets) == len(payload.keys)):
            raise FileError

        # set client
        s3_client = S3Client()
        google_client = GoogleFileSearchClient(file_data=payload)

        # business logic
        document_names = list()
        status = list()
        # 작업하는동안 임시 디렉토리 생성 및 유지 -> 모든 작업 완료 후 디렉토리 삭제
        with helper_import_files_temp_workspace(dir_path=TMP_DIR) as temp_dir:
            for bucket, key in zip(payload.buckets, payload.keys):
                try:
                    file_name, temp_file_path = helper_import_files_make_temp_file_path(key, temp_dir)
                    await s3_client.download_file_to_path(bucket, key, temp_file_path)

                    document_name = await google_client.upload_file_in_file_search_store(
                        store_name=payload.store_name,
                        file_path = temp_file_path,
                        file_name=file_name
                    )
                    Path(temp_file_path).unlink(missing_ok=True) # delete file after import
                    upload_result = True if document_name else False

                    document_names.append(document_name)
                    status.append(upload_result)

                except:
                    if len(document_names) == len(status):
                        document_names.append(None)
                        status.append(False)
                    else:
                        status.append(False)

        # response
        data = {"documentName": document_names, "status": status}
        return Response200(data=data).to_orjson()

    except Exception as e:
        logging.error(f"[api.file.import_files] ERROR: {e}")
        raise FileError


@file.post("get_files")
@handle_errors()
async def chat(payload: GetFilesPayload):
    try:
        # client
        google_client = GoogleFileSearchClient(file_data=payload)

        # business logic
        document_names = await google_client.get_all_file_in_file_search_store(
            store_name = payload.store_name
        )

        # response
        data = {"documentNames": document_names}
        return Response200(data=data).to_orjson()

    except Exception as e:
        logging.error(f"[api.file.get_files] ERROR: {e}")
        raise FileError


@file.post("/delete_store")
@handle_errors()
async def chat(payload: DeleteStorePayload):
    try:
        # client
        google_client = GoogleFileSearchClient(file_data=payload)

        # business logic
        await google_client.delete_file_search_store(store_name=payload.store_name)

        # response
        return Response200().to_orjson()

    except Exception as e:
        logging.error(f"[api.file.delete_store] ERROR: {e}")
        raise FileError


@file.post("/delete_document")
@handle_errors()
async def delete_document(payload: DeleteDocumentPayload):
    try:
        # client
        google_client = GoogleFileSearchClient(file_data=payload)

        # business logic
        is_single = isinstance(payload.document_name, str)
        if is_single:
            await google_client.delete_file_in_file_search_store(document_name=payload.document_name)
            data = {"status": True}
        else:
            status = []
            for document_name_str in payload.document_name:
                try:
                    await google_client.delete_file_in_file_search_store(document_name=payload.document_name_str)
                    status.append(True)
                except Exception as e:
                    logging.info(f"[helper.file.delete_document] Fail to delete document. document_name is {document_name_str} | ERROR: {e}")
                    status.append(False)
            data = {"status": status}

        # response
        return Response200(data=data).to_orjson()

    except Exception as e:
        logging.error(f"[api.file.delete_document] ERROR: {e}")
        raise FileError