import locale
import platform
import subprocess
import shutil
import json
from monitoring.base import BaseObject, SubObject

from logger.logger_monitoring import logger_monitoring

class DisksMonitor(BaseObject):
    def __init__(self):
        super().__init__()
        self.disks = {}
        self.disks_info = {}
        self.item_index = {}
        self.system = platform.system()
        self.iostat_available = shutil.which("iostat") is not None
        self.wmic_available = shutil.which("wmic") is not None

        try:
            command = ['smartctl', '--scan', '-j']
            encoding = locale.getpreferredencoding()
            result = subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding)
            result_json = json.loads(result)
            all_disks = result_json.get("devices", [])
            print(all_disks)
            for dev in all_disks:
                name = dev.get("name")
                dev_type = dev.get("type")
                if dev_type not in ["ata", "nvme", "scsi"]:
                    continue
                self.disks[name] = Disk(name, dev_type)
                #disk_index = self.__replace_device_name(name, True)
                self.disks_info[name] = f"disk:{len(self.disks) - 1}"
        except Exception as e:
            logger_monitoring.error(f"Ошибка выполнения команды smartctl --scan: {e}")

    def update(self):
        disks_speed = self.__get_disks_rw_speed()
        for name, disk in self.disks.items():
            speed = disks_speed.get(name, {"read": None, "write": None})
            disk.update(speed)

    def get_all(self):
        return [{index: disk.get_params_all()} for index, disk in self.disks.items()]

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            logger_monitoring.error(f"Ошибка при вызове item_id - {item_id}: {metric_id} - {e}")
            return None

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

    def get_objects_description(self):
        return self.disks_info

    @staticmethod
    def __replace_device_name(index_or_name, reverse=False):
        if reverse:
            name = index_or_name
            if not name.startswith("/dev/sd"):
                return None
            suffix = name[7:]
            result = 0
            for char in suffix:
                result = result * 26 + (ord(char) - ord('a') + 1)
            return str(result - 1)
        else:
            index = index_or_name
            if index < 0:
                return None
            letters = []
            while index >= 0:
                letters.append(chr(ord('a') + (index % 26)))
                index = (index // 26) - 1
            return f"/dev/sd{''.join(reversed(letters))}"

    def __get_disks_rw_speed(self):
        if self.system == "Windows":
            return self.__get_windows_disk_speed() if self.wmic_available else {}
        elif self.system == "Linux":
            return self.__get_linux_disk_speed() if self.iostat_available else {}
        else:
            logger_monitoring.error("Ошибка: Поддерживаются только Windows и Linux.")
            return {}

    def __get_windows_disk_speed(self):
        cmd = 'wmic path Win32_PerfFormattedData_PerfDisk_PhysicalDisk get Name,DiskReadBytesPersec,DiskWriteBytesPersec'
        try:
            result = subprocess.check_output(cmd, shell=True, text=True)
            lines = result.strip().split("\n")
            disk_speeds = {}
            for line in lines[1:]:
                data = line.split()
                if len(data) >= 3:
                    disk_name, read_speed, write_speed = data[2], data[0], data[1]
                    if disk_name == "_Total":
                        continue
                    disk_name = self.__replace_device_name(int(disk_name))
                    try:
                        disk_speeds[disk_name] = {"read": float(read_speed), "write": float(write_speed)}
                    except ValueError:
                        disk_speeds[disk_name] = {"read": None, "write": None}
            return disk_speeds
        except Exception as e:
            logger_monitoring.error(f"Ошибка при получении данных о скорости дисков в Windows: {e}")
            return {}

    @staticmethod
    def __get_linux_disk_speed():
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
                        # if "nvme" in disk_name:
                        #     disk_name = data[0][:5]
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


class Disk(SubObject):
    def __init__(self, name: str, interface_type: str):
        super().__init__()
        self.name = name
        self.interface_type = interface_type
        self.params = {
            "disk.write.bytes.per.sec": None,
            "disk.read.bytes.per.sec": None,
            "disk.temperature": None,
            "disk.power.on.hours": None,
            "disk.read.error.rate": None,
            "disk.seek.error.rate": None,
            "disk.reallocated.sectors.count": None
        }
        self.system = platform.system()

    def update(self, disks_speed):
        self.params["disk.write.bytes.per.sec"] = disks_speed.get("write")
        self.params["disk.read.bytes.per.sec"] = disks_speed.get("read")
        command = list()
        if self.system == "Windows":
            command = ['smartctl', '-a', '-j', '-d', self.interface_type, self.name]
        elif self.system == "Linux":
            command = ['smartctl', '-a', '-j', self.name]

        try:
            output = subprocess.check_output(command, text=True)
            data = json.loads(output)
        except Exception as e:
            logger_monitoring.error(f"Ошибка вызова команды {command} - {e}")
            return

        if "ata_smart_attributes" in data:
            attributes = data["ata_smart_attributes"].get("table", [])
            for attr in attributes:
                attr_id = attr.get("id")
                raw_value = attr.get("raw", {}).get("value")
                if attr_id == 1:
                    self.params["disk.read.error.rate"] = raw_value
                elif attr_id == 5:
                    self.params["disk.reallocated.sectors.count"] = raw_value
                elif attr_id == 7:
                    self.params["disk.seek.error.rate"] = raw_value
                elif attr_id == 9:
                    self.params["disk.power.on.hours"] = raw_value
                elif attr_id == 194:
                    self.params["disk.temperature"] = raw_value
                elif attr_id == 190:
                    self.params["disk.temperature"] = raw_value

        elif "nvme_smart_health_information_log" in data:
            nvme_data = data["nvme_smart_health_information_log"]
            self.params["disk.temperature"] = nvme_data.get("temperature")
            self.params["disk.power.on.hours"] = nvme_data.get("power_on_hours")
            self.params["disk.read.error.rate"] = None
            self.params["disk.seek.error.rate"] = None
            self.params["disk.reallocated.sectors.count"] = None

        elif "scsi_grown_defect_list" in data or "scsi_error_counter_log" in data or "scsi_version" in data:
            self.params["disk.seek.error.rate"] = None
            if "temperature" in data and isinstance(data["temperature"], dict):
                self.params["disk.temperature"] = data["temperature"].get("current")

            if "power_on_time" in data and isinstance(data["power_on_time"], dict):
                self.params["disk.power.on.hours"] = data["power_on_time"].get("hours")

            # Переназначенные сектора (аналог - список дефектов)
            if "scsi_grown_defect_list" in data:
                self.params["disk.reallocated.sectors.count"] = data["scsi_grown_defect_list"].get("glist")

            if "scsi_error_counter_log" in data:
                read_errors = data["scsi_error_counter_log"].get("read", {}).get("total_uncorrected_errors")
                self.params["disk.read.error.rate"] = read_errors

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    if metric_id in ["disk.read.bytes.per.sec", "disk.write.bytes.per.sec"]:
                        result = self.validate_double(result)
                    else:
                        result = self.validate_integer(result)
                return result
            else:
                raise KeyError(f"Ключ {metric_id} не найден в словаре параметров.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None

a = DisksMonitor()
a.update()
print(a.get_all())