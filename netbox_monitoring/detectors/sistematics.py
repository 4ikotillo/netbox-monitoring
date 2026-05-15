from .base import AbstractDetector, ModemSpec
from .registry import register_detector


@register_detector
class SistematicsDetector(AbstractDetector):
    """
    Sistematics MMS-424-SAC-NW — LTE-агрегатор с 4 USB-модемами.
    Интерфейсы названы usb_m1..usb_m4.
    """
    matches = [
        ("sistematics", None),
    ]

    @classmethod
    def detect(cls, device):
        specs = []
        for iface in device.interfaces.filter(name__startswith="usb_m").order_by("name"):
            specs.append(ModemSpec(
                name=f"Modem {iface.name}",
                interface_id=iface.pk,
                interface_name=iface.name,
                hint=(
                    "Sistematics modem slot. Каждый usb_m* = отдельный USB-модем "
                    "с SIM-картой. Установите стратегию по публичному IP или ключу item."
                ),
            ))
        return specs
