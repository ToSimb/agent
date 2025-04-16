import subprocess
from monitoring.base import BaseObject, SubObject

from logger.logger_monitoring import logger_monitoring

class GPUsMonitor(BaseObject):
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            gpus (dict): Словарь, где ключ  - uuid gpu,
                            а значением - объект класса GPU.
                            Пример: {'GPU-70cfb510-d7fe-14a2-9b28-ba4943bc96f2': <__main__.GPU object at 0x74fefb6cea30>}
            gpus_info (dict): Словарь, где ключ -- uuid gpu,
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'GPU-70cfb510-d7fe-14a2-9b28-ba4943bc96f2': 'gpu:0'}
            item_index: Словарь, где ключ - это будущий item_id из схемы,
                        а значением - ссылка на объект класса GPU.
                        Пример: {'122': <__main__.GPU object at 0x74fefb6cea30>}
        """
        super().__init__()
        self.gpus = {}
        self.gpus_info = {}
        self.item_index = {}
        # не работает с --format=json
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,uuid", "--format=csv,noheader"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.splitlines()
        for line in lines:
            index, name, uuid_gpu = line.split(',')
            uuid_gpu = uuid_gpu.strip()
            self.gpus[uuid_gpu] = GPU(uuid_gpu)
            self.gpus_info[uuid_gpu] = f"gpu:{index}"

    def get_objects_description(self):
        return self.gpus_info

    def create_index(self, gpu_dict):
        """
        Пример gpu_dict:
            {
                "gpu:0": 121,
            }
        """
        for index in gpu_dict:
            if gpu_dict[index] is not None:
                for key, value in self.gpus_info.items():
                    if value == index:
                        self.item_index[str(gpu_dict[index])] = self.gpus.get(key, None)
                        break
            else:
                logger_monitoring.debug(f'Для индекса {index} нет значения')
        logger_monitoring.info("Индексы для GPU обновлены")

    def update(self):
        try:
            result = subprocess.run(
                ["nvidia-smi",
                 "--query-gpu=index,uuid,name,clocks.current.graphics,clocks.current.memory,utilization.gpu,utilization.memory,memory.used,fan.speed,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.splitlines()
        except:
            logger_monitoring.error("No GPUs found")
            return False

        for line in lines:
            values = line.split(",")
            for index in range(len(values)):
                values[index] = values[index].strip()
            if values[1] in self.gpus:
                result_line = {
                    "gpu.index": values[0],
                    "gpu.uuid": values[1],
                    "gpu.name": values[2],
                    "gpu.clocks.current.graphics": values[3],
                    "gpu.clocks.current.memory": values[4],
                    "gpu.utilization.gpu": values[5],
                    "gpu.utilization.memory": values[6],
                    "gpu.memory.used": values[7],
                    "gpu.fan.speed": values[8],
                    "gpu.temperature.gpu": values[9]
                }
                self.gpus.get(values[1]).update(result_line)
            else:
                logger_monitoring.error(f"uuid {values[1]} - не найден в списке объектов")
        return True

    def get_all(self):
        return_list = []
        for index_gpu in self.gpus.keys():
            result = self.gpus[index_gpu].get_params_all()
            return_list.append({index_gpu: result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id:str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            logger_monitoring.error(f"Ошибка при вызове item_id  - {item_id}: {metric_id} - {e}")
            return None

    def get_item_origin(self, uuid_gpu: str, metric_id:str):
        try:
            return self.gpus.get(uuid_gpu).get_metric(metric_id)
        except:
            logger_monitoring.error(f"ошибка - {uuid_gpu}: {metric_id}")
            return None

class GPU(SubObject):
    def __init__(self, uuid_gpu: str):
        super().__init__()
        self.params = {
            "gpu.index": None,
            "gpu.uuid": uuid_gpu,
            "gpu.name": None,
            "gpu.clocks.current.graphics": None,
            "gpu.clocks.current.memory": None,
            "gpu.utilization.gpu": None,
            "gpu.utilization.memory": None,
            "gpu.memory.used": None,
            "gpu.fan.speed": None,
            "gpu.temperature.gpu": None
        }

    def update(self, params_new: dict=None):
        self.params.update(params_new)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    if metric_id in ["gpu.index", "gpu.clocks.current.graphics", "gpu.clocks.current.memory", "gpu.utilization.gpu",
                                     "gpu.utilization.memory", "gpu.memory.used", "gpu.fan.speed", "gpu.temperature.gpu"]:
                        result = self.validate_integer(result)
                    else:
                        result = self.validate_string(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None