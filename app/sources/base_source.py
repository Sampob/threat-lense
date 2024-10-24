import abc
from datetime import datetime, timezone

from app.models import fetch_api_key
from app.utils.cache import fetch_from_cache, cache_results
from app.utils.enums import IndicatorType, Verdict
from app.utils.logger import setup_logger

import aiohttp
import xmltodict

logger = setup_logger(__name__)

class BaseSource(abc.ABC):
    """
    Base class for all API sources. Every source should implement this. Unified handling of sources with different features. 
    """
    
    def __init__(self, url: str="", name: str="", requires_api_key: bool=False):
        self.url = url
        self.name = name
        self.requires_api_key = requires_api_key
    
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
            elif value == 0:
                return Verdict(0)
            elif value == -100:
                return Verdict(-100)
            return Verdict(-1)
        else:
            return Verdict(-1)
    
    def fetch_api_key(self) -> str:
        """
        Fetch API key from Redis database if available. 
        If API key not in Redis, attempts to fetch it from the database and cache it on Redis for future use.
        
        :return: API key in string format
        """
        name = self.get_name()
        redis_key = f"api_key:{name}"
        logger.debug(f"Fetching API key with value {redis_key}")
        cached_api_key = fetch_from_cache(redis_key)
        if cached_api_key:
            logger.debug(f"API key found from redis, with key {redis_key}")
            api_key = cached_api_key
            return api_key
        else:
            api_key = fetch_api_key(name)
            if api_key:
                logger.debug(f"API key found from database, storing to redis")
                cache_results(redis_key, api_key)
                return api_key
            else:
                logger.error(f"Empty API key found in the database for {name}")
                raise ValueError(f"Empty API key found in the database for {name}")
    
    def format_response(self, summary: str="", verdict: int=-1, url: str="", data: dict={}) -> dict:
        """
        Formats response in unified way.
        {
            "summary": "summary",
            "verdict": "VERDICT NAME",
            "url": "url",
            "data": {}
        }
        
        :param summary: Most important results, glanced over
        :param verdict: Verdict of results, benign, suspicious or malicious
        :param url: URL to the service's result
        :param data: Raw data from the source
        
        :return: Dict of full formatted response
        """
        return_dict = {
            "summary": summary,
            "verdict": self.get_verdict(verdict).name,
            "url": url,
            "data": data
        }
        return return_dict
    
    def format_error(self, url: str="", message: str="", status_code: int=None, timestamp: datetime=datetime.now(timezone.utc)) -> dict:
        """
        Formats error messages in unified way. 
        {
            "summary": "error",
            "verdict": "ERROR",
            "url": "url",
            "data": {
                "message": "error message",
                "status_code": "http status code or -1",
                "timestamp": "current timestamp"
            }
        }
        
        :param url: URL to the service's result
        :param message: Error message explaining what happened to cause the error
        :param status_code: HTTP status code for the error, default None
        :param timestamp: When the error occurred, defaults to datetime.now(timezone.utc)
        
        :return: Dict of error summary
        """
        return_dict = {
            "summary": "error",
            "verdict": self.get_verdict(-100).name,
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
            logger.debug(f"Sending request to {url}, attempt {attempt}/{retries}")
            try:
                # Set timeout configuration
                timeout_config = aiohttp.ClientTimeout(total=timeout)

                # Make the request
                async with aiohttp.ClientSession(timeout=timeout_config) as session:
                    async with session.request(method, url, headers=headers, json=json, params=params) as response:
                        response.raise_for_status() # Raise an error for bad HTTP responses (4xx, 5xx)
                        
                        content_type = response.headers.get("Content-Type")
                        if "application/json" in content_type:
                            data = await response.json() # Parse JSON response
                            return data
                        elif "text/txt" in content_type or "text/plain" in content_type or "application/xml" in content_type:
                            text_data = await response.text() # Fetch as text
                            data = xmltodict.parse(text_data) # Convert XML to dict
                            return data
                        else:
                            logger.warning(f"Unsupported content type: {content_type}")
                            return None

            except aiohttp.ClientResponseError as e:
                logger.error(f"URL: {url}, HTTP Error: {e.status} - {e.message}")
                if e.status in {500, 502, 503, 504}: # Retry on server errors
                    attempt += 1
                    logger.error(f"Server error, retrying... ({attempt}/{retries})")
                else:
                    raise
            except aiohttp.ClientError as e:
                # Handle other connection-related errors (timeouts, network failures)
                logger.error(f"URL: {url}, Connection error: {str(e)}")
                raise
            except TimeoutError as e:
                logger.error(f"Request to {url} timed out after {timeout} seconds")
                raise
        
        raise RuntimeError(f"Failed after {retries} attempts")
    
    async def fetch_intel(self, indicator: str, indicator_type: IndicatorType=IndicatorType.UNKNOWN) -> dict | None:
        """
        Categorizes the indicator and calls the correct method to fetch IOC intel. 
        
        :param indicator: IOC that will be enriched
        
        :return: Enriched IOC data from the source
        """
        if self.requires_api_key:
            try:
                self.api_key = self.fetch_api_key()
            except ValueError as e:
                logger.info(e)
                return None
        
        data = None
        try:
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
                logger.warning(f"Invalid indicator type for indicator {indicator}")
        except Exception as e:
            logger.error(f"Error occurred during fetching intel: {str(e)}")
        return data
    
    @abc.abstractmethod
    def create_url(self, indicator: str) -> str:
        raise NotImplementedError("Subclasses should implement this method")

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