import platform
import subprocess
from monitoring.base import BaseObject, SubObject

from logger.logger_monitoring import logger_monitoring

class DisksLigthMonitor(BaseObject):
    def __init__(self):
        super().__init__()
        self.disks = {}
        self.disks_info = {}
        self.item_index = {}
        self.system = platform.system()

        disks_list = []
        if self.system == "Linux":
            disks_list = self.__get_linux_disk()
        elif self.system == "Windows":
            pass

        for disk in disks_list:
            self.disks[disk] = Disk()
            self.disks_info[disk] = f"disk:{disk.split('/')[-1]}"

    @staticmethod
    def __get_linux_disk():
        devs = []
        out = subprocess.check_output(["iostat", "-d", "-k", "1", "1"], text=True )
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0] not in ("Device", "Linux") and "loop" not in parts[0]:
                devs.append(f"/dev/{parts[0]}")
        return devs

    def update(self):
        disks_speed = self.__get_disks_rw_speed()
        # вот так должно быть
        # {'/dev/sdd': {'read': 0.0, 'write': 0.0}, '/dev/sdc': {'read': 0.0, 'write': 0.0}, '/dev/sdb': {'read': 0.0, 'write': 0.0}, '/dev/sda': {'read': 0.0, 'write': 0.0}, '/dev/nvme0': {'read': 0.0, 'write': 0.0}}
        for key, value in disks_speed.items():
            self.disks.get(key).update(value)

    def __get_disks_rw_speed(self):
        if self.system == "Windows":
            pass
            # return self.__get_windows_disk_speed() if self.wmic_available else {}
        elif self.system == "Linux":
            return self.__get_linux_disk_speed() if self.iostat_available else {}
        else:
            logger_monitoring.error("Ошибка: Поддерживаются только Windows и Linux.")
            return None

    @staticmethod
    def __get_linux_disk_speed():
        """Получает скорость чтения и записи дисков в Linux с помощью iostat."""
        try:
            result = subprocess.run(["iostat", "-d", "-k", "1", "2"],
                                    capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")
            disk_speeds = {}
            for line in reversed(lines):
                if line:
                    data = line.split()
                    if len(data) >= 4:
                        disk_name, read_speed, write_speed = data[0], data[2], data[3]

                        if disk_name == 'Device':
                            break
                        try:
                            if 'loop' not in disk_name:
                                read_speed = float(read_speed.replace(",", ".")) * 1024
                                write_speed = float(write_speed.replace(",", ".")) * 1024
                                disk_speeds[f"/dev/{disk_name}"] = {"read": read_speed, "write": write_speed}
                        except ValueError:
                            disk_speeds[f"/dev/{disk_name}"] = {"read": None, "write": None}
            return disk_speeds
        except Exception as e:
            logger_monitoring.error(f"Ошибка при получении данных о скорости дисков в Linux: {e}")
            return {}

    def get_objects_description(self):
        return self.disks_info

    def create_index(self, disk_dict: dict):
        for index in disk_dict:
            if disk_dict[index] is not None:
                for key, value in self.disks_info.items():
                    if value == index:
                        self.item_index[str(disk_dict[index])] = self.disks.get(key, None)
                        break
                else:
                    logger_monitoring.debug(f'Для индекса {index} нет значения')
        logger_monitoring.info("Индексы для дисков обновлены")

    def get_all(self):
        return [{index: obj.get_params_all()} for index, obj in self.disks.items()]

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            logger_monitoring.error(f"Ошибка при вызове item_id - {item_id}: {metric_id} - {e}")
            return None

class Disk(SubObject):
    def __init__(self):
        super().__init__()
        self.params = {
            "disk.write.bytes.per.sec": None,
            "disk.read.bytes.per.sec": None,
        }

    def update(self, disks_speed):
        result = {"disk.write.bytes.per.sec": disks_speed["write"], "disk.read.bytes.per.sec": disks_speed["read"]}
        self.params.update(result)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    result = self.validate_double(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None
