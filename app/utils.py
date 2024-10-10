from app import redis_client
from app.config import Config

import hashlib
import json

def generate_cache_key(indicator):
    """Generate a unique key based on query parameter."""
    return hashlib.md5(indicator.encode()).hexdigest()

def fetch_from_cache(key):
    """Fetch results from Redis."""
    return redis_client.get(key)

def cache_results(key, data, expiration=Config.CACHE_EXPIRATION):
    """Cache results in Redis with expiration."""
    redis_client.setex(key, expiration, json.dumps(data))

def process_data(data):
    """Modify the API response data as needed."""
    return {
        "name": data.get("name"),
        "link": data.get("link"),
        "verdict": data.get("verdict", "unknown"),
        "data": data.get("data"),
        "raw": data.get("raw")
    }
