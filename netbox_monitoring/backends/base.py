from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HostStatus(str, Enum):
    """Статус роутера/железа."""
    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


class ModemStatus(str, Enum):
    """Статус модема (SIM)."""
    OK = "ok"
    WHITELIST = "whitelist"
    NO_INTERNET = "no_internet"
    UNKNOWN = "unknown"


@dataclass
class HostStatusResult:
    status: HostStatus
    rtt_ms: Optional[float] = None
    last_check: Optional[str] = None
    zabbix_host_id: Optional[str] = None


@dataclass
class ModemStatusResult:
    status: ModemStatus
    latency_ms: Optional[int] = None
    http_code: Optional[int] = None
    last_check: Optional[str] = None
