from django.db import models
from netbox.models import NetBoxModel


class ZabbixServer(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(help_text="http://zabbix.example.com")
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=255, blank=True)
    token = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Zabbix Server"
        verbose_name_plural = "Zabbix Servers"

    def __str__(self):
        return self.name
