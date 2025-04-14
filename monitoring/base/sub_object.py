from abc import ABC, abstractmethod
from monitoring.base.validator import ValidationMixin

class SubObject(ValidationMixin, ABC):
    def __init__(self):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass

    @abstractmethod
    def get_params_all(self):
        pass

    @abstractmethod
    def get_metric(self, metric_id: str):
        pass