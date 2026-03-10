import os
import logging
import asyncio
from dataclasses import dataclass
from pymilvus import MilvusClient as MilvusClientConn, MilvusException, connections, utility, Collection, FieldSchema, CollectionSchema, DataType
from pydantic import BaseModel
from utils.error import VectorDBError
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MilvusResponse(BaseModel):
    id: str|int
    score: float
    metadata: dict


@dataclass
class MilvusClientConnector:
    _client: MilvusClientConn = None
    _lock = asyncio.Lock()

    @classmethod
    async def connect(cls):
        async with cls._lock:
            if cls._client is None:
                try:
                    cls._client = MilvusClientConn(
                        uri=os.getenv("VECTOR_DB_URI", "http://vector:19530"),
                        token=os.getenv("VECTOR_DB_TOKEN", "root:Milvus"),
                    )
                    logging.info(f"✅ connected Milvus: {os.getenv('VECTOR_DB_URI')}")

                except MilvusException as e:
                    logging.error(f"[MilvusClient.connect] 🔴 MilvusException: {e}")
                    raise VectorDBError(f"Failed to connect to Milvus: {e}")
                except Exception as e:
                    logging.error(f"[MilvusClient.connect] 🔴 Exception: {e}")
                    raise VectorDBError(f"Failed to connect to Milvus: {e}")

    @classmethod
    async def disconnect(cls):
        async with cls._lock:
            cls._client = None
            logging.info(f"🔴 disconnected Milvus: {os.getenv('VECTOR_DB_URI')}")

    @classmethod
    async def get_client(cls):
        try:
            if cls._client is None:
                await cls.connect()
                return cls._client
            else:
                return cls._client
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.check_connection] 🔴 Failed to check connection to Milvus: {e}")
            raise VectorDBError(f"Failed to check connection to Milvus: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.check_connection] 🔴 Failed to check connection to Milvus: {e}")
            raise VectorDBError(f"Failed to check connection to Milvus: {e}")

@dataclass
class MilvusClient(MilvusClientConnector):
    collection_name: str = None
    namespace: str = None
    collection = None

    async def create_collection(self):
        try:
            mc = await MilvusClientConnector.get_client()

            # 스키마 생성
            schema = mc.create_schema(
                auto_id=False,
                enable_dynamic_field=True,
            )
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=10000)
            schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
            schema.add_field(field_name="metadata", datatype=DataType.JSON)
            schema.add_field(field_name="data_type", datatype=DataType.VARCHAR)
            schema.add_field(field_name="is_on", datatype=DataType.BOOL)

            # 3.3. Prepare index parameters
            index_params = mc.prepare_index_params()

            # 3.4. Add indexes
            index_params.add_index(
                field_name="id",
                index_type="AUTOINDEX"
            )

            index_params.add_index(
                field_name="vector",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            mc.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                index_params=index_params
            )

            mc.load_collection(self.collection_name)

            logging.info(f"Collection {self.collection_name} created successfully")
            return True
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.create_collection] 🔴 Failed to create collection: {e}")
            raise VectorDBError(f"Failed to create collection: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.create_collection] 🔴 Failed to create collection: {e}")
            raise VectorDBError(f"Failed to create collection: {e}")

    async def get_collection(self):
        try:
            mc = await MilvusClientConnector.get_client()

            # 컬렉션이 존재하는지 확인
            if not mc.has_collection(self.collection_name):
                await self.create_collection()
                logging.info(f"[client.milvus.MilvusClient.get_collection] ✅ Collection {self.collection_name} created successfully")

            # 컬렉션 로드
            mc.load_collection(self.collection_name)
            self.collection = mc
            return self.collection
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.get_collection] 🔴 Failed to get collection: {e}")
            raise VectorDBError(f"Failed to get collection: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.get_collection] 🔴 Failed to get collection: {e}")
            raise VectorDBError(f"Failed to get collection: {e}")

    async def insert(self, id: str, value: list, metadata: dict, data_type: str, is_on: bool, namespace: str = None):
        try:
            mc = await self.get_collection()
            data = [{
                "id": id,
                "vector": value,
                "metadata": metadata,
                "data_type": metadata.get("data_type", "post"),
                "is_on": metadata.get("is_on", True)
            }]
            result = await asyncio.to_thread(mc.insert, self.collection_name, data)
            return result
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.insert] 🔴 Failed to insert data to Milvus: {e}")
            raise VectorDBError(f"Failed to insert data to Milvus: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.insert] 🔴 Failed to insert data to Milvus: {e}")
            raise VectorDBError(f"Failed to insert data to Milvus: {e}")

    async def insert_many(self, ids: list, values: list, metadatas: list, namespace: str = None):
        try:
            mc = await self.get_collection()
            data = [{
                "id": id,
                "vector": value,
                "metadata": metadata,
                "data_type": metadata.get("data_type", "post"),
                "is_on": metadata.get("is_on", True)
            } for id, value, metadata in zip(ids, values, metadatas)]

            result = await asyncio.to_thread(mc.insert, self.collection_name, data)
            return result
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.insert_many] 🔴 Failed to insert data to Milvus: {e}")
            raise VectorDBError(f"Failed to insert data to Milvus: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.insert_many] 🔴 Failed to insert data to Milvus: {e}")
            raise VectorDBError(f"Failed to insert data to Milvus: {e}")

    async def find(self, vector: list, k: int = 4, filter: dict = None):
        try:
            mc = await self.get_collection()

            # SET filter
            filter_ = ""
            if filter:
                conditions = []
                for key, value in filter.items():
                    if key == "is_on" and value is True:
                        conditions.append(f"{key} == true")
                    elif key == "is_on" and value is False:
                        conditions.append(f"{key} == false")
                    elif key == "data_type":
                        conditions.append(f"{key} == '{value}'")

                if conditions:
                    filter_ = " AND ".join(conditions)

            # SET search logic
            search_params = {
                "metric_type": "COSINE", #L2, IP, JACCARD, HAMMING
                "params": {"nprobe": 10}
            }

            # activate
            results = await asyncio.to_thread(
                mc.search,
                collection_name=self.collection_name,
                data=[vector],
                anns_field="vector",
                search_params=search_params,
                limit=k,
                filter=filter_,
                output_fields=["metadata"]
            )

            # REFORM data
            matches = []
            for hits in results:
                for hit in hits:
                    matches.append(MilvusResponse(
                        id=hit["id"],
                        score=hit["distance"] if search_params["metric_type"] in ["COSINE", "IP"] else 1-hit["distance"],
                        metadata=hit["entity"]["metadata"]
                    ))
            sorted_matches = sorted(matches, key=lambda x: x.score, reverse=True)

            # RETURN
            return sorted_matches
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.find] 🔴 Failed to find data in Milvus: {e}")
            raise VectorDBError(f"Failed to find data in Milvus: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.find] 🔴 Failed to find data in Milvus: {e}")
            raise VectorDBError(f"Failed to find data in Milvus: {e}")

    async def fetch(self, ids: list, namespace: str = None):
        try:
            mc = await self.get_collection()
            results = await asyncio.to_thread(
                mc.get,
                collection_name=self.collection_name,
                ids=ids,
                output_fields=["vector", "metadata"]
            )

            vectors = {}
            for item in results:
                vectors[item["id"]] = {
                    "id": item["id"],
                    "values": item["vector"],
                    "metadata": item["metadata"]
                }

            return {"vectors": vectors}
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.fetch] 🔴 Failed to fetch data from Milvus: {e}")
            raise VectorDBError(f"Failed to fetch data from Milvus: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.fetch] 🔴 Failed to fetch data from Milvus: {e}")
            raise VectorDBError(f"Failed to fetch data from Milvus: {e}")

    async def remove(self, id: list = None, delete_all: bool = False, filter: dict = None):
        try:
            mc = await self.get_collection()

            if delete_all:
                # 모든 데이터 삭제
                await asyncio.to_thread(mc.delete, self.collection_name, expr="id != ''")
                logging.info(f"All records deleted from collection {self.collection_name}")
                return True
            elif id:
                # ID로 삭제
                logging.info(f"[milvus.remove] id: {id}")
                await asyncio.to_thread(mc.delete, self.collection_name, filter=f"id in {id}")
                logging.info(f"Deleted records with IDs: {id}")
                return True
            elif filter is not None:
                # 필터로 삭제
                conditions = []
                for key, value in filter.items():
                    if isinstance(value, str):
                        conditions.append(f"json_contains(metadata, '{{\"{key}\": \"{value}\"}}')")
                    else:
                        conditions.append(f"json_contains(metadata, '{{\"{key}\": {value}}}')")

                expr = " AND ".join(conditions)
                await asyncio.to_thread(mc.delete, self.collection_name, expr=expr)
                logging.info(f"Deleted records with filter: {filter}")
                return True

            return False
        except VectorDBError as e:
            logging.info(f"[client.milvus.MilvusClient.remove] 🔴 Failed to remove data from Milvus: {e}")
            raise VectorDBError(f"Failed to remove data from Milvus: {e}")
        except Exception as e:
            logging.info(f"[client.milvus.MilvusClient.remove] 🔴 Failed to remove data from Milvus: {e}")
            raise VectorDBError(f"Failed to remove data from Milvus: {e}")
