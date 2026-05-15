from django import forms
from dcim.models import Interface
from ..models.monitoring import MonitoredModem, ModemLookupStrategy


class ModemForm(forms.ModelForm):
    class Meta:
        model = MonitoredModem
        fields = [
            "name", "interface", "lookup_strategy", "lookup_value", "enabled",
        ]
        help_texts = {
            "name": "Например: 'МТС slot 1', 'USB Huawei E3372'",
            "interface": "Какой интерфейс роутера представляет модем",
            "lookup_strategy": (
                "Как Internet Checker идентифицирует этот модем в Zabbix. "
                "Public IP — модем заведён как отдельный хост по своему публичному IP. "
                "Hostname — по имени хоста в Zabbix. "
                "Item key — это item на хосте роутера."
            ),
            "lookup_value": (
                "Public IP: '85.142.x.x'. Hostname: 'modem-msk-01'. "
                "Item key: 'inet.checker.status[modem1]'"
            ),
        }

    def __init__(self, *args, host=None, **kwargs):
        super().__init__(*args, **kwargs)
        if host:
            self.fields["interface"].queryset = Interface.objects.filter(
                device=host.device
            ).order_by("name")
            self.fields["interface"].required = False
