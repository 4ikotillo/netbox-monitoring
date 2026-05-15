from .registry import detect_modems, register_detector
from .base import AbstractDetector, ModemSpec

# Регистрируем встроенные детекторы — импорт триггерит decorator
from . import huawei, tplink, sistematics, generic  # noqa

__all__ = [
    "detect_modems",
    "register_detector",
    "AbstractDetector",
    "ModemSpec",
]
