from enum import Enum

class IndicatorType(Enum):
    IPv4 = "IPV4"
    IPv6 = "IPV6"
    DOMAIN = "DOMAIN"
    URL = "URL"
    HASH = "HASH"
    UNKNOWN = "Unknown"
    
class Verdict(Enum):
    NONE = -1
    GOOD = 0
    SUSPICIOUS = 1
    MALICIOUS = 2

class VerdictColors(Enum):
    NONE = (190, 190, 190)      # Grey
    GOOD = (0, 128, 0)          # Green
    SUSPICIOUS = (255, 175, 0)  # Yellow
    MALICIOUS = (255, 0, 0)     # Red