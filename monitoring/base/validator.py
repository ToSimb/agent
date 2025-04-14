class ValidationMixin:
    @staticmethod
    def validate_string(value):
        return str(value)

    @staticmethod
    def validate_integer(value):
        try:
            result = int(value)
        except (ValueError, TypeError):
            result = None
        return str(result)

    @staticmethod
    def validate_double(value):
        try:
            result = round(float(str(value).replace(',', '.')), 2)
        except (ValueError, TypeError):
            result = None
        return str(result)

    @staticmethod
    def validate_state(value):
        allowed_states = {"OK", "WARN", "ERROR", "FATAL", "UNKNOWN"}
        val_str = str(value).upper().strip()
        result = val_str if val_str in allowed_states else None
        return str(result)