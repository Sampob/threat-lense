from app import redis_client
from app.celery_worker import celery
from app.config import Config
from app.sources.base_source import SourceFactory, BaseSource
from app.utils.cache import generate_cache_key, cache_results
from app.utils.logger import app_logger

import asyncio
from asyncio import Semaphore

semaphore = Semaphore(Config.MAX_CONCURRENT_REQUESTS)

@celery.task(bind=True)
def search_task(indicator: str):
    app_logger.info(f"Starting search task for '{indicator}'")
    asyncio.run(main_task(indicator))

async def main_task(indicator: str):
    # Generate cache key
    cache_key = generate_cache_key(indicator)

    # Check for cached results
    cached_results = redis_client.get(cache_key)
    if cached_results:
        app_logger.info(f"Cached result found for '{indicator}', returning cached result")
        return handle_result(cached_results)

    app_logger.info(f"No cached result found for '{indicator}', proceeding to searching")

    sources = SourceFactory.create_sources()

    # List to store results
    results = []

    async def query_source(source: BaseSource):
        async with semaphore:
            try:
                return await source.fetch_intel(indicator)
            except Exception as e:
                app_logger.error(f"Error fetching data from {source.__class__.__name__}: {e}")
                return None
    
    tasks = [query_source(source) for source in sources]
    results = await asyncio.gather(*tasks)
    
    results = [result for result in results if result is not None]
    
    # Cache results
    cache_results(cache_key, results, expiration=Config.CACHE_EXPIRATION)

    return handle_result(results)

def handle_result(results):
    app_logger.info(f"Returning results: {results}")
    return results