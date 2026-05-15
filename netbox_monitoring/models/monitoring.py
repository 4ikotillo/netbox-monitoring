from django.db import models
from netbox.models import NetBoxModel
from dcim.models import Device, Interface


class MonitoredHost(NetBoxModel):
    """Router/switch/server. Checked via ICMP in Zabbix."""
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="monitoring_host")
    enabled = models.BooleanField(default=True)
    icmp_check_enabled = models.BooleanField(default=True, help_text="Check reachability via ICMP in Zabbix")
    zabbix_host_id = models.CharField(max_length=64, blank=True, help_text="Cached Zabbix hostid")

    class Meta:
        ordering = ["device"]
        verbose_name = "Monitored Host"
        verbose_name_plural = "Monitored Hosts"

    def __str__(self):
        return self.device.name or f"Host #{self.pk}"


class ModemLookupStrategy(models.TextChoices):
    PUBLIC_IP = "public_ip", "Public IP in Zabbix host"
    HOST_NAME = "host_name", "Hostname in Zabbix"
    ITEM_KEY = "item_key", "Item on router host"


class MonitoredModem(NetBoxModel):
    """Modem (SIM card). Checked via Internet Checker."""
    host = models.ForeignKey(MonitoredHost, on_delete=models.CASCADE, related_name="modems")
    interface = models.ForeignKey(Interface, on_delete=models.SET_NULL, null=True, blank=True, related_name="monitoring_modems")
    name = models.CharField(max_length=100, help_text="E.g. 'MTS slot 1', 'USB Huawei E3372'")
    enabled = models.BooleanField(default=True)
    lookup_strategy = models.CharField(max_length=20, choices=ModemLookupStrategy.choices, default=ModemLookupStrategy.PUBLIC_IP)
    lookup_value = models.CharField(max_length=255, blank=True, help_text="IP / hostname / item key")

    class Meta:
        ordering = ["host", "name"]
        verbose_name = "Monitored Modem"
        verbose_name_plural = "Monitored Modems"

    def __str__(self):
        return f"{self.name} ({self.host})"
