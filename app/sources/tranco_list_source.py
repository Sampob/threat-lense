from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

import aiohttp

logger = setup_logger(__name__)

class TrancoListSource(BaseSource):
    def __init__(self):
        super().__init__(url="https://tranco-list.eu/api/ranks/domain/", name="Tranco", requires_api_key=False)
        
    async def fetch_domain_intel(self, indicator: str) -> dict:
        domain_url = self.url + indicator
        
        try:
            response = await self.http_request(domain_url)
        except aiohttp.ClientResponseError as e:
            logger.error(f"ClientResponseError: {str(e)}")
            return self.format_error(self.create_url(indicator), message=e.message, status_code=e.status)
        except aiohttp.ClientError as e:
            logger.error(f"ClientError: {str(e)}")
            return self.format_error(self.create_url(indicator), message=str(e))
        except RuntimeError as e:
            logger.error(f"RuntimeError: {str(e)}")
            return self.format_error(self.create_url(indicator), message=str(e))
        except TimeoutError as e:
            logger.error(f"TimeoutError: {str(e)}")
            error_message = str(e)
            if hasattr(e, "message"):
                error_message = str(e.message)
            status = None
            if hasattr(e, "status"):
                status = e.status
            return self.format_error(self.create_url(indicator), message=str(e), status_code=status)
        except Exception as e:
            error_message = str(e)
            if hasattr(e, "message"):
                error_message = str(e.message)
            logger.error(f"Exception: {error_message}")
            return self.format_error(self.create_url(indicator), message=error_message)
        if response:
            return self.parse_intel(response)
        return response
    
    async def fetch_ipv4_intel(self, indicator: str):
        return None
    async def fetch_ipv6_intel(self, indicator: str):
        return None
    async def fetch_url_intel(self, indicator: str):
        return None
    async def fetch_hash_intel(self, indicator: str):
        return None
    
    def create_url(self, indicator) -> str:
        return "https://tranco-list.eu/query"
    
    def parse_intel(self, intel: dict) -> dict:
        verdict = 0
        
        # Extract ranks
        ranks = [entry.get("rank") for entry in intel.get("ranks")]
        
        if ranks:
            min_rank = min(ranks)
            average_rank = round(sum(ranks) / len(ranks))
            
            # Basic logic to determine verdict
            if min_rank <= 750000:
                verdict = 1
            summary_string = f"Rank: {average_rank}"
        else:
            summary_string = "No ranking"
            verdict = 1
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(""), data=intel)
        
        return formatted_intel
