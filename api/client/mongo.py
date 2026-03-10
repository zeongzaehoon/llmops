import os
import logging

from motor.motor_asyncio import AsyncIOMotorClient

from utils.error import DBError


class BaseMongoClient:
    """
    인스턴스 기반 MongoDB 클라이언트
    - lifespan에서 connect()로 초기화
    - app.state에 보관 → Depends()로 주입
    """

    def __init__(self):
        self._client: AsyncIOMotorClient | None = None
        self._db = None

    async def connect(self, uri: str, db_name: str = None, is_real_by_stg: bool = False):
        if self._client is not None:
            return
        try:
            if is_real_by_stg:
                self._client = AsyncIOMotorClient(uri, ssl=True)
            else:
                self._client = AsyncIOMotorClient(uri)
            self._db = self._client[db_name]
            logging.info(f"✅ on MongoDB: {db_name}")
        except Exception as e:
            logging.error(f"[BaseMongoClient.connect] 🔴 Failed to connect MongoDB: {e}")
            raise DBError(f"Failed to connect MongoDB: {e}")

    async def disconnect(self):
        if self._client:
            try:
                self._client.close()
                self._client = None
                self._db = None
                logging.info("🔴 off MongoDB")
            except Exception as e:
                logging.error(f"[BaseMongoClient.disconnect] 🔴 Failed to disconnect MongoDB: {e}")
                raise DBError(f"Failed to disconnect MongoDB: {e}")

    async def insert_one(self, collection: str, document: dict):
        try:
            return await self._db[collection].insert_one(document)
        except Exception as e:
            logging.error(f"[BaseMongoClient.insert_one] 🔴 {e}")
            raise DBError(f"Failed to insert data into MongoDB: {e}")

    async def insert_many(self, collection: str, documents: list):
        try:
            return await self._db[collection].insert_many(documents)
        except Exception as e:
            logging.error(f"[BaseMongoClient.insert_many] 🔴 {e}")
            raise DBError(f"Failed to insert data into MongoDB: {e}")

    async def find_one(self, collection: str, filter: dict, sort: list = None, projection: dict = None):
        try:
            kwargs = {}
            if sort is not None:
                kwargs['sort'] = sort
            if projection is not None:
                kwargs['projection'] = projection
            return await self._db[collection].find_one(filter, **kwargs)
        except Exception as e:
            logging.error(f"[BaseMongoClient.find_one] 🔴 {e}")
            raise DBError(f"Failed to find data in MongoDB: {e}")

    async def find(self, collection: str, filter: dict, sort: list = None, skip: int = None, limit: int = None, projection: dict = None):
        try:
            cursor = self._db[collection].find(filter) if not projection else self._db[collection].find(filter, projection=projection)

            chaining_ops = {
                "sort": sort,
                "skip": skip,
                "limit": limit,
            }
            for method, arg in chaining_ops.items():
                if arg is not None:
                    cursor = getattr(cursor, method)(arg)
            return [doc async for doc in cursor]
        except Exception as e:
            logging.error(f"[BaseMongoClient.find] 🔴 {e}")
            raise DBError(f"Failed to find data in MongoDB: {e}")

    async def distinct(self, collection: str, key: str, filter: dict = None):
        try:
            return await self._db[collection].distinct(key, filter)
        except Exception as e:
            logging.error(f"[BaseMongoClient.distinct] 🔴 {e}")
            raise DBError(f"Failed to find distinct data in MongoDB: {e}")

    async def count_documents(self, collection: str, filter: dict):
        try:
            return await self._db[collection].count_documents(filter)
        except Exception as e:
            logging.error(f"[BaseMongoClient.count_documents] 🔴 {e}")
            raise DBError(f"Failed to count documents in MongoDB: {e}")

    async def update_one(self, collection: str, filter: dict, update: dict):
        try:
            return await self._db[collection].update_one(filter, update)
        except Exception as e:
            logging.error(f"[BaseMongoClient.update_one] 🔴 {e}")
            raise DBError(f"Failed to update data in MongoDB: {e}")

    async def update_many(self, collection: str, filter: dict, update: dict):
        try:
            return await self._db[collection].update_many(filter, update)
        except Exception as e:
            logging.error(f"[BaseMongoClient.update_many] 🔴 {e}")
            raise DBError(f"Failed to update data in MongoDB: {e}")

    async def delete_one(self, collection: str, filter: dict):
        try:
            return await self._db[collection].delete_one(filter)
        except Exception as e:
            logging.error(f"[BaseMongoClient.delete_one] 🔴 {e}")
            raise DBError(f"Failed to delete data in MongoDB: {e}")

    async def delete_many(self, collection: str, filter: dict):
        try:
            return await self._db[collection].delete_many(filter)
        except Exception as e:
            logging.error(f"[BaseMongoClient.delete_many] 🔴 {e}")
            raise DBError(f"Failed to delete data in MongoDB: {e}")


class MongoClient(BaseMongoClient):
    """MainDB"""
    async def initialize(self):
        uri = os.getenv("DB_URI")
        db_name = os.getenv("DB_NAME")
        await self.connect(uri, db_name)


class ProductionMongoClient(BaseMongoClient):
    """ProductionDB (used from STAGING)"""
    async def initialize(self):
        uri = os.getenv("REAL_DB_URI")
        db_name = os.getenv("REAL_DB_NAME")
        await self.connect(uri, db_name, is_real_by_stg=True)