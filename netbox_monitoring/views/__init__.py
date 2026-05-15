from .dashboard import MonitoringDashboardView
from .site import SiteMonitoringView, SiteHostAddView, SiteHostRemoveView
from .group import (
    GroupMonitoringView, GroupCreateView, GroupEditView, GroupDeleteView,
    GroupHostAddView, GroupHostRemoveView,
)
from .host import HostDetailView, HostAutodetectView, HostToggleView
from .modem import ModemCreateView, ModemEditView, ModemDeleteView
from .zabbix import (
    ZabbixServerListView, ZabbixServerCreateView, ZabbixServerEditView,
    ZabbixServerDeleteView, ZabbixServerTestView,
)
from .common import get_default_backend, get_backend  # для совместимости

__all__ = [
    "MonitoringDashboardView",
    "SiteMonitoringView", "SiteHostAddView", "SiteHostRemoveView",
    "GroupMonitoringView", "GroupCreateView", "GroupEditView", "GroupDeleteView",
    "GroupHostAddView", "GroupHostRemoveView",
    "HostDetailView", "HostAutodetectView", "HostToggleView",
    "ModemCreateView", "ModemEditView", "ModemDeleteView",
    "ZabbixServerListView", "ZabbixServerCreateView", "ZabbixServerEditView",
    "ZabbixServerDeleteView", "ZabbixServerTestView",
]
