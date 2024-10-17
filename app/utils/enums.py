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

class VerdictColors(Enum):
    ERROR = (255, 0, 255)       # Pink
    NONE = (190, 190, 190)      # Grey
    BENIGN = (0, 128, 0)          # Green
    SUSPICIOUS = (255, 175, 0)  # Yellow
    MALICIOUS = (255, 0, 0)     # Red