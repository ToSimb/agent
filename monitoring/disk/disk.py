import locale
import platform
import subprocess
import shutil
import json
from base import BaseObject
from base import SubObject


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
            command = ['smartctl', '--scan']
            encoding = locale.getpreferredencoding()
            result = subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding).strip().split("\n")
            if result:
                all_disks = [[line.split()[0], line.split()[2]] for line in result if line.strip()]
                for disk in all_disks:
                    self.disks[disk[0]] = Disk(disk)
                    disk_index = self.__replace_device_name(disk[0], True)
                    self.disks_info[disk[0]] = f"disk:{disk_index}"
        except Exception as e:
            print(f"Ошибка выполнения команды {command}: {e}")

    def update(self):
        disks_speed = self.__get_disks_rw_speed()
        for key, disk in self.disks.items():
            disk.update(disks_speed[key])

    def get_all(self):
        return [{index: gpu.get_params_all()} for index, gpu in self.disks.items()]

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            print(f"Ошибка - {item_id}: {metric_id} - {e}")
            return None

    def create_index(self, disk_dict: dict):
        for index in disk_dict:
            if disk_dict[index] is not None:
                for key, value in self.disks_info.items():
                    if value == index:
                        self.item_index[str(disk_dict[index])] = self.disks.get(key, None)
                        break
                else:
                    print(f'Для индекса {index} нет значения')
        print("Индексы для дисков обновлены")

    def get_objects_description(self):
        return self.disks_info

    @staticmethod
    def __replace_device_name(index_or_name, reverse=False):
        if reverse:
            # Ожидаем имя устройства, например: "/dev/sdab"
            name = index_or_name
            if not name.startswith("/dev/sd"):
                return None
            suffix = name[7:]  # удаляем "/dev/sd"
            result = 0
            for char in suffix:
                result = result * 26 + (ord(char) - ord('a') + 1)
            return str(result - 1)
        else:
            # Ожидаем индекс, например: 27
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
            print("Ошибка: Поддерживаются только Windows и Linux.")
            return None

    def __get_windows_disk_speed(self):
        """Получает скорость чтения и записи дисков в Windows с помощью wmic."""
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
            print(f"Ошибка при получении данных о скорости дисков в Windows: {e}")
            return {}

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

                        # Слабое место - необходимо больше данных!
                        if "nvme" in disk_name:
                            disk_name = data[0][:5]

                        if disk_name == 'Device':
                            break
                        try:
                            if 'loop' not in disk_name:
                                read_speed = float(read_speed.replace(",", ".")) * 1024
                                write_speed = float(write_speed.replace(",", ".")) * 1024
                                disk_speeds[f"/dev/{disk_name}"] = {"read": read_speed, "write": write_speed}
                        except ValueError:
                            print("!")
                            disk_speeds[f"/dev/{disk_name}"] = {"read": None, "write": None}
            return disk_speeds
        except Exception as e:
            print(f"Ошибка при получении данных о скорости дисков в Linux: {e}")
            return {}


class Disk(SubObject):
    def __init__(self, disk_indo: list):
        super().__init__()
        self.name = disk_indo[0]
        self.interface_type = disk_indo[1]
        self.params = {
            "disk.write.bytes.per.sec": None,
            "disk.temperature": None,
            "disk.seek.error.rate": None,
            "disk.read.error.retry.rate": None,
            "disk.reallocated.sectors.count": None,
            "disk.read.bytes.per.sec": None,
            "disk.head.flying.hours": None
        }
        self.system = platform.system()

    def update(self, disks_speed):
        result = {"disk.write.bytes.per.sec": disks_speed["write"], "disk.read.bytes.per.sec": disks_speed["read"]}

        if self.system == "Windows":
            command = ['smartctl', '-A', '-j', '-d', self.interface_type, self.name]
        else:
            command = ['smartctl', '-A', '-j', self.name]

        try:
            output = subprocess.check_output(command, text=True)
            if not output:
                return
            data = json.loads(output)
        except Exception as e:
            print(f"Ошибка вызова команды {command} - {e}")
            return

        if data.get("ata_smart_attributes"):
            attributes = data.get("ata_smart_attributes", {}).get("table", [])
            for attr in attributes:
                attr_name = attr.get("name", "").lower()

                if "temperature_celsius" in attr_name or "airflow_temperature_cel" in attr_name:
                    result["disk.temperature"] = attr.get("raw", None).get("value")

                elif "seek_error_rate" in attr_name:
                    result["disk.seek.error.rate"] = attr.get("raw", None).get("value")

                elif "raw_read_error_rate" in attr_name:
                    result["disk.read.error.retry.rate"] = attr.get("raw", None).get("value")

                elif "reallocated_sector_ct" in attr_name:
                    result["disk.reallocated.sectors.count"] = attr.get("raw", None).get("value")

                elif "power_on_hours" in attr_name:
                    result["disk.head.flying.hours"] = attr.get("raw", None).get("value")

        elif data.get("nvme_smart_health_information_log"):
            attributes = data.get("nvme_smart_health_information_log", {})

            if "temperature" in attributes:
                result["disk.temperature"] = attributes.get("temperature", None)

            if "power_on_hours" in attributes:
                result["disk.head.flying.hours"] = attributes.get("power_on_hours", None)

            if "power_cycles" in attributes:
                result["disk.power.cycles"] = attributes.get("power_cycles", None)

        self.params.update(result)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    if metric_id in ["disk.read.bytes.per.sec", "disk.write.bytes.per.sec"]:
                        result = self.validate_value("double", result)
                    else:
                        result = self.validate_value("integer", result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None