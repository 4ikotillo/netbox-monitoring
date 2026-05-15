from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModemSpec:
    """Что детектор предлагает добавить как модем."""
    name: str
    interface_id: Optional[int] = None
    interface_name: str = ""
    hint: str = ""  # подсказка для пользователя


class AbstractDetector:
    """Базовый класс детектора модемов на устройстве."""

    # Условие применимости: list of (manufacturer_slug, model_substring)
    # либо list of (manufacturer_slug, None) для любой модели производителя
    matches = []  # type: list

    @classmethod
    def applies_to(cls, device) -> bool:
        if not device.device_type:
            return False
        manuf_slug = ""
        if device.device_type.manufacturer:
            manuf_slug = device.device_type.manufacturer.slug.lower()
        model = (device.device_type.model or "").lower()
        for m_slug, m_substr in cls.matches:
            if manuf_slug == m_slug.lower():
                if m_substr is None or m_substr.lower() in model:
                    return True
        return False

    @classmethod
    def detect(cls, device) -> List[ModemSpec]:
        raise NotImplementedError
