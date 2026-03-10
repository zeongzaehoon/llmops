import os
import logging

from redis.asyncio import Redis

from utils.error import MemoryDBError


class RedisClient:
    """
    인스턴스 기반 Redis 클라이언트
    - lifespan에서 connect()로 초기화
    - app.state에 보관 → Depends()로 주입
    """

    def __init__(self):
        self._redis: Redis | None = None

    async def connect(self):
        if self._redis is not None:
            return
        try:
            self._redis = await Redis(
                host=os.getenv("MEMORY_DB_HOST"),
                port=os.getenv("MEMORY_DB_PORT"),
                db=os.getenv("MEMORY_DB_NUMBER"),
                decode_responses=True
            )
            logging.info("✅ on Redis")
        except Exception as e:
            logging.error(f"[RedisClient.connect] 🔴 Failed to connect Redis: {e}")
            raise MemoryDBError(f"Failed to connect Redis: {e}")

    async def disconnect(self):
        if self._redis:
            try:
                await self._redis.close()
                self._redis = None
                logging.info("🔴 off Redis")
            except Exception as e:
                logging.error(f"[RedisClient.disconnect] 🔴 Failed to disconnect Redis: {e}")
                raise MemoryDBError(f"Failed to disconnect Redis: {e}")

    async def set(self, key: str, value: str):
        try:
            async with self._redis.client() as conn:
                await conn.set(key, value)
        except Exception as e:
            logging.error(f"[RedisClient.set] 🔴 {e}")
            raise MemoryDBError(f"Failed to set data in Redis: {e}")

    async def rpush(self, key: str, value: str):
        try:
            async with self._redis.client() as conn:
                await conn.rpush(key, value)
        except Exception as e:
            logging.error(f"[RedisClient.rpush] 🔴 {e}")
            raise MemoryDBError(f"Failed to push data into Redis: {e}")

    async def set_with_expire(self, key: str, value: str, expire: int):
        try:
            async with self._redis.client() as conn:
                await conn.set(key, value, ex=expire)
        except Exception as e:
            logging.error(f"[RedisClient.set_with_expire] 🔴 {e}")
            raise MemoryDBError(f"Failed to set data in Redis: {e}")

    async def set_expire(self, key: str, time: int):
        try:
            async with self._redis.client() as conn:
                await conn.expire(key, time)
        except Exception as e:
            logging.error(f"[RedisClient.set_expire] 🔴 {e}")
            raise MemoryDBError(f"Failed to set data in Redis: {e}")

    async def get(self, key: str):
        try:
            async with self._redis.client() as conn:
                return await conn.get(key)
        except Exception as e:
            logging.error(f"[RedisClient.get] 🔴 {e}")
            raise MemoryDBError(f"Failed to get data in Redis: {e}")

    async def lrange(self, key: str, start: int = 0, end: int = -1):
        try:
            async with self._redis.client() as conn:
                return await conn.lrange(key, start, end)
        except Exception as e:
            logging.error(f"[RedisClient.lrange] 🔴 {e}")
            raise MemoryDBError(f"Failed to get data in Redis: {e}")

    async def llen(self, key: str):
        try:
            async with self._redis.client() as conn:
                return await conn.llen(key)
        except Exception as e:
            logging.error(f"[RedisClient.llen] 🔴 {e}")
            raise MemoryDBError(f"Failed to get data in Redis: {e}")

    async def delete(self, key: str):
        try:
            async with self._redis.client() as conn:
                await conn.delete(key)
        except Exception as e:
            logging.error(f"[RedisClient.delete] 🔴 {e}")
            raise MemoryDBError(f"Failed to delete data in Redis: {e}")
