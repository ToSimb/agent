import locale
import platform
import subprocess
import shutil
import json
import time


class DisksMonitor:
    def __init__(self):
        self.disks = {}
        self.system = platform.system()
        self.iostat_available = shutil.which("iostat") is not None
        self.wmic_available = shutil.which("wmic") is not None

        try:
            # Нет пока что смысла использовать, так как если smartctl находит только те диски, которые может опросить!!!
            # result1 = subprocess.run(['lsblk', '-o', 'NAME,TYPE,SIZE'], capture_output=True, text=True)
            # lines = result1.stdout.strip().split('\n')

            command = ['smartctl', '--scan']
            encoding = locale.getpreferredencoding()
            result = subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding).strip().split("\n")
            if result:
                all_disks = [[line.split()[0], line.split()[2]] for line in result if line.strip()]
                self.disks = {f"{disk[0]}": Disk(disk) for disk in all_disks}
            print("от smartctl")
            for i in self.disks.keys():
                print(i)
        except:
            print(f"Ошибка выполнения команды {command}")

    def update(self):
        disks_speed = self.__get_disks_rw_speed()
        print("от iostat")
        for i in disks_speed.keys():
            print(i)

        for disk_key in self.disks.keys():
            print("Обновление ",disk_key)
            self.disks[disk_key].update(disks_speed[disk_key])

    def get_all(self):
        for disk in self.disks:
            print(f"Параметры {disk}:")
            aaa = self.disks[disk].get_params_all()
            print(aaa)

    @staticmethod
    def __replace_device_name(index):
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

    def __get_linux_disk_speed(self):
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


class Disk:
    def __init__(self, disk_indo: list):
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
        result = {}
        result["disk.write.bytes.per.sec"] = disks_speed["write"]
        result["disk.read.bytes.per.sec"] = disks_speed["read"]

        if self.system == "Windows":
            command = ['smartctl', '-A', '-j', '-d', self.interface_type, self.name]
        else:
            command = ['smartctl', '-A', '-j', self.name]

        try:
            output = subprocess.check_output(command, text=True)
            if not output:
                return
            data = json.loads(output)
            # with open(f"{self.name[-3:]}.json", "w") as f:
            #     json.dump(data, f, indent=4, ensure_ascii=False)
            #     print(f"{self.name[-3:]}.json")
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
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None

a = DisksMonitor()
a.update()
print("- -"*30)
a.get_all()