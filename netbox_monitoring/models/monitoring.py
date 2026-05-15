from django.db import models
from netbox.models import NetBoxModel
from dcim.models import Device, Interface


class MonitoredHost(NetBoxModel):
    """
    Роутер/коммутатор/сервер. Проверяется через ICMP в Zabbix.
    Один Device = один MonitoredHost.
    """
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, related_name="monitoring_host"
    )
    enabled = models.BooleanField(default=True)
    icmp_check_enabled = models.BooleanField(
        default=True,
        help_text="Проверять доступность через ICMP в Zabbix",
    )
    zabbix_host_id = models.CharField(
        max_length=64, blank=True,
        help_text="Кеш hostid в Zabbix (заполняется автоматически)",
    )

    class Meta:
        ordering = ["device"]
        verbose_name = "Monitored Host"
        verbose_name_plural = "Monitored Hosts"

    def __str__(self):
        return self.device.name or f"Host #{self.pk}"


class ModemLookupStrategy(models.TextChoices):
    """
    Как искать модем в Zabbix Internet Checker'а.
    Разные у разных операторов/инсталляций — выбираем индивидуально.
    """
    PUBLIC_IP = "public_ip", "Публичный IP в Zabbix host"
    HOST_NAME = "host_name", "Hostname в Zabbix"
    ITEM_KEY = "item_key", "Item на хосте роутера"


class MonitoredModem(NetBoxModel):
    """
    Модем (SIM-карта). Проверяется через Internet Checker.
    Привязан к MonitoredHost (на каком роутере живёт)
    и опционально к Interface (какой именно интерфейс представляет).
    """
    host = models.ForeignKey(
        MonitoredHost, on_delete=models.CASCADE, related_name="modems"
    )
    interface = models.ForeignKey(
        Interface, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="monitoring_modems",
        help_text="Интерфейс роутера который представляет модем (LTE, USB)",
    )
    name = models.CharField(
        max_length=100,
        help_text="Например: 'МТС slot 1', 'USB Huawei E3372'",
    )
    enabled = models.BooleanField(default=True)

    # Стратегия поиска в Zabbix
    lookup_strategy = models.CharField(
        max_length=20,
        choices=ModemLookupStrategy.choices,
        default=ModemLookupStrategy.PUBLIC_IP,
    )
    lookup_value = models.CharField(
        max_length=255, blank=True,
        help_text="IP / hostname / item key — зависит от стратегии",
    )

    class Meta:
        ordering = ["host", "name"]
        verbose_name = "Monitored Modem"
        verbose_name_plural = "Monitored Modems"

    def __str__(self):
        return f"{self.name} ({self.host})"
