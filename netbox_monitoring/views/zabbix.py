from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..forms import ZabbixServerForm
from ..models.zabbix import ZabbixServer
from .common import get_backend


class ZabbixServerListView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/zabbix_servers.html"

    def get(self, request):
        return render(request, self.template_name, {
            "servers": ZabbixServer.objects.all(),
        })


class ZabbixServerCreateView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/zabbix_server_form.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": ZabbixServerForm(), "title": "Add Zabbix Server",
        })

    def post(self, request):
        form = ZabbixServerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Zabbix server added.")
            return redirect("plugins:netbox_monitoring:zabbix_servers")
        return render(request, self.template_name, {
            "form": form, "title": "Add Zabbix Server",
        })


class ZabbixServerEditView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/zabbix_server_form.html"

    def get(self, request, pk):
        s = get_object_or_404(ZabbixServer, pk=pk)
        return render(request, self.template_name, {
            "form": ZabbixServerForm(instance=s), "title": f"Edit {s.name}",
        })

    def post(self, request, pk):
        s = get_object_or_404(ZabbixServer, pk=pk)
        form = ZabbixServerForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, "Zabbix server updated.")
            return redirect("plugins:netbox_monitoring:zabbix_servers")
        return render(request, self.template_name, {
            "form": form, "title": f"Edit {s.name}",
        })


class ZabbixServerDeleteView(LoginRequiredMixin, View):
    template_name = "netbox_monitoring/zabbix_server_confirm_delete.html"

    def get(self, request, pk):
        return render(request, self.template_name, {
            "server": get_object_or_404(ZabbixServer, pk=pk),
        })

    def post(self, request, pk):
        s = get_object_or_404(ZabbixServer, pk=pk)
        s.delete()
        messages.success(request, "Server deleted.")
        return redirect("plugins:netbox_monitoring:zabbix_servers")


class ZabbixServerTestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        s = get_object_or_404(ZabbixServer, pk=pk)
        ok, msg = get_backend(s).test_connection()
        return JsonResponse({"ok": ok, "message": msg})
