import os
import logging
import asyncio
from dataclasses import dataclass
from pinecone.grpc import PineconeGRPC
from utils.error import VectorDBError
from utils.constants import MAIN_INDEX

@dataclass
class PineconeClientConnector:
    _client: PineconeGRPC | None = None
    _index = None
    _current_index_name = None
    _lock = asyncio.Lock()

    @classmethod
    async def connect(cls):
        async with cls._lock:
            if cls._client is None:
                try:
                    cls._client = PineconeGRPC(api_key=os.getenv("PINECONE_API_KEY"))
                    logging.info("✅ Pinecone connected")
                except Exception as e:
                    logging.error(f"[PineconeClient.connect] 🔴 Exception: {e}")
                    raise VectorDBError(f"Failed to connect to Pinecone: {e}")


    @classmethod
    async def disconnect(cls):
        async with cls._lock:
            cls._client = None
            cls._index = None
            logging.info("🔴 Pinecone disconnected")


    @classmethod
    async def get_client(cls):
        try:
            if cls._client is None:
                await cls.connect()
                return cls._client
            else:
                return cls._client
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.check_connection] 🔴 Failed to check connection to Pinecone: {e}")
            raise VectorDBError(f"Failed to check connection to Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.check_connection] 🔴 Failed to check connection to Pinecone: {e}")
            raise VectorDBError(f"Failed to check connection to Pinecone: {e}")


    @classmethod
    async def get_index(cls, index_name):
        try:
            await cls.get_client()
            if cls._index is None or cls._current_index_name != index_name:
                cls._index = cls._client.Index(index_name)
                cls._current_index_name = index_name
            return cls._index
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.get_index] 🔴 VectorDBError: {e}")
            raise VectorDBError(f"Failed to check connection to Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.get_index] 🔴 Exception: {e}")
            raise VectorDBError(f"Failed to check connection to Pinecone: {e}")


    @classmethod
    async def initialize(cls):
        try:
            server_stage = os.getenv("SERVER_STAGE")
            if server_stage:
                index_name = MAIN_INDEX
                await cls.get_index(index_name=index_name)
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.get_index] 🔴 VectorDBError: {e}")
            raise VectorDBError(f"Failed to check connection to Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.get_index] 🔴 Exception: {e}")
            raise VectorDBError(f"Failed to check connection to Pinecone: {e}")



@dataclass
class PineconeClient:
    index_name: str
    namespace: str | list | tuple | None = None

    async def get_index(self):
        try:
            self.idx = await PineconeClientConnector.get_index(index_name=self.index_name)
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.get_index] 🔴 Failed to get index: {e}")
            raise VectorDBError(f"Failed to get index: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.get_index] 🔴 Failed to get index: {e}")
            raise VectorDBError(f"Failed to get index: {e}")


    async def insert(self, id:str, value:str, metadata:dict, namespace:str=None):
        try:
            await self.get_index()
            vectors = [{"id": id, "values": value, 'metadata': metadata}]
            if self.namespace or namespace:
                await asyncio.to_thread(self.idx.upsert, vectors=vectors, namespace=self.namespace or namespace)
            else:
                await asyncio.to_thread(self.idx.upsert, vectors=vectors)
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.insert] 🔴 Failed to insert data to Pinecone: {e}")
            raise VectorDBError(f"Failed to insert data to Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.insert] 🔴 Failed to insert data to Pinecone: {e}")
            raise VectorDBError(f"Failed to insert data to Pinecone: {e}")


    async def insert_many(self, ids:list, values:list, metadatas:list, namespace:str=None):
        try:
            await self.get_index()
            vectors = [{"id": id, "values": value, 'metadata': metadata} for id, value, metadata in zip(ids, values, metadatas)]
            if self.namespace or namespace:
                await asyncio.to_thread(self.idx.upsert, vectors=vectors, batch_size=32, namespace=self.namespace or namespace)
            else:
                await asyncio.to_thread(self.idx.upsert, vectors=vectors, batch_size=32)
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.insert_many] 🔴 Failed to insert data to Pinecone: {e}")
            raise VectorDBError(f"Failed to insert data to Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.insert_many] 🔴 Failed to insert data to Pinecone: {e}")
            raise VectorDBError(f"Failed to insert data to Pinecone: {e}")


    async def remove(self, id:str|list=None, delete_all:bool=False, filter:dict=None):
        try:
            await self.get_index()
            if id:
                await asyncio.to_thread(self.idx.delete, ids=id, namespace=self.namespace or None)
            elif id is None and filter is not None:
                await asyncio.to_thread(self.idx.delete, filter=filter, namespace=self.namespace or None)
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.remove] 🔴 Failed to remove data from Pinecone: {e}")
            raise VectorDBError(f"Failed to remove data from Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.remove] 🔴 Failed to remove data from Pinecone: {e}")
            raise VectorDBError(f"Failed to remove data from Pinecone: {e}")


    async def find(self, vector, k:int=4, filter:dict=None):
        try:
            await self.get_index()
            if isinstance(self.namespace, str) or not self.namespace:
                response = await asyncio.to_thread(
                    self.idx.query,
                    vector=vector,
                    top_k=k,
                    include_values=False,
                    include_metadata=True,
                    filter=filter,
                    namespace=self.namespace or None
                )
                if hasattr(response, "matches"):
                    sorted_matches = sorted(response.matches, key=lambda x: x.score, reverse=True)
                else:
                    sorted_matches = sorted(response['matches'], key=lambda x: x['score'], reverse=True)

            elif isinstance(self.namespace, list) or isinstance(self.namespace, tuple):
                task_list = list()
                for namespace in self.namespace:
                    task_list.append(
                        asyncio.to_thread(
                            self.idx.query.query,
                            vector=vector,
                            top_k=k,
                            include_values=False,
                            include_metadata=True,
                            filter=filter,
                            namespace=namespace
                        )
                    )
                all_responses = await asyncio.gather(*task_list)
                sorted_matches_before_sort = list()
                for response in all_responses:
                    if hasattr(response, "matches"):
                        sorted_matches_before_sort.extend(response.matches)
                    else:
                        sorted_matches_before_sort.extend(response['matches'])
                sorted_matches = sorted(sorted_matches_before_sort, key=lambda x: x.score, reverse=True)

            else:
                raise Exception(f"namespace must be str, list, tuple when query. but the type of namespace is {type(self.namespace)}")

            return sorted_matches
        except VectorDBError as e:
            logging.error(f"[client.pinecone.PineconeClient.find] 🔴 VectorDBError: {e}")
            raise VectorDBError(f"Failed to find data in Pinecone: {e}")
        except Exception as e:
            logging.error(f"[client.pinecone.PineconeClient.find] 🔴 Exception: {e}")
            raise VectorDBError(f"Failed to find data in Pinecone: {e}")


    async def fetch(self, ids:list, namespace:str=None):
        try:
            await self.get_index()
            response = await asyncio.to_thread(self.idx.fetch, ids=ids, namespace=self.namespace or namespace)
            return response
        except VectorDBError as e:
            logging.info(f"[client.pinecone.PineconeClient.fetch] 🔴 Failed to fetch data from Pinecone: {e}")
            raise VectorDBError(f"Failed to fetch data from Pinecone: {e}")
        except Exception as e:
            logging.info(f"[client.pinecone.PineconeClient.fetch] 🔴 Failed to fetch data from Pinecone: {e}")
            raise VectorDBError(f"Failed to fetch data from Pinecone: {e}")
