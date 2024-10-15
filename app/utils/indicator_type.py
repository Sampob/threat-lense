import re
import ipaddress

from app.utils.enums import IndicatorType

def validate_ip(ip_string: str) -> IndicatorType:
    """
    Validates if the string is a valid IPv4/IPv6 address.
    
    :param ip_string: String to be validated
    
    :return: IndicatorType enum with either IPv4 or IPv6, UNKNOWN if not valid
    """
    try:
        ip = ipaddress.ip_address(ip_string)
        if isinstance(ip, ipaddress.IPv4Address):
            return IndicatorType.IPv4
        elif isinstance(ip, ipaddress.IPv6Address):
            return IndicatorType.IPv6
    except ValueError:
        return IndicatorType.UNKNOWN

def validate_domain(domain: str) -> IndicatorType:
    """
    Uses regex to validate the string as a domain. 
    
    :param domain: String to be validated
    
    :return: Boolean if the string is a valid domain
    """
    # Regular expression for validating a domain
    domain_pattern = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if domain_pattern.match(domain):
        return True
    else:
        return False

def validate_url(url: str) -> IndicatorType:
    """
    Uses regex to validate the string as an url. 
    
    :param domain: String to be validated
    
    :return: Boolean if the string is a valid url
    """
    url_pattern = re.compile(r"^https?://")
    if url_pattern.match(url):
        return True
    else:
        return False

def validate_hash(hash: str) -> IndicatorType:
    """
    Uses regex to validate the string as a hash. 
    
    :param domain: String to be validated
    
    :return: Boolean if the string is a valid hash
    """
    if len(hash) in {32, 40, 64} and all(c in '0123456789abcdefABCDEF' for c in hash):
        return True
    else:
        return False
    
def get_indicator_type(ioc: str) -> IndicatorType:
    """
    Validates and categorizes the string as an IndicatorType. 
    
    :param ioc: String to be categorized
    
    :return: IndicatorType with categorized type, UNKNOWN if not valid
    """
    indicator_type = validate_ip(ioc)
    if indicator_type == IndicatorType.UNKNOWN:
        if validate_domain(ioc):
            return IndicatorType.DOMAIN
        elif validate_url(ioc):
            return IndicatorType.URL
        elif validate_hash(ioc):
            return IndicatorType.HASH
    return indicator_type

def is_valid_indicator(ioc: str) -> bool:
    """
    Validates the string as a supported IOC. 
    
    :param ioc: String to be validated
    
    :return: Boolean if the string is a valid IOC
    """
    if get_indicator_type(ioc) == IndicatorType.UNKNOWN:
        return False
    return True