from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from dcim.models import Site, Device
from ..models.monitoring import MonitoredHost
from ..models.groups import MonitoringGroup
from ..services import StatusService, get_diagnostic_hint
from .common import get_default_backend


class MonitoringDashboardView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/dashboard.html"

    def get(self, request):
        backend = get_default_backend()
        svc = StatusService(backend)

        # ===== Sites =====
        sites = Site.objects.filter(
            devices__primary_ip4__isnull=False
        ).distinct().order_by("name")

        site_cards = []
        totals = {
            "host_ok": 0, "host_down": 0, "host_total": 0,
            "modem_ok": 0, "modem_wl": 0, "modem_off": 0,
            "modem_total": 0,
        }
        for site in sites:
            mhs = MonitoredHost.objects.filter(
                device__site=site, enabled=True
            ).select_related("device__primary_ip4").prefetch_related("modems__interface")

            available_count = Device.objects.filter(
                site=site, primary_ip4__isnull=False
            ).count()

            if not mhs.exists():
                site_cards.append({
                    "site": site, "not_configured": True,
                    "available_count": available_count,
                })
                continue

            summary = svc.collect(mhs)
            hint = get_diagnostic_hint(summary)
            site_cards.append({
                "site": site, "not_configured": False,
                "summary": summary, "hint": hint,
            })
            totals["host_ok"] += summary.host_counters.get("reachable", 0)
            totals["host_down"] += summary.host_counters.get("unreachable", 0)
            totals["host_total"] += summary.host_total
            totals["modem_ok"] += summary.modem_counters.get("ok", 0)
            totals["modem_wl"] += summary.modem_counters.get("whitelist", 0)
            totals["modem_off"] += summary.modem_counters.get("no_internet", 0)
            totals["modem_total"] += summary.modem_total

        # ===== Groups =====
        group_cards = []
        for grp in MonitoringGroup.objects.prefetch_related("devices"):
            mhs = MonitoredHost.objects.filter(
                device__in=grp.devices.all(), enabled=True
            ).select_related("device__primary_ip4").prefetch_related("modems")
            summary = svc.collect(mhs)
            hint = get_diagnostic_hint(summary)
            group_cards.append({"group": grp, "summary": summary, "hint": hint})

        return render(request, self.template_name, {
            "site_cards": site_cards,
            "group_cards": group_cards,
            "totals": totals,
            "has_backend": backend is not None,
        })
