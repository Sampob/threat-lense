from hashlib import sha256

from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

import aiohttp

logger = setup_logger(__name__, log_file="sources.log")

class MaltiverseSource(BaseSource):
    def __init__(self):
        super().__init__("https://api.maltiverse.com/", "Maltiverse", requires_api_key=True)
    
    async def fetch_ipv4_intel(self, ip: str) -> dict:
        return await self.make_request("ip", ip)
    
    async def fetch_domain_intel(self, domain: str):
        return await self.make_request("hostname", domain)
    
    async def fetch_url_intel(self, url: str):
        return await self.make_request("url", url)
    
    async def fetch_hash_intel(self, hash: str):
        # Supports SHA256 (64), SHA1 (40) and MD5 (32)
        if len(hash) == 64: # SHA256
            return await self.make_request("sample", hash)
        elif len(hash) == 40: # SHA1
            return await self.make_request("sha1", hash)
        elif len(hash) == 32: # MD5
            return await self.make_request("md5", hash)
        return None
    
    def fetch_ipv6_intel(self, indicator: str):
        return None
    
    async def make_request(self, type: str, indicator: str) -> dict:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Maltiverse requires URLs to be SHA256 hashed for searches
        if type == "url":
            hashed_url = sha256(indicator.encode("utf-8")).hexdigest()
            search_url = f"{self.url}{type}/{hashed_url}"
        else:
            search_url = f"{self.url}{type}/{indicator}"
        
        try:
            response = await self.http_request(search_url, headers=headers)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                logger.error(f"ClientResponseError GreyNoise rate-limit exceeded: {str(e)}")
                return self.format_response(summary=e.message, verdict=-100, url=self.create_url(indicator), data={})
            elif e.status == 404:
                logger.error(f"ClientResponseError indicator {indicator} not found from GreyNoise")
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
    
    def create_url(self, indicator: str) -> str:
        base_url = "https://maltiverse.com/intelligence/search;query={}"
        return base_url.format(indicator)
    
    def parse_intel(self, intel: dict):
        verdict = 0
        
        indicator_fields = ["ip_addr", "hostname", "url", "sha256"]
        indicator = ""
        
        blacklisted = intel.get("blacklist")
        classification = intel.get("classification")
                
        for key in intel.keys():
            if key in ["is_cnc", "is_distributing_malware", "is_iot_threat", "is_mining_pool", "is_phishing", "is_storing_phishing", "is_known_attacker", "is_known_scanner", "is_tor_node"]:
                verdict += 1
            if key in indicator_fields:
                indicator = intel.get(key, "")
        
        if blacklisted:
            verdict += 1
            if blacklisted > 2:
                verdict = 2
        
        if classification == "malicious":
            verdict = 2
        
        summary_string = f"Classification: {classification}"
        
        formatted_intel = self.format_response(summary=summary_string, verdict=verdict, url=self.create_url(indicator), data=intel)
        
        return formatted_intel