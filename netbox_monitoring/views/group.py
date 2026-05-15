from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from dcim.models import Device
from ..forms import MonitoringGroupForm
from ..models.groups import MonitoringGroup
from ..models.monitoring import MonitoredHost
from ..services import StatusService, get_diagnostic_hint
from .common import get_default_backend


class GroupMonitoringView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/site_detail.html"  # переиспользуем

    def get(self, request, pk):
        group = get_object_or_404(MonitoringGroup, pk=pk)
        backend = get_default_backend()
        svc = StatusService(backend)

        mhs = MonitoredHost.objects.filter(
            device__in=group.devices.all(), enabled=True
        ).select_related(
            "device__primary_ip4", "device__site"
        ).prefetch_related("modems__interface")
        summary = svc.collect(mhs)
        hint = get_diagnostic_hint(summary)

        in_ids = mhs.values_list("device_id", flat=True)
        available = Device.objects.filter(
            primary_ip4__isnull=False, id__in=group.devices.values_list("id", flat=True)
        ).exclude(id__in=in_ids).select_related("site").order_by("site__name", "name")

        return render(request, self.template_name, {
            "container": group,
            "container_type": "group",
            "summary": summary,
            "hint": hint,
            "available_devices": available,
            "has_backend": backend is not None,
        })


class GroupHostAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(MonitoringGroup, pk=pk)
        for device_id in request.POST.getlist("device_id"):
            dev = Device.objects.filter(pk=device_id).first()
            if dev:
                MonitoredHost.objects.update_or_create(device=dev, defaults={"enabled": True})
                # Также гарантируем что устройство в группе
                group.devices.add(dev)
        messages.success(request, "Hosts added.")
        return redirect("plugins:netbox_monitoring:group_detail", pk=pk)


class GroupHostRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk, mh_pk):
        group = get_object_or_404(MonitoringGroup, pk=pk)
        mh = get_object_or_404(MonitoredHost, pk=mh_pk)
        # Из группы удаляем девайс, но MonitoredHost не трогаем (он может быть и в site)
        group.devices.remove(mh.device)
        messages.success(request, f"{mh.device.name} removed from group.")
        return redirect("plugins:netbox_monitoring:group_detail", pk=pk)


class GroupCreateView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/group_form.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": MonitoringGroupForm(), "title": "New Group",
        })

    def post(self, request):
        form = MonitoringGroupForm(request.POST)
        if form.is_valid():
            grp = form.save()
            # Для каждого устройства в группе — создаём MonitoredHost если нет
            for dev in grp.devices.all():
                MonitoredHost.objects.get_or_create(device=dev, defaults={"enabled": True})
            messages.success(request, f"Group {grp.name} created.")
            return redirect("plugins:netbox_monitoring:group_detail", pk=grp.pk)
        return render(request, self.template_name, {"form": form, "title": "New Group"})


class GroupEditView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/group_form.html"

    def get(self, request, pk):
        grp = get_object_or_404(MonitoringGroup, pk=pk)
        return render(request, self.template_name, {
            "form": MonitoringGroupForm(instance=grp), "title": f"Edit {grp.name}",
        })

    def post(self, request, pk):
        grp = get_object_or_404(MonitoringGroup, pk=pk)
        form = MonitoringGroupForm(request.POST, instance=grp)
        if form.is_valid():
            form.save()
            for dev in grp.devices.all():
                MonitoredHost.objects.get_or_create(device=dev, defaults={"enabled": True})
            messages.success(request, "Group updated.")
            return redirect("plugins:netbox_monitoring:group_detail", pk=pk)
        return render(request, self.template_name, {"form": form, "title": f"Edit {grp.name}"})


class GroupDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        grp = get_object_or_404(MonitoringGroup, pk=pk)
        name = grp.name
        grp.delete()
        messages.success(request, f"Group {name} deleted.")
        return redirect("plugins:netbox_monitoring:dashboard")
