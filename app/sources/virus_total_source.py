from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

import aiohttp

logger = setup_logger(__name__, log_file="sources.log")

class VirusTotalSource(BaseSource):
    def __init__(self):
        super().__init__("https://www.virustotal.com/api/v3/", "VirusTotal", requires_api_key=True)
    
    async def fetch_ipv4_intel(self, ip: str) -> dict:
        url = self.url + "ip_addresses/" + ip
        return await self.fetch_intel_by_url(url, ip)
    
    async def fetch_ipv6_intel(self, ip: str) -> dict:
        url = self.url + "ip_addresses/" + ip
        return await self.fetch_intel_by_url(url, ip)
    
    async def fetch_domain_intel(self, domain: str) -> dict:
        url = self.url + "domains/" + domain
        return await self.fetch_intel_by_url(url, domain)
    
    async def fetch_url_intel(self, url_ioc: str) -> dict:
        url = f"{self.url}urls/{url_ioc}"
        return await self.fetch_intel_by_url(url, url_ioc)
    
    async def fetch_hash_intel(self, hash: str) -> dict:
        url = f"{self.url}files/{hash}"
        return await self.fetch_intel_by_url(url, hash)
    
    async def fetch_intel_by_url(self, url, indicator="") -> dict:
        headers = {
            "accept": "application/json",
            "x-apikey": self.api_key
        }
        
        try:
            response = await self.http_request(url, headers=headers)
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
    
    def create_url(self, indicator: str):
        return f"https://www.virustotal.com/gui/search/{indicator}"
    
    def parse_intel(self, intel: dict) -> dict:
        verdict = 0
        
        data = intel.get("data", {})
        attributes = data.get("attributes")

        count_analysis = 0
        last_analysis = {}
        if attributes.get("last_analysis_stats"):
            last_analysis = attributes.get("last_analysis_stats")
            for value in last_analysis.values():
                count_analysis += value
        
        total_suspicious = 0
        total_suspicious += last_analysis.get("malicious")
        total_suspicious += last_analysis.get("suspicious")
        
        community_rep = data.get("reputation", 0)
        
        # Community votes are in the negatives
        if community_rep < 0:
            verdict += 1
        # Vendor has marked indicator as "malicious"
        if last_analysis.get("malicious") > 2:
            verdict += 2
        # Vendor has marked indicator as "suspicious"
        if last_analysis.get("suspicious") > 0 or last_analysis.get("malicious") > 0:
            verdict += 1
        
        summary_string = f"{total_suspicious}/{count_analysis}, community: {community_rep}"
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(data.get("id", "")), data=data)
        
        return formatted_intel