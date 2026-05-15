"""
Превращает сводку (ContainerSummary) в человекопонятную подсказку:
'Всё ок' / 'SIM-проблема на X' / 'Хост Y не отвечает'.
"""
from dataclasses import dataclass

from ..backends.base import HostStatus, ModemStatus
from .status_service import ContainerSummary


@dataclass
class DiagnosticHint:
    severity: str   # "ok" | "warn" | "danger" | "info"
    title: str
    detail: str = ""


def get_diagnostic_hint(summary: ContainerSummary) -> DiagnosticHint:
    hc = summary.host_counters
    mc = summary.modem_counters

    unreachable = hc.get(HostStatus.UNREACHABLE.value, 0)
    no_inet = mc.get(ModemStatus.NO_INTERNET.value, 0)
    whitelist = mc.get(ModemStatus.WHITELIST.value, 0)
    host_total = summary.host_total

    if host_total == 0:
        return DiagnosticHint("info", "No hosts monitored",
                              "Add devices to start monitoring.")

    # Всё совсем плохо
    if unreachable == host_total and host_total > 0:
        return DiagnosticHint(
            "danger", "Site outage",
            f"All {host_total} hosts are unreachable. "
            "Check power and network at the site."
        )

    # Несколько хостов лежат
    if unreachable > 1:
        return DiagnosticHint(
            "danger", f"{unreachable} hosts down",
            "Multiple hosts unreachable — check power/network."
        )

    # Один хост лежит
    if unreachable == 1:
        return DiagnosticHint(
            "danger", "Host unreachable",
            "One host is down. Check its power and network connection."
        )

    # Хосты живы, но проблемы с модемами
    if no_inet > 0 and whitelist > 0:
        return DiagnosticHint(
            "warn", f"{no_inet} offline, {whitelist} whitelisted modems",
            "Hosts are reachable. Check SIM cards / carriers."
        )
    if no_inet > 0:
        return DiagnosticHint(
            "warn", f"{no_inet} modem(s) without internet",
            "Hosts are up. Likely SIM/carrier issue."
        )
    if whitelist > 0:
        return DiagnosticHint(
            "warn", f"{whitelist} modem(s) on whitelist",
            "Captive portal detected. Pay/activate the SIM."
        )

    # Всё ок
    return DiagnosticHint(
        "ok", "All systems operational",
        f"{host_total} host(s) reachable, {summary.modem_total} modem(s) online."
    )
