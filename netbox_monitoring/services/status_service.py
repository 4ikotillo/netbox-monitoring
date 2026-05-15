"""
StatusService — единая точка получения агрегированного статуса.
Views дёргают только это, не лезут напрямую в Zabbix.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..backends.base import HostStatus, ModemStatus
from ..models.monitoring import MonitoredHost, MonitoredModem


@dataclass
class HostRow:
    monitored_host: MonitoredHost
    status: str = "unknown"
    rtt_ms: Optional[float] = None
    last_check: Optional[str] = None
    modems: List[dict] = field(default_factory=list)


@dataclass
class ContainerSummary:
    """Итоговая сводка по сайту/группе для дашборда."""
    host_total: int = 0
    host_counters: Dict[str, int] = field(default_factory=dict)
    modem_total: int = 0
    modem_counters: Dict[str, int] = field(default_factory=dict)
    rows: List[HostRow] = field(default_factory=list)


class StatusService:
    """
    Принимает Zabbix-backend (или None) и набор хостов,
    возвращает строки и сводку.
    """

    def __init__(self, backend):
        self.backend = backend

    def empty_host_counters(self):
        return {s.value: 0 for s in HostStatus}

    def empty_modem_counters(self):
        return {s.value: 0 for s in ModemStatus}

    def collect(self, monitored_hosts) -> ContainerSummary:
        summary = ContainerSummary(
            host_counters=self.empty_host_counters(),
            modem_counters=self.empty_modem_counters(),
        )
        for mh in monitored_hosts:
            row = self._build_host_row(mh)
            summary.rows.append(row)
            summary.host_counters[row.status] += 1
            summary.host_total += 1
            for m in row.modems:
                summary.modem_counters[m["status"]] += 1
                summary.modem_total += 1
        return summary

    def _build_host_row(self, mh: MonitoredHost) -> HostRow:
        row = HostRow(monitored_host=mh)
        device = mh.device

        # Host status
        if self.backend and mh.icmp_check_enabled and device.primary_ip4:
            ip = str(device.primary_ip4.address.ip)
            hr = self.backend.get_host_status(ip)
            row.status = hr.status.value
            row.rtt_ms = hr.rtt_ms
            row.last_check = hr.last_check
        else:
            row.status = HostStatus.UNKNOWN.value

        # Modems
        host_unreachable = row.status == HostStatus.UNREACHABLE.value
        for modem in mh.modems.filter(enabled=True).select_related("interface"):
            if host_unreachable:
                # Хост мёртв → модем неизвестен (не offline!)
                m_status = ModemStatus.UNKNOWN.value
                m_latency = None
                m_code = None
                m_last = None
            elif self.backend:
                ms = self.backend.get_modem_status(modem)
                m_status = ms.status.value
                m_latency = ms.latency_ms
                m_code = ms.http_code
                m_last = ms.last_check
            else:
                m_status = ModemStatus.UNKNOWN.value
                m_latency = m_code = m_last = None

            row.modems.append({
                "modem": modem,
                "status": m_status,
                "latency_ms": m_latency,
                "http_code": m_code,
                "last_check": m_last,
            })
        return row
