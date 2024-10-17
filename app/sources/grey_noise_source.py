from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

import aiohttp

logger = setup_logger(__name__, log_file="sources.log")

class GreyNoiseSource(BaseSource):
    def __init__(self):
        super().__init__("https://api.greynoise.io/v3/community/", "GreyNoise Community", requires_api_key=True)
    
    async def fetch_ipv4_intel(self, indicator: str) -> dict:
        return await self.fetch_ip_intel(indicator)
    
    async def fetch_ipv6_intel(self, indicator: str) -> dict:
        return await self.fetch_ip_intel(indicator)
    
    async def fetch_ip_intel(self, indicator: str) -> dict:
        logger.debug(f"Searching for indicator {indicator}")
        
        headers = {
            "accept": "application/json", 
            "key": self.api_key
        }
        search_url = self.url + indicator
        
        try:
            response = await self.http_request(search_url, headers=headers)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                logger.error(f"ClientResponseError GreyNoise rate-limit exceeded: {str(e)}")
                return self.format_response(summary=e.message, verdict=-100, url=self.create_url(indicator), data={})
            elif e.status == 404:
                logger.info(f"ClientResponseError indicator {indicator} not found from GreyNoise")
                return self.format_response(summary="IP not observed scanning the internet", verdict=0, url=self.create_url(indicator), data=e.text)
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
            return self.format_error(self.create_url(type, indicator), message=str(e))
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return self.format_error(self.create_url(indicator), message=str(e))
        return self.parse_intel(response)
        
    async def fetch_domain_intel(self, indicator: str):
        return None
    async def fetch_url_intel(self, indicator: str):
        return None
    async def fetch_hash_intel(self, indicator: str):
        return None
    
    def create_url(self, indicator: str) -> str:
        return f"https://viz.greynoise.io/ip/{indicator}"
    
    def parse_intel(self, intel) -> dict:
        verdict = 0

        if intel.get("noise"):
            verdict = 1
        if intel.get("classification") == "malicious":
            verdict = 2
        
        summary_string = f"Classification: {intel.get("classification")}, last seen {intel.get("last_seen")}"
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=intel.get("link"), data=intel)
        
        return formatted_intel
