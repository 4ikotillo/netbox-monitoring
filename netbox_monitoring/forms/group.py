from django import forms
from dcim.models import Device
from ..models.groups import MonitoringGroup


class MonitoringGroupForm(forms.ModelForm):
    devices = forms.ModelMultipleChoiceField(
        queryset=Device.objects.filter(
            primary_ip4__isnull=False
        ).select_related("site").order_by("site__name", "name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 12, "class": "form-select"}),
        help_text="Hold Ctrl/Cmd to multi-select. Only devices with Primary IP shown.",
    )

    class Meta:
        model = MonitoringGroup
        fields = ["name", "description", "devices"]
