from abc import ABC, abstractmethod


class BaseObject(ABC):
    def __init__(self):
        pass
        #Переменные класса можно назвать одинаково и реализовать здесь методы
        #и они будут не абстрактные

    @abstractmethod
    def get_objects_description(self):
        pass

    @abstractmethod
    def create_index(self, object_dict: dict):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_item_and_metric(self, item_id: str, metric_id: str):
        pass

    @staticmethod
    def validate_value(type_: str, value):
        result = None
        if type_ == "string":
            result = str(value)
        elif type_ == "integer":
            try:
                result = int(value)
            except (ValueError, TypeError):
                result = None
        elif type_ == "double":
            try:
                result = round(float(str(value).replace(',', '.')), 2)
            except (ValueError, TypeError):
                result = None

        elif type_ == "state":
            allowed_states = {"OK", "WARN", "ERROR", "FATAL", "UNKNOWN"}
            val_str = str(value).upper().strip()
            result = val_str if val_str in allowed_states else None

        return str(result)