import abc
from datetime import datetime, timezone

from app.utils.enums import IndicatorType, Verdict
from app.utils.indicator_type import get_indicator_type
from app.utils.logger import source_logger

import aiohttp

class BaseSource(abc.ABC):
    """
    Base class for all API sources. Every source should implement this. Unified handling of sources with different features. 
    """
    
    def __init__(self, url: str="", name: str=""):
        self.url = url
        self.name = name
    
    def get_name(self) -> str:
        """
        Function to get source's name. 
        
        :return: Source's name
        """
        if self.name:
            return self.name
        else:
            return self.__class__.__name__
    
    def get_verdict(self, value: int) -> Verdict:
        """
        Transforms integer value to a Verdict enum. 
        
        :param value: Integer that represents an IOC's verdict
        
        :return: Transformed, unified Verdict enum
        """
        if isinstance(value, int):
            if value >= 2:
                return Verdict(2)
            elif value == 1:
                return Verdict(1)
            return Verdict(0)
        else:
            return Verdict(-1)
        
    
    def format_response(self, summary: str="", verdict: Verdict=Verdict.NONE, url: str="", data: dict={}) -> dict:
        return_dict = {
            "summary": summary,
            "verdict": self.get_verdict(verdict).name,
            "url": url,
            "data": data
        }
        return return_dict
    
    def format_error(self, url: str="", message: str="", status_code: int=-1, timestamp: datetime=datetime.now(timezone.utc)) -> dict:
        return_dict = {
            "summary": "error",
            "verdict": self.get_verdict(-1).name,
            "url": url,
            "data": {
                "message": message,
                "status_code": status_code,
                "timestamp": str(timestamp)
            }
        }
        return return_dict
    
    async def http_request(self, url: str, method="GET", headers=None, json=None, params=None, timeout=10, retries=3) -> dict:
        """
        A helper method to handle HTTP requests uniformly and handle errors.
        
        :param url: The URL to send the request to
        :param method: The HTTP method to use ('GET', 'POST', etc.)
        :param headers: Dictionary of HTTP headers to send with the request
        :param json: Dictionary of JSON data to send in the request body (for POST/PUT requests)
        :param params: Dictionary of query parameters to append to the URL
        :param timeout: Timeout for the request in seconds
        :param retries: Number of times to retry the request in case of transient errors
        
        :return: Dict of HTTP response
        """
        attempt = 0
        while attempt < retries:
            try:
                # Set timeout configuration
                timeout_config = aiohttp.ClientTimeout(total=timeout)

                # Make the request
                async with aiohttp.ClientSession(timeout=timeout_config) as session:
                    async with session.request(method, url, headers=headers, json=json, params=params) as response:
                        response.raise_for_status()  # Raise an error for bad HTTP responses (4xx, 5xx)
                        return await response.json()  # Assuming the response is JSON

            except aiohttp.ClientResponseError as e:
                source_logger.error(f"URL: {url}, HTTP Error: {e.status} - {e.message}")
                if e.status in {500, 502, 503, 504}:  # Retry on server errors
                    attempt += 1
                    source_logger.error(f"Retrying... ({attempt}/{retries})")
                else:
                    raise
            except aiohttp.ClientError as e:
                # Handle other connection-related errors (timeouts, network failures)
                source_logger.error(f"URL: {url}, Connection error: {str(e)}")
                raise
        
        raise RuntimeError(f"Failed after {retries} attempts")
    
    async def fetch_intel(self, indicator: str) -> dict:
        """
        Categorizes the indicator and calls the correct method to fetch IOC intel. 
        
        :param indicator: IOC that will be enriched
        
        :return: Enriched IOC data from the source
        """
        indicator_type = get_indicator_type(indicator)
        
        data = None
        if indicator_type == IndicatorType.IPv4:
            data = await self.fetch_ipv4_intel(indicator)
        elif indicator_type == IndicatorType.IPv6:
            data = await self.fetch_ipv6_intel(indicator)
        elif indicator_type == IndicatorType.DOMAIN:
            data = await self.fetch_domain_intel(indicator)
        elif indicator_type == IndicatorType.URL:
            data = await self.fetch_url_intel(indicator)
        elif indicator_type == IndicatorType.HASH:
            data = await self.fetch_hash_intel(indicator)
        else:
            source_logger.warning(f"Invalid indicator type for indicator {indicator}")
        return data

    @abc.abstractmethod
    async def fetch_ipv4_intel(self, indicator: str):
        raise NotImplementedError("Subclasses should implement this method")
    
    @abc.abstractmethod
    async def fetch_ipv6_intel(self, indicator: str):
        raise NotImplementedError("Subclasses should implement this method")
    
    @abc.abstractmethod
    async def fetch_domain_intel(self, indicator: str):
        raise NotImplementedError("Subclasses should implement this method")
    
    @abc.abstractmethod
    async def fetch_url_intel(self, indicator: str):
        raise NotImplementedError("Subclasses should implement this method")
    
    @abc.abstractmethod
    async def fetch_hash_intel(self, indicator: str):
        raise NotImplementedError("Subclasses should implement this method")
    
    @abc.abstractmethod
    async def parse_intel(self, intel: dict):
        raise NotImplementedError("Subclasses should implement this method")