class ValidationMixin:
    @staticmethod
    def validate_string(value):
        return str(value)

    @staticmethod
    def validate_integer(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_double(value):
        try:
            return round(float(str(value).replace(',', '.')), 2)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_state(value):
        allowed_states = {"OK", "WARN", "ERROR", "FATAL", "UNKNOWN"}
        val_str = str(value).upper().strip()
        result = val_str if val_str in allowed_states else None
        if result is None:
            return None
        return str(result)