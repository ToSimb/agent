#import locale
import os
import platform
import subprocess
import shutil
import json
from monitoring.base import BaseObject, SubObject
from logger.logger_mon_disk import logger_monitoring


class DisksMonitor(BaseObject):
    def __init__(self):
        super().__init__()
        self.disks = {}
        self.disks_info = {}
        self.item_index = {}

        self.system = platform.system()
        self.iostat_available = shutil.which("iostat") is not None
        self.wmic_available = shutil.which("wmic") is not None
        self.smartctl_available = True

        self.smartctl_dir = r"C:\Users\prom\Documents\Agent_VKL\smartmontools\bin"
        self.smartctl_path = os.path.join(self.smartctl_dir, "smartctl.exe")
        self.env = os.environ.copy()
        self.env["PATH"] = self.smartctl_dir + ";" + self.env.get("PATH", "")

        if self.smartctl_available:
            try:
                cmd = [self.smartctl_path, '--scan', '-j']
                #encoding = locale.getpreferredencoding()
                output = subprocess.run(cmd, cwd=self.smartctl_dir, env=self.env, capture_output=True)
                data = json.loads(output.stdout)
                devices = data.get("devices", [])
                for dev in devices:
                    name = dev.get("name")
                    dev_type = dev.get("type")
                    if dev_type not in ["ata", "nvme", "scsi"] or not name:
                        continue
                    self.disks[name] = Disk(name=name,
                                            interface_type=dev_type,
                                            smartctl_available=self.smartctl_available,
                                            smartctl_dir=self.smartctl_dir,
                                            smartctl_path=self.smartctl_path,
                                            env=self.env)
                    self.disks_info[name] = f"disk:{name}"
            except Exception as e:
                logger_monitoring.warning(f"Нет прав администратора или ошибка при сканировании дисков: {e}")
        else:
            logger_monitoring.info("smartctl не найден в системе, невозможно собрать SMART параметры.")

        # Добавление дисков которые smartctl не увидел
        speeds = self.__get_disks_rw_speed() or {}
        for name in speeds.keys():
            if name not in self.disks:
                self.disks[name] = Disk(name=name,
                                            interface_type="auto",
                                            smartctl_available=self.smartctl_available,
                                            smartctl_dir=self.smartctl_dir,
                                            smartctl_path=self.smartctl_path,
                                            env=self.env)
                self.disks_info[name] = f"disk:{name}"

    def update(self):
        speeds = self.__get_disks_rw_speed() or {}
        for name, disk in self.disks.items():
            disk_speed = speeds.get(name, {"read": None, "write": None})
            disk.update(disk_speed)

    def get_all(self):
        return [{self.disks_info[name]: disk.get_params_all()} for name, disk in self.disks.items()]

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            disk = self.item_index.get(item_id)
            return disk.get_metric(metric_id) if disk else None
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

    def __get_disks_rw_speed(self):
        if self.system == "Windows":
            if not self.wmic_available:
                logger_monitoring.warning(f"wmic не найден в Windows, невозможно собрать скорости чтения и записи.")
                return {}
            return self.__get_windows_disk_speed()
        elif self.system == "Linux":
            if not self.iostat_available:
                logger_monitoring.warning("iostat не найден в Linux, невозможно собрать скорости чтения и записи.")
                return {}
            return self.__get_linux_disk_speed()
        else:
            logger_monitoring.error("ОС не поддерживается.")
            return {}

    def __get_windows_disk_speed(self):
        cmd = ['wmic', 'path', 'Win32_PerfFormattedData_PerfDisk_PhysicalDisk',
               'get', 'Name,DiskReadBytesPersec,DiskWriteBytesPersec', '/format:csv']
        try:
            output = subprocess.check_output(cmd, text=True)
            lines = [line for line in output.splitlines() if line.strip()]
            speeds = {}
            for line in lines[1:]:
                parts = line.split(',')
                if len(parts) < 4:
                    continue
                _, read_b, write_b, disk_name = parts[:4]
                disk_name = disk_name.split()[0]
                if disk_name == "_Total":
                    continue
                try:
                    dev = self.__replace_device_name(int(disk_name))
                except Exception:
                    dev = None
                speeds[dev] = {"read": float(read_b), "write": float(write_b)}
            return speeds
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
                        if disk_name == 'Device':
                            break
                        try:
                            if 'loop' not in disk_name:
                                if "nvme" in disk_name:
                                    disk_name = disk_name[:-2]
                                read_speed = float(read_speed.replace(",", ".")) * 1024
                                write_speed = float(write_speed.replace(",", ".")) * 1024
                                disk_speeds[f"/dev/{disk_name}"] = {"read": read_speed, "write": write_speed}
                        except ValueError:
                            disk_speeds[f"/dev/{disk_name}"] = {"read": None, "write": None}
            return disk_speeds
        except Exception as e:
            logger_monitoring.error(f"Ошибка при получении данных о скорости дисков в Linux: {e}")
            return {}

    @staticmethod
    def __replace_device_name(index_or_name, reverse=False):
        if reverse:
            name = index_or_name
            if not name.startswith("/dev/sd"):
                return None
            suffix = name[7:]
            idx = 0
            for c in suffix:
                idx = idx * 26 + (ord(c) - ord('a') + 1)
            return str(idx - 1)
        else:
            idx = index_or_name
            if idx < 0:
                return None
            letters = []
            while idx >= 0:
                letters.append(chr(ord('a') + (idx % 26)))
                idx = idx // 26 - 1
            return f"/dev/sd{''.join(reversed(letters))}"

class Disk(SubObject):
    def __init__(self, name: str, interface_type, smartctl_available: bool, smartctl_dir, smartctl_path, env):
        super().__init__()
        self.name = name
        self.interface_type = interface_type
        self.smartctl_available = smartctl_available
        self.system = platform.system()
        self.smartctl_dir = smartctl_dir
        self.smartctl_path = smartctl_path
        self.env = env

        self.params = {
            "disk.write.bytes.per.sec": None,
            "disk.read.bytes.per.sec": None,
            "disk.temperature": None,
            "disk.power.on.hours": None,
            "disk.read.error.rate": None,
            "disk.seek.error.rate": None,
            "disk.reallocated.sectors.count": None,
            "disk.ecc.error.rate": None,
            "disk.uncorrectable.error.count": None
        }

    def update(self, speed: dict):
        self.params["disk.write.bytes.per.sec"] = speed.get("write")
        self.params["disk.read.bytes.per.sec"] = speed.get("read")
        if not self.smartctl_available:
            logger_monitoring.debug(f"SMART параметры пропущены для: {self.name}.")
            return

        if self.system == "Windows":
            cmd = [self.smartctl_path, '-a', '-j', '-d', self.interface_type, self.name]
        else:
            cmd = [self.smartctl_path, '-a', '-j', self.name]

        try:
            output = subprocess.run(cmd, cwd=self.smartctl_dir, env=self.env, capture_output=True)
            data = json.loads(output.stdout)
        except (PermissionError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger_monitoring.debug(f"SMART параметры пропущены для: {self.name}:\n{e}")
            return
        except Exception as e:
            logger_monitoring.error(f"Ошибка вызова команды {cmd}\n{e}")
            return

        if "ata_smart_attributes" in data:
            for attr in data["ata_smart_attributes"].get("table", []):
                raw = attr.get("raw", {}).get("value")
                attr_id = attr.get("id")
                if raw is None or attr_id is None:
                    continue
                if attr_id == 1:
                    self.params["disk.read.error.rate"] = raw
                elif attr_id == 5:
                    self.params["disk.reallocated.sectors.count"] = raw
                elif attr_id == 7:
                    self.params["disk.seek.error.rate"] = raw
                elif attr_id == 9:
                    self.params["disk.power.on.hours"] = raw
                elif attr_id in (190, 194):
                    string_value = attr.get("raw", {}).get("string")
                    raw_value = string_value.split()[0]
                    self.params["disk.temperature"] = raw_value
                elif attr_id == 195:
                    self.params["disk.ecc.error.rate"] = raw
                elif attr_id == 187:
                    self.params["disk.uncorrectable.error.count"] = raw

        elif "nvme_smart_health_information_log" in data:
            nv = data["nvme_smart_health_information_log"]
            self.params["disk.temperature"] = nv.get("temperature")
            self.params["disk.power.on.hours"] = nv.get("power_on_hours")

        else:
            # Temperature
            if isinstance(data.get("temperature"), dict):
                self.params["disk.temperature"] = data["temperature"].get("current")
            # Power-on hours
            if isinstance(data.get("power_on_time"), dict):
                self.params["disk.power.on.hours"] = data["power_on_time"].get("hours")

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
