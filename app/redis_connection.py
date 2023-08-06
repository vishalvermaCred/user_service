from typing import Optional

from redis import Redis

from app.settings import REDIS_CONFIG as redis_config

redisCache: Optional[Redis] = None


async def init_redis():
    global redisCache
    if not redis_config:
        raise ValueError("Redis config is not set")
    if not redisCache:
        redisCache = await create_redis_connection(redis_config)


async def get_redis():
    global redisCache
    if redisCache is None:
        await init_redis()
    return redisCache


async def create_redis_connection(config):
    redisObj = Redis(host=config["HOST"], port=config["PORT"])
    return redisObj
