import aiohttp
from app.sources.base_source import BaseSource
from app.utils.logger import source_logger

class AbuseIpDbSource(BaseSource):
    def __init__(self):
        super().__init__("https://api.abuseipdb.com/api/v2/check", "AbuseIPDB")
        self.headers = {
            "Accept": "application/json",
            "Key": "" #self.api_key
        }
    
    async def fetch_ipv4_intel(self, indicator: str) -> dict:
        return await self.fetch_ip_intel(indicator)
    
    async def fetch_ipv6_intel(self, indicator: str) -> dict:
        return await self.fetch_ip_intel(indicator)
    
    async def fetch_ip_intel(self, indicator: str) -> dict:
        source_logger.debug(f"{self.name} | Searching for indicator '{indicator}'")
        querystring = {
            "ipAddress": indicator,
            "maxAgeInDays": "90"
        }
        
        try:
            response = await self.http_request(self.url, headers=self.headers, params=querystring)
        except aiohttp.ClientResponseError as e:
            return self.format_error(self.create_url(indicator), message=e.message, status_code=e.status)
        except aiohttp.ClientError as e:
            return self.format_error(self.create_url(indicator), message=str(e), status_code=-1)
        except RuntimeError as e:
            return self.format_error(self.create_url(indicator), message=str(e), status_code=-1)
        except Exception as e:
            return self.format_error(self.create_url(indicator), message=str(e))
            
        return self.parse_intel(response)
    
    async def fetch_domain_intel(self, indicator):
        return None
    async def fetch_url_intel(self, indicator: str):
        return None
    async def fetch_hash_intel(self, indicator: str):
        return None
    
    def create_url(self, indicator: str) -> str:
        return f"https://www.abuseipdb.com/check/{indicator}"
    
    def parse_intel(self, intel) -> dict:
        verdict = 0
        
        # Simple analysis to determine possible suspicious activity
        if intel["data"]["abuseConfidenceScore"] > 49:
            verdict = 2
        elif intel["data"]["abuseConfidenceScore"] > 0:
            verdict = 1
        
        if verdict == 0 and intel["data"]["totalReports"] > 0:
            verdict = 1
        
        summary_string = f'Confidence: {intel["data"]["abuseConfidenceScore"]}'
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(intel["data"]["ipAddress"]), data=intel["data"])
        
        return formatted_intel