from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from dcim.models import Device, Site
from ..models.monitoring import MonitoredHost
from ..services import StatusService, get_diagnostic_hint
from .common import get_default_backend


class SiteMonitoringView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/site_detail.html"

    def get(self, request, site_slug):
        site = get_object_or_404(Site, slug=site_slug)
        backend = get_default_backend()
        svc = StatusService(backend)

        mhs = MonitoredHost.objects.filter(
            device__site=site, enabled=True
        ).select_related(
            "device__primary_ip4", "device__device_type__manufacturer"
        ).prefetch_related("modems__interface")
        summary = svc.collect(mhs)
        hint = get_diagnostic_hint(summary)

        host_ids = mhs.values_list("device_id", flat=True)
        available = Device.objects.filter(
            site=site, primary_ip4__isnull=False
        ).exclude(id__in=host_ids).order_by("name")

        return render(request, self.template_name, {
            "container": site,
            "container_type": "site",
            "summary": summary,
            "hint": hint,
            "available_devices": available,
            "has_backend": backend is not None,
        })


class SiteHostAddView(LoginRequiredMixin, View):
    def post(self, request, site_slug):
        site = get_object_or_404(Site, slug=site_slug)
        for device_id in request.POST.getlist("device_id"):
            dev = Device.objects.filter(pk=device_id, site=site).first()
            if dev:
                MonitoredHost.objects.update_or_create(
                    device=dev, defaults={"enabled": True}
                )
        messages.success(request, "Hosts added.")
        return redirect("plugins:netbox_monitoring:site_detail", site_slug=site_slug)


class SiteHostRemoveView(LoginRequiredMixin, View):
    def post(self, request, site_slug, mh_pk):
        mh = get_object_or_404(
            MonitoredHost, pk=mh_pk, device__site__slug=site_slug
        )
        name = mh.device.name
        mh.delete()
        messages.success(request, f"{name} removed.")
        return redirect("plugins:netbox_monitoring:site_detail", site_slug=site_slug)
