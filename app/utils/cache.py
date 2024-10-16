import hashlib
import json

from app import redis_client
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def generate_cache_key(indicator):
    """ Generate a unique key based on query parameter. """
    logger.info(f"Creating cache key for {indicator}, type: {type(indicator)}")
    return hashlib.md5(indicator.encode()).hexdigest()

def fetch_from_cache(key):
    """ Fetch results from Redis. """
    logger.info(f"Fetching results from Redis for key: {key}")
    return redis_client.get(key)

def cache_results(key, data, expiration=Config.CACHE_EXPIRATION):
    """ Cache results in Redis with expiration. """
    logger.info(f"Caching {data} to redis with key: {key}")
    redis_client.setex(key, expiration, json.dumps(data))