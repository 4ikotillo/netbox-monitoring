from .base import AbstractDetector, ModemSpec


class GenericDetector(AbstractDetector):
    """
    Fallback: ищет интерфейсы с признаками LTE/USB/cellular.
    Не регистрируется в registry — используется явно как последний шанс.
    """
    matches = []

    @classmethod
    def detect(cls, device):
        specs = []
        for iface in device.interfaces.all():
            name_l = iface.name.lower()
            type_l = (iface.type or "").lower()
            is_lte = "lte" in type_l or "lte" in name_l or "cellular" in name_l
            is_usb = name_l.startswith("usb") and ("other" in type_l or "lte" in type_l)
            if is_lte or is_usb:
                specs.append(ModemSpec(
                    name=f"Modem {iface.name}",
                    interface_id=iface.pk,
                    interface_name=iface.name,
                    hint="Generic detection — please verify and configure lookup strategy.",
                ))
        return specs
