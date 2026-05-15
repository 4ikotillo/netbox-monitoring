from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..detectors import detect_modems
from ..models.monitoring import MonitoredHost, MonitoredModem


class HostDetailView(LoginRequiredMixin, View):
    """Детальная страница хоста — список модемов + кнопка автодетекта."""
    template_name = "netbox_monitoring/host_detail.html"

    def get(self, request, pk):
        mh = get_object_or_404(
            MonitoredHost.objects.select_related("device__device_type__manufacturer"),
            pk=pk,
        )
        # Какие модемы детектор предложил бы — для подсказки
        suggested = detect_modems(mh.device)
        existing_iface_ids = set(
            mh.modems.exclude(interface__isnull=True).values_list("interface_id", flat=True)
        )
        new_suggestions = [s for s in suggested if s.interface_id not in existing_iface_ids]

        return render(request, self.template_name, {
            "host": mh,
            "modems": mh.modems.select_related("interface").all(),
            "suggestions": new_suggestions,
        })


class HostAutodetectView(LoginRequiredMixin, View):
    """Применить детектор и создать недостающие модемы."""
    def post(self, request, pk):
        mh = get_object_or_404(MonitoredHost, pk=pk)
        suggested = detect_modems(mh.device)
        existing_iface_ids = set(
            mh.modems.exclude(interface__isnull=True).values_list("interface_id", flat=True)
        )
        created = 0
        for spec in suggested:
            if spec.interface_id and spec.interface_id in existing_iface_ids:
                continue
            MonitoredModem.objects.create(
                host=mh,
                interface_id=spec.interface_id,
                name=spec.name,
                enabled=True,
            )
            created += 1
        if created:
            messages.success(request, f"Auto-detected {created} modem(s).")
        else:
            messages.info(request, "No new modems detected.")
        return redirect("plugins:netbox_monitoring:host_detail", pk=mh.pk)


class HostToggleView(LoginRequiredMixin, View):
    """Включить/выключить ICMP-проверку хоста."""
    def post(self, request, pk):
        mh = get_object_or_404(MonitoredHost, pk=pk)
        mh.icmp_check_enabled = not mh.icmp_check_enabled
        mh.save()
        return redirect("plugins:netbox_monitoring:host_detail", pk=mh.pk)
