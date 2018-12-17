"""
storage abstractions
"""
import aioredis

class RedisStorage:
    """storage backed by persistent redis storage"""
    def __init__(self, url):
        self.url = url
        self._redis = None

    async def init(self):
        """we need a second init function, since __init__ can't call await"""
        self._redis = await aioredis.create_redis_pool(self.url, encoding="utf-8")

    async def get_language(self, chat_id: int):
        """get the language code set for a chat"""
        return await self._redis.get("lang:" + str(chat_id))

    async def set_language(self, chat_id: int, locale: str):
        """get the language code set for a chat"""
        return await self._redis.set("lang:" + str(chat_id), locale)
