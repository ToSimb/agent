from typing import Optional, Set

class ValidationMixin:

    _ALLOWED_STATES: Set[str] = {"OK", "WARN", "ERROR", "FATAL", "UNKNOWN"}

    @staticmethod
    def validate_string(value: object) -> str:
        return str(value)

    @staticmethod
    def validate_integer(value: object) -> Optional[int]:
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_double(value: object) -> Optional[float]:
        try:
            return round(float(str(value).replace(",", ".")), 2)
        except (ValueError, TypeError):
            return None

    @classmethod
    def validate_state(cls, value: object) -> Optional[str]:
        val = str(value).upper().strip()
        return val if val in cls._ALLOWED_STATES else None
