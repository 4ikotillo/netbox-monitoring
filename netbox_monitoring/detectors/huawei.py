from .base import AbstractDetector, ModemSpec
from .registry import register_detector


@register_detector
class HuaweiDetector(AbstractDetector):
    """
    Huawei B315/B525/B612 — встроенный LTE-модуль.
    Ищем интерфейсы типа LTE.
    """
    matches = [
        ("huawei", None),
    ]

    @classmethod
    def detect(cls, device):
        specs = []
        for iface in device.interfaces.all():
            t = (iface.type or "").lower()
            if "lte" in t or "lte" in iface.name.lower():
                specs.append(ModemSpec(
                    name=f"LTE {iface.name}",
                    interface_id=iface.pk,
                    interface_name=iface.name,
                    hint="Встроенный LTE-модуль Huawei. Установите стратегию поиска по публичному IP.",
                ))
        return specs
