from .base_source import BaseSource
from app.utils.logger import setup_logger

import aiohttp

logger = setup_logger(__name__, log_file="sources.log")

class AlienVaultSource(BaseSource):
    def __init__(self):
        super().__init__(url="https://otx.alienvault.com/api/v1/indicators/{}/{}/general/", name="Open Threat Exchange", requires_api_key=True)
    
    async def fetch_ipv4_intel(self, ip: str):
        return await self.make_request("IPv4", ip)
    
    async def fetch_ipv6_intel(self, ip: str):
        return await self.make_request("IPv6", ip)
    
    async def fetch_domain_intel(self, domain: str):
        return await self.make_request("domain", domain)
    
    async def fetch_url_intel(self, url: str):
        return await self.make_request("url", url)
    
    async def fetch_hash_intel(self, hash: str):
        return await self.make_request("file", hash)
    
    async def make_request(self, type: str, indicator: str):
        logger.debug(f"Searching for indicator {indicator}")
        headers = {
            "X-OTX-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.http_request(self.url.format(type, indicator), headers=headers)
        except aiohttp.ClientResponseError as e:
            logger.error(f"ClientResponseError: {str(e)}")
            return self.format_error(self.create_url(type, indicator), message=e.message, status_code=e.status)
        except aiohttp.ClientError as e:
            logger.error(f"ClientError: {str(e)}")
            return self.format_error(self.create_url(type, indicator), message=str(e))
        except RuntimeError as e:
            logger.error(f"RuntimeError: {str(e)}")
            return self.format_error(self.create_url(type, indicator), message=str(e))
        except TimeoutError as e:
            logger.error(f"TimeoutError: {str(e)}")
            return self.format_error(self.create_url(type, indicator), message=str(e))
        except Exception as e:
            error_message = str(e)
            if hasattr(e, "message"):
                error_message = str(e.message)
            logger.error(f"Exception: {error_message}")
            return self.format_error(self.create_url(type, indicator), message=error_message)
        return self.parse_intel(response)
    
    def create_url(self, type: str, indicator: str) -> str:
        base_url = "https://otx.alienvault.com/indicator/{}/{}"
        return base_url.format(type, indicator)
    
    def parse_intel(self, intel):
        verdict = 0
        
        # Simple analysis to determine possible suspicious activity
        pulse_count = intel.get("pulse_info", {}).get("count", 0)
        summary_string = f"No. of pulses: {pulse_count}"
        if pulse_count:
            if pulse_count > 10:
                verdict = 2
            elif pulse_count > 0:
                verdict = 1
        if len(intel.get("validation", [])) > 0:
            if verdict > 0:
                verdict = 1
            summary_string = f"Accepted whitelist on indicator. No. of pulses: {pulse_count}"
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(intel.get("type"), intel.get("indicator")), data=intel)
        
        return formatted_intel