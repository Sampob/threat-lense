from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

import aiohttp

logger = setup_logger(__name__, log_file="sources.log")

class StopForumSpamSource(BaseSource):
    def __init__(self):
        super().__init__(url="http://api.stopforumspam.org/api", name="Stop Forum Spam", requires_api_key=False)
    
    async def fetch_ipv4_intel(self, ip: str) -> dict:
        return await self.fetch_ip_intel(ip)
    
    async def fetch_ipv6_intel(self, ip: str) -> dict:
        return await self.fetch_ip_intel(ip)
    
    async def fetch_ip_intel(self, indicator: str) -> dict:
        search_url = f"{self.url}?ip={indicator}"
        
        try:
            response = await self.http_request(search_url)
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
    
    async def fetch_domain_intel(self, indicator: str):
        return None
    async def fetch_url_intel(self, indicator: str):
        return None
    async def fetch_hash_intel(self, indicator: str):
        return None
    
    def create_url(self, indicator):
        return f"{self.url}?ip={indicator}"
    
    def parse_intel(self, intel: dict) -> dict:
        verdict = 0
        response = intel.get("response")
                        
        appears = response.get("appears", "")
        if appears == "yes":
            last_seen = response.get("lastseen")
            verdict = 1
        frequency = response.get("frequency")
        
        if int(frequency) > 5:
            verdict += 1
        elif int("frequency") > 20:
            verdict += 2
        
        summary_string = f"Appears: {appears}, frequency: {frequency}"
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(""), data=response)
        
        return formatted_intel