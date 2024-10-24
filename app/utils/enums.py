from enum import Enum

class IndicatorType(Enum):
    IPv4 = "IPV4"
    IPv6 = "IPV6"
    DOMAIN = "DOMAIN"
    URL = "URL"
    HASH = "HASH"
    UNKNOWN = "Unknown"
    
class Verdict(Enum):
    ERROR = -100
    NONE = -1
    BENIGN = 0
    SUSPICIOUS = 1
    MALICIOUS = 2