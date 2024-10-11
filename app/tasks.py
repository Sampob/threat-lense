from app import redis_client
from app.celery_worker import celery
from app.utils import generate_cache_key, cache_results, process_data
from app.config import Config
from app.logger import app_logger

import threading, requests

@celery.task(bind=True)
def search_task(self, indicator: str):
    app_logger.info(f"Starting search task for '{indicator}'")
    # Generate cache key
    cache_key = generate_cache_key(indicator)

    # Check for cached results
    cached_results = redis_client.get(cache_key)
    if cached_results:
        app_logger.info(f"Cached result found for '{indicator}', returning cached result")
        return handle_returning(cached_results)

    app_logger.info(f"No cached result found for '{indicator}', proceeding to searching")

    sources = [
        {"test": 123},
        {"test": 234},
        {"test": 345},
        {"test": 456},
        {"test": indicator}
    ]

    # List to store results
    results = []

    def fetch_data(source):
        results.append(source["test"])

    # Create threads to make concurrent API calls
    threads = [threading.Thread(target=fetch_data, args=(source,)) for source in sources]

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    # Cache results
    cache_results(cache_key, results, expiration=Config.CACHE_EXPIRATION)

    app_logger.info(f"Returning results: {results}")
    return handle_returning(results)

def handle_returning(results):
    app_logger.info(f"Returning results: {results}")
    return results