import subprocess
import uuid


class GPUsMonitor:
    def __init__(self):
        self.gpus = {}
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"],
            capture_output=True, text=True, check=True
        )
        for uuid in result.stdout.split("\n"):
            if uuid:
                self.gpus[uuid.strip()] = uuid
                self.gpus[uuid] = GPU(uuid)

    def validate_value_int(self, value):
        try:
            return int(value)
        except:
            return None

    def validate_value_float(self, value):
        try:
            return float(value)
        except:
            return None

    def update(self):
        try:
            result = subprocess.run(
                ["nvidia-smi",
                 "--query-gpu=index,uuid,name,clocks.current.graphics,clocks.current.memory,utilization.gpu,utilization.memory,memory.used,fan.speed,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split("\n")
        except:
            print("No GPUs found")
            return None

        for line in lines:
            values = line.split(", ")
            if values[1] in self.gpus:
                result_line = {
                    "gpu.index": self.validate_value_int(values[0]),
                    "gpu.uuid": values[1],
                    "gpu.name": values[2],
                    "gpu.clocks.current.graphics": self.validate_value_int(values[3]),
                    "gpu.clocks.current.memory": self.validate_value_int(values[4]),
                    "gpu.utilization.gpu": self.validate_value_int(values[5]),
                    "gpu.utilization.memory": self.validate_value_int(values[6]),
                    "gpu.memory.used": self.validate_value_int(values[7]),
                    "gpu.fan.speed": self.validate_value_int(values[8]),
                    "gpu.temperature.gpu": self.validate_value_int(values[9])
                }
                self.gpus.get(values[1]).update_params(result_line)
            else:
                print(f"uuid {values[1]} - не найден в списке объектов")

    def get_all(self):
        for uuid in self.gpus.values():
            aaa = uuid.get_params_all()

    def get_item_all(self, uuid: str):
        try:
            return self.gpus.get(uuid).get_params_all()
        except:
            return None

    def get_item(self, uuid: str, metric_id:str):
        try:
            return self.gpus.get(uuid).get_metric(metric_id)
        except:
            print(f"ошибка - {uuid}: {metric_id}")
            return None


class GPU:
    def __init__(self, uuid: str):
        self.params = {
            "gpu.index": None,
            "gpu.uuid": uuid,
            "gpu.name": None,
            "gpu.clocks.current.graphics": None,
            "gpu.clocks.current.memory": None,
            "gpu.utilization.gpu": None,
            "gpu.utilization.memory": None,
            "gpu.memory.used": None,
            "gpu.fan.speed": None,
            "gpu.temperature.gpu": None
        }

    def update_params(self, params_new: dict):
        self.params.update(params_new)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None
