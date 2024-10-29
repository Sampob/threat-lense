import hashlib
import json

from app.config import Config
from app.utils.logger import setup_logger

import redis

logger = setup_logger(__name__)

# Create a Redis connection
redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

def generate_cache_key(indicator: str) -> str:
    """ Generate a unique key based on query parameter. """
    logger.info(f"Creating cache key for {indicator}")
    return hashlib.md5(indicator.encode()).hexdigest()

def fetch_from_cache(key: str) -> str:
    """ Fetch results from Redis. """
    logger.info(f"Fetching results from Redis for key: {key}")
    return redis_client.get(key)

def cache_results(key: str, data: str | dict, expiration: int=Config.CACHE_EXPIRATION) -> None:
    """ Cache results in Redis with expiration. """
    logger.info(f"Caching data to redis with key: {key}")
    if isinstance(data, dict):
        data = json.dumps(data)
    redis_client.setex(key, expiration, data)

def delete_from_cache(key: str) -> None:
    """ Remove an entry from Redis """
    logger.info(f"Removing entry from Redis with key: {key}")
    redis_client.delete(key)

def flush_cache() -> None:
    """ Remove all entries from the current Redis database. """
    logger.warning(f"FLUSHING current Redis database")
    redis_client.flushdb()