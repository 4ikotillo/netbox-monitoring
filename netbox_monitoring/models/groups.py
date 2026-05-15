from django.db import models
from netbox.models import NetBoxModel
from dcim.models import Device


class MonitoringGroup(NetBoxModel):
    """Кастомная группа: устройства из разных сайтов в одну панель."""
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    devices = models.ManyToManyField(
        Device, related_name="monitoring_groups", blank=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Monitoring Group"
        verbose_name_plural = "Monitoring Groups"

    def __str__(self):
        return self.name
