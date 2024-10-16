from app import redis_client
from app.celery_worker import celery
from app.config import Config
from app.sources.base_source import BaseSource
from app.utils.source_registry import SourceRegistry
from app.utils.cache import generate_cache_key, cache_results
from app.utils.logger import app_logger

import asyncio
from asyncio import Semaphore

semaphore = Semaphore(Config.MAX_CONCURRENT_REQUESTS)

@celery.task(bind=True)
def search_task(self, indicator: str):
    app_logger.info(f"Starting search task for {indicator}")
    return asyncio.run(main_task(indicator))

async def main_task(indicator: str):
    # Generate cache key
    cache_key = generate_cache_key(indicator)

    # Check for cached results
    cached_results = redis_client.get(cache_key)
    if cached_results:
        app_logger.info(f"Cached result found for {indicator}, returning cached result")
        return handle_result(cached_results)

    app_logger.info(f"No cached result found for {indicator}, proceeding to searching")

    sources = SourceRegistry.get_instance()
    
    # List to store results
    results = []
    encountered_error = False

    async def query_source(source: BaseSource):
        async with semaphore:
            try:
                return await source.fetch_intel(indicator)
            except Exception as e:
                app_logger.error(f"Error fetching data from {source.get_name()}: {e}")
                encountered_error = True
                return None
    
    tasks = [query_source(source) for source in sources.values()]
    
    results = await asyncio.gather(*tasks)
    
    results = {source.get_name(): result for source, result in zip(sources.values(), results)}
    
    # Cache results, ignore if error was encountered and empty results
    if encountered_error:
        app_logger.info("Encountered an error, skipping caching")
    elif results:
        cache_results(cache_key, results, expiration=Config.CACHE_EXPIRATION)
    else:
        app_logger.info("Empty results, skipping caching")

    return handle_result(results)

def handle_result(results):
    app_logger.info(f"Returning results: {results}")
    return results