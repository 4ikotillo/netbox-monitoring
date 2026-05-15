from .base import AbstractDetector, ModemSpec
from .registry import register_detector


@register_detector
class TpLinkUsbDetector(AbstractDetector):
    """
    TP-Link MR3020/MR3040/etc — USB-порт для внешнего LTE-модема (Huawei E3372).
    Ищем интерфейсы name=usb* с типом 'other'.
    """
    matches = [
        ("tp-link", "mr"),
        ("tplink", "mr"),
    ]

    @classmethod
    def detect(cls, device):
        specs = []
        for iface in device.interfaces.all():
            name_l = iface.name.lower()
            if name_l.startswith("usb"):
                specs.append(ModemSpec(
                    name=f"USB modem ({iface.name})",
                    interface_id=iface.pk,
                    interface_name=iface.name,
                    hint=(
                        "TP-Link с USB-модемом. Подключите Huawei E3372 "
                        "и укажите его публичный IP в стратегии поиска."
                    ),
                ))
        return specs
