from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

logger = setup_logger(__name__, log_file="sources.log")

class ThreatMinerSource(BaseSource):
    def __init__(self):
        super().__init__(url="https://api.threatminer.org/v2/", name="ThreatMiner", requires_api_key=False)
    
    async def fetch_ipv4_intel(self, ip: str) -> dict:
        search_url = self.url + f"host.php?q={ip}&rt=6"
        return await self.fetch_intel_by_url(search_url)
    
    async def fetch_ipv6_intel(self, ip: str) -> dict:
        search_url = self.url + f"host.php?q={ip}&rt=6"
        return await self.fetch_intel_by_url(search_url)
    
    async def fetch_domain_intel(self, domain: str) -> dict:
        search_url = self.url + f"domain.php?q={domain}&rt=6"
        return await self.fetch_intel_by_url(search_url)
    
    async def fetch_hash_intel(self, hash: str) -> dict:
        search_url = self.url + f"sample.php?q={hash}&rt=7"
        return await self.fetch_intel_by_url(search_url)
    
    async def fetch_intel_by_url(self, url: str) -> dict:
        response = await self.http_request(url)

        # Bad API design
        # HTTP Status code 200 --> Response "status_code" contains the actual status, in str format
        if response.get("status_code", 0) != "200":
            if response.get("status_code") == "404":
                return self.parse_intel(response)
            else:
                return self.format_error(url, message=response.get("status_message", "Error"), status_code=response.get("status_code"))
            
        return self.parse_intel(response)
    
    async def fetch_url_intel(self, indicator: str):
        return None
    
    def create_url(self, indicator) -> str:
        return "https://www.threatminer.org/index.php"
    
    def parse_intel(self, intel: dict) -> dict:
        verdict = 0
        summary_string = "No results"
        
        if intel.get("results"):
            results_size = len(intel.get("results", []))
            summary_string = f"Appears in {results_size} reports"
            verdict = 1
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(""), data=intel.get("results"))
        
        return formatted_intel