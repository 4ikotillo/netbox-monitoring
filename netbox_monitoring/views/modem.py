from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..forms import ModemForm
from ..models.monitoring import MonitoredHost, MonitoredModem


class ModemCreateView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/modem_form.html"

    def get(self, request, host_pk):
        mh = get_object_or_404(MonitoredHost, pk=host_pk)
        return render(request, self.template_name, {
            "form": ModemForm(host=mh),
            "host": mh, "title": "Add modem",
        })

    def post(self, request, host_pk):
        mh = get_object_or_404(MonitoredHost, pk=host_pk)
        form = ModemForm(request.POST, host=mh)
        if form.is_valid():
            modem = form.save(commit=False)
            modem.host = mh
            modem.save()
            messages.success(request, f"Modem {modem.name} added.")
            return redirect("plugins:netbox_monitoring:host_detail", pk=mh.pk)
        return render(request, self.template_name, {
            "form": form, "host": mh, "title": "Add modem",
        })


class ModemEditView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/modem_form.html"

    def get(self, request, pk):
        modem = get_object_or_404(MonitoredModem, pk=pk)
        return render(request, self.template_name, {
            "form": ModemForm(instance=modem, host=modem.host),
            "host": modem.host, "title": f"Edit {modem.name}",
        })

    def post(self, request, pk):
        modem = get_object_or_404(MonitoredModem, pk=pk)
        form = ModemForm(request.POST, instance=modem, host=modem.host)
        if form.is_valid():
            form.save()
            messages.success(request, "Modem updated.")
            return redirect("plugins:netbox_monitoring:host_detail", pk=modem.host.pk)
        return render(request, self.template_name, {
            "form": form, "host": modem.host, "title": f"Edit {modem.name}",
        })


class ModemDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        modem = get_object_or_404(MonitoredModem, pk=pk)
        host_pk = modem.host.pk
        name = modem.name
        modem.delete()
        messages.success(request, f"Modem {name} deleted.")
        return redirect("plugins:netbox_monitoring:host_detail", pk=host_pk)
