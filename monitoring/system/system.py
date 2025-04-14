import time
import psutil
from monitoring.base import BaseObject


class SystemMonitor(BaseObject):
    def __init__(self):
        """
        Инициализация единственного экземпляра класса!

        Атрибуты:
            system_info (dict): ЗАГУЛШКА! Словарь, где ключ - 0 (статический id для одного экземпляра),
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {"0": "chassis:0"}
            item_index: Значение item_id из будущей схемы
        """
        super().__init__()
        self.system_info = {
            "0": "chassis:0"
        }
        self.item_index = None
        self.params = {
            "chassis.uptime": None,
            "chassis.core.count": None,
            "chassis.logic.count": None,
            "chassis.load.avg": None,
            "chassis.irq": None,
            "chassis.memory.total": None,
            "chassis.memory.used": None,
            "chassis.memory.available": None,
            "chassis.swap.total": None,
            "chassis.swap.used": None,
            "chassis.swap.available": None
        }

    def update(self):
        uptime = psutil.boot_time()
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        load_avg = psutil.cpu_percent(interval=0.2)
        core_count = psutil.cpu_count(logical=False)
        logic_count = psutil.cpu_count(logical=True)
        cpu_stats = psutil.cpu_stats()

        result = {
            "chassis.uptime": int(time.time() - uptime),
            "chassis.core.count": core_count,
            "chassis.logic.count": logic_count,
            "chassis.load.avg": load_avg,
            "chassis.irq": cpu_stats.interrupts,
            "chassis.memory.total": vm.total,
            "chassis.memory.used": vm.used,
            "chassis.memory.available": vm.free,
            "chassis.swap.total": swap.total,
            "chassis.swap.used": swap.used,
            "chassis.swap.available": swap.free
        }
        self.params.update(result)

    def get_objects_description(self):
        return self.system_info

    def create_index(self, system_dict):
        for index in system_dict:
            if system_dict[index] is not None:
                for key, value in self.system_info.items():
                    if value == index:
                        self.item_index = str(system_dict[index])
                        break
                else:
                    print(f'Для индекса {index} нет значения')
        print("Индексы для SYSTEM обновлены")

    def get_all(self):
        return_list = [self.params]
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            if item_id == self.item_index:
                if metric_id in self.params:
                    result = self.params[metric_id]
                    if result is not None:
                        self.params[metric_id] = None
                        if metric_id in ["chassis.load.avg"]:
                            result = self.validate_double(result)
                        else:
                            result = self.validate_integer(result)
                    return result
                else:
                    raise KeyError(f"Ключ не найден в словаре.")
            else:
                raise KeyError(f"Не найден такой item_id")
        except Exception as e:
            print(f"Ошибка в запросе item - {item_id}, метрики {metric_id} - {e}")
            return None