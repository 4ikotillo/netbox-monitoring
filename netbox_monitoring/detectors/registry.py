from typing import List
from .base import AbstractDetector, ModemSpec

_DETECTORS = []


def register_detector(cls):
    """Декоратор для регистрации детектора."""
    _DETECTORS.append(cls)
    return cls


def detect_modems(device) -> List[ModemSpec]:
    """
    Прогоняет все детекторы по устройству, возвращает список найденных модемов.
    Если несколько детекторов подходят — берётся первый. Generic — последний fallback.
    """
    for det in _DETECTORS:
        if det is GenericDetector:
            continue
        if det.applies_to(device):
            return det.detect(device)
    # Fallback на generic
    return GenericDetector.detect(device)


# Forward reference resolver — generic импортируется ниже в __init__
from .generic import GenericDetector  # noqa: E402
