import json
import psutil
import pynvml


class ServerSchemaGenerator:
    def __init__(self):
        self.metrics = {}
        self.templates = []
        self.item_id_list = []
        self.item_info_list = []
        self.template_map = {}

    def add_metric(self, metric_id, name, dimension, query_interval=10, type_="double", comment=None, is_config=False,
                   err_thr_max=None, err_thr_min=None):
        if metric_id not in self.metrics:
            metric = {
                "metric_id": metric_id,
                "name": name,
                "dimension": dimension,
                "query_interval": query_interval,
                "type": type_
            }
            if comment:
                metric["comment"] = comment
            if is_config:
                metric["is_config"] = True
            if err_thr_max:
                metric["err_thr_max"] = err_thr_max
            if err_thr_min:
                metric["err_thr_min"] = err_thr_min
            self.metrics[metric_id] = metric

    def add_template(self, template_id, name, metrics=None, includes=None, description=None):
        template = {"template_id": template_id, "name": name}
        if metrics:
            template["metrics"] = metrics
        if includes:
            template["includes"] = includes
        if description:
            template["description"] = description
        self.templates.append(template)
        self.template_map[template_id] = template

    def add_item(self, full_path, item_id=None, serial_number=None, comment=None):
        self.item_id_list.append({"full_path": full_path, "item_id": item_id})
        if serial_number or comment:
            item_info = {"full_path": full_path, "sn": serial_number, "comment": comment}
            self.item_info_list.append({k: v for k, v in item_info.items() if v})

    def generate_schema(self):
        return {
            "scheme_revision": 0,
            "scheme": {
                "metrics": list(self.metrics.values()),
                "templates": self.templates,
                "item_id_list": self.item_id_list,
                "item_info_list": self.item_info_list
            }
        }

    def auto_discover(self):
        cpu_count = psutil.cpu_count(logical=False) or 0
        if cpu_count > 0:
            self.add_template("cpu_generic", "Процессор", ["cpu.user.time", "cpu.core.load"])
            for i in range(cpu_count):
                self.add_item(f"cpu_generic[{i}]")

        if psutil.virtual_memory().total > 0:
            self.add_template("ram_generic", "Оперативная память", ["chassis.memory.total"])
            self.add_item("ram_generic[0]", serial_number="RAM_SN_123456")

        # gpu_count = 0
        # try:
        #     pynvml.nvmlInit()
        #     gpu_count = pynvml.nvmlDeviceGetCount() or 0
        #     if gpu_count > 0:
        #         self.add_template("gpu_nvidia", "GPU Nvidia",
        #                           ["gpu.utilization", "gpu.memory.total", "gpu.memory.used"])
        #         for i in range(gpu_count):
        #             handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        #             serial_number = pynvml.nvmlDeviceGetSerial(handle).decode("utf-8")
        #             self.add_item(f"gpu_nvidia[{i}]", serial_number=serial_number)
        # except Exception as e:
        #     print(f"Ошибка при обнаружении GPU: {e}")
        # finally:
        #     pynvml.nvmlShutdown()

        metrics = [
            ("cpu.user.time", "% времени польз. операций", "%", "double",
             "% времени, кот. ЦП тратит на пользоват. операции за 1 секунд"),
            ("cpu.core.load", "Загрузка процессора", "%"),
            ("chassis.memory.total", "Общее кол-во опер. пам.", "B", "integer", None, True),
            ("gpu.utilization", "Загрузка GPU", "%"),
            ("gpu.memory.total", "Объем видеопамяти", "B", "integer"),
            ("gpu.memory.used", "Используемая видеопамять", "B", "integer")
        ]

        for metric in metrics:
            self.add_metric(*metric)

        includes = []
        if cpu_count > 0:
            includes.append({"count": cpu_count, "template_id": "cpu_generic"})
        if psutil.virtual_memory().total > 0:
            includes.append({"count": 1, "template_id": "ram_generic"})
        # if gpu_count > 0:
        #     includes.append({"count": gpu_count, "template_id": "gpu_nvidia"})

        if includes:
            self.add_template("server_auto", "Автообнаруженный сервер", ["chassis.uptime"], includes=includes,
                              description="Сервер, обнаруженный автоматически")
            self.add_item("server_auto[0]", serial_number="SERVER_SN_987654")


# Запуск автоматического создания схемы
generator = ServerSchemaGenerator()
generator.auto_discover()
schema = generator.generate_schema()
print(json.dumps(schema, indent=4, ensure_ascii=False))
