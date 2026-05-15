from django import forms
from ..models.zabbix import ZabbixServer


class ZabbixServerForm(forms.ModelForm):
    class Meta:
        model = ZabbixServer
        fields = ["name", "url", "username", "password", "token", "is_active"]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
            "token": forms.PasswordInput(render_value=True),
            "url": forms.URLInput(attrs={
                "placeholder": "http://zabbix.example.com/zabbix",
            }),
        }
        help_texts = {
            "username": "Zabbix 5.x: login + password",
            "token": "Zabbix 6.x+: API token only",
        }
