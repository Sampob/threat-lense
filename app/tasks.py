from app.celery_worker import celery
from app.config import Config
from app.sources.base_source import BaseSource
from app.utils.source_registry import SourceRegistry
from app.utils.cache import generate_cache_key, cache_results, fetch_from_cache
from app.utils.indicator_type import get_indicator_type
from app.utils.logger import setup_logger

import asyncio

logger = setup_logger(__name__)

@celery.task(bind=True)
def search_task(self, indicator: str):
    logger.debug(f"Starting search task for {indicator}")
    return asyncio.run(main_task(indicator))

async def main_task(indicator: str):
    # Generate cache key
    cache_key = generate_cache_key(indicator)

    # Check for cached results
    cached_results = fetch_from_cache(cache_key)
    if cached_results:
        logger.debug(f"Cached result found for {indicator}, returning cached result")
        return handle_result(cached_results)

    logger.debug(f"No cached result found for {indicator}, proceeding to searching")

    sources = SourceRegistry.get_instance()
    
    # List to store results
    results = []

    indicator_type = get_indicator_type(indicator)
    logger.debug(f"Indicator type: {indicator_type.name}")

    async def query_source(source: BaseSource):
        semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_REQUESTS)
        async with semaphore:
            try:
                response = await source.fetch_intel(indicator, indicator_type)
                return response
            except Exception as e:
                logger.error(f"Error fetching data from {source.get_name()}: {e}")
                return None
    
    tasks = [query_source(source) for source in sources.values()]
    
    results = await asyncio.gather(*tasks)
    
    results = {source.get_name(): result for source, result in zip(sources.values(), results) if result}
    
    encountered_error = False
    
    for value in results.values():
        if value:
            if value.get("summary") == "error":
                encountered_error = True
                break
        else:
            encountered_error = True
            break
    
    final_result = {
        "indicator": indicator,
        "type": get_indicator_type(indicator).name,
        "sources": results
    }
    
    # Cache results, ignore if error was encountered and empty results
    if encountered_error:
        logger.info("Encountered an error, skipping caching")
    elif results:
        cache_results(cache_key, final_result, expiration=Config.CACHE_EXPIRATION)
    else:
        logger.info("Empty results, skipping caching")

    return handle_result(final_result)

def handle_result(results: dict):
    return results