import locale
import subprocess
import time
import re


def run_smartctl_command(command: list):
    """Запускает smartctl и возвращает вывод или None при ошибке"""
    try:
        encoding = locale.getpreferredencoding()
        return subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding)
    except subprocess.CalledProcessError:
        return None

def extract_last_number(line: str):
    """ Извлекает последнее числовое значение, объединяя части с пробелами """
    line = line.replace('\xa0', '').replace(',', '')
    numbers = re.findall(r'[\d]+(?:\s[\d]+)*', line)
    if numbers:
        return int(numbers[-1].replace(' ', ''))
    return None

def replace_device_names(device_name: str):
    match = re.match(r"/dev/sd([a-z])", device_name)
    if match:
        index = ord(match.group(1)) - ord('a')  # Преобразуем 'a' -> 0, 'b' -> 1 и т.д.
        return index
    return None



class DisksMonitor:
    def __init__(self):
        # Нет пока что смысла использовать, так как если smartctl находит только те диски, которые может опросить!!!
        # result1 = subprocess.run(['lsblk', '-o', 'NAME,TYPE,SIZE'], capture_output=True, text=True)
        # lines = result1.stdout.strip().split('\n')

        result = run_smartctl_command(['smartctl', '--scan']).strip().split("\n")
        print(result)
        if result:
            all_disks = [[line.split()[0], line.split()[2]] for line in result if line.strip()]
            print(all_disks)
            self.disks = {f"{disk[0]}": Disk(disk) for disk in all_disks}

    def get_disks(self):
        return self.disks

    def update(self):
        for disk in self.disks.values():
            disk.update()


class Disk:
    def __init__(self, disk_indo: list):
        self.name = disk_indo[0]
        self.interface_type = disk_indo[1]
        self.params = {
            "disk.head.flying.hours": None,
            "disk.read.bytes.per.sec": None,
            "disk.read.error.retry.rate": None,
            "disk.reallocated.sectors.count": None,
            "disk.seek.error.rate": None,
            "disk.temperature": None,
            "disk.write.bytes.per.sec": None
        }


    def update(self):
        result = {
            "disk.head.flying.hours": None,
            "disk.read.bytes.per.sec": None,
            "disk.read.error.retry.rate": None,
            "disk.reallocated.sectors.count": None,
            "disk.seek.error.rate": None,
            "disk.temperature": None,
            "disk.write.bytes.per.sec": None
        }

        commands = [
            ['smartctl', '-A', '-d', self.name[1], self.name[0]],
            ['smartctl', '-A', self.name[0]]
        ]

        lines = None
        for cmd in commands:
            lines = run_smartctl_command(cmd)
            if lines:
                break
        print(len(lines.splitlines()))
        i = 0
        if lines:
            for line in lines.splitlines():
                print(i)
                i +=1
                if line:
                    print(line)
                    if any(keyword in line for keyword in
                           ["Temperature_Celsius", "Temperature:", "Airflow_Temperature_Cel", "Temperature Sensor"]):
                        key = "disk.temperature"
                    elif any(keyword in line for keyword in ["Power_On_Hours", "Power On Hours:", "Power Cycles"]):
                        key = "disk.head.flying.hours"
                    elif any(keyword in line for keyword in ["Raw_Read_Error_Rate", "Read_Error_Rate", "ECC_Error_Rate"]):
                        key = "disk.read.error.retry.rate"
                    elif "Seek_Error_Rate" in line:
                        key = "disk.seek.error.rate"
                    elif "Reallocated_Sector_Ct" in line:
                        key = "disk.reallocated.sectors.count"
                    else:
                        continue

                    value = extract_last_number(line)
                    if value is not None:
                        result[key] = value

        self.params.update(result)

    def get_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        return self.params.get(metric_id, None)

aaa = DisksMonitor()
