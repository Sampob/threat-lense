import abc

from app.utils.enums import IndicatorType, Verdict
from app.utils.indicator_type import get_indicator_type
from app.utils.logger import app_logger

import aiohttp

class SourceMeta(abc.ABCMeta):
    _sources = {}
    
    def __new__(mcs, name, bases, class_dict):
        cls = super().__new__(mcs, name, bases, class_dict)
        if bases != (object,):
            app_logger.debug(f"Adding object '{cls.__name__}' to _sources")
            SourceMeta._sources[cls.__name__] = cls
        return cls

    @classmethod
    def get_sources(cls):
        return cls._sources.values()

class SourceFactory:
    @staticmethod
    def create_sources():
        sources = []
        for source_cls in SourceMeta.get_sources():
            sources.append(source_cls())
        return sources

class BaseSource(metaclass=SourceMeta):
    """ Base class for all API sources. """
    
    async def http_request(self, url: str, method="GET", headers=None, json=None, params=None, timeout=10, retries=3):
        """
        A helper method to handle HTTP requests uniformly and handle errors.
        
        :param url: The URL to send the request to
        :param method: The HTTP method to use ('GET', 'POST', etc.)
        :param headers: Dictionary of HTTP headers to send with the request
        :param json: Dictionary of JSON data to send in the request body (for POST/PUT requests)
        :param params: Dictionary of query parameters to append to the URL
        :param timeout: Timeout for the request in seconds
        :param retries: Number of times to retry the request in case of transient errors
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
                app_logger.error(f"URL: {url}, HTTP Error: {e.status} - {e.message} | Retrying... ({attempt}/{retries})")
                if e.status in {500, 502, 503, 504}:  # Retry on server errors
                    attempt += 1
                else:
                    raise
            except aiohttp.ClientError as e:
                # Handle other connection-related errors (timeouts, network failures)
                app_logger.error(f"URL: {url}, Connection error: {str(e)}")
                raise
        
        raise RuntimeError(f"Failed after {retries} attempts")
    
    async def fetch_intel(self, indicator: str) -> dict:
        """
        Categorizes the indicator and calls the correct method to fetch IOC intel. 
        
        :param indicator: IOC that will be enriched
        
        :return: Enriched IOC data from the source
        """
        if self.init:
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
                app_logger.warning(f"Invalid indicator type for indicator '{indicator}'")
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