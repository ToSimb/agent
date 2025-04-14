from abc import ABC, abstractmethod
from monitoring.base.validator import ValidationMixin

class BaseObject(ValidationMixin, ABC):
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