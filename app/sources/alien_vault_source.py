from .base_source import BaseSource
from app.utils.logger import source_logger

import aiohttp

class AlienVaultSource(BaseSource):
    def __init__(self):
        super().__init__(url="https://otx.alienvault.com/api/v1/indicators/{}/{}/general/", name="Open Threat Exchange")
        self.headers = {
            "X-OTX-API-KEY": self.key,
            "Content-Type": "application/json"
        }
    
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
        source_logger.debug(f"{self.name} | Searching for indicator {indicator}")
        try:
            response = await self.http_request(self.url.format(type, indicator), headers=self.headers)
        except aiohttp.ClientResponseError as e:
            return self.format_error(self.create_url(type, indicator), message=e.message, status_code=e.status)
        except aiohttp.ClientError as e:
            return self.format_error(self.create_url(type, indicator), message=str(e), status_code=-1)
        except RuntimeError as e:
            return self.format_error(self.create_url(type, indicator), message=str(e), status_code=-1)
        except Exception as e:
            return self.format_error(self.create_url(type, indicator), message=str(e))
        
        return self.parse_intel(response)
    
    def create_url(self, type: str, indicator: str) -> str:
        base_url = "https://otx.alienvault.com/indicator/{}/{}"
        return base_url.format(type, indicator)
    
    def parse_intel(self, intel):
        verdict = 0
        
        # Simple analysis to determine possible suspicious activity
        
        pulse_count = intel["pulse_info"]["count"]
        
        if intel["malware"]["size"] > 0:
            verdict += 2
        if pulse_count > 10:
            verdict += 2
        elif pulse_count > 0:
            verdict += 1
        if len(intel["validation"]) > 0:
            verdict = 0

        if len(intel["validation"]) > 0:
            summary_string = f"Accepted whitelist. No. of pulses: {pulse_count}"
        else:
            summary_string = f"No. of pulses: {pulse_count}"
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(intel["type"], intel["indicator"]), data=intel)
        
        return formatted_intel