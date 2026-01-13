import json
from typing import Optional, Any
from redis import asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()


class RedisService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def set(self, key: str, value: Any, expire: int = 300):
        if not self.redis:
            await self.connect()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)

    async def delete(self, key: str):
        if not self.redis:
            await self.connect()
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key) > 0


redis_service = RedisService()
