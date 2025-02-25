import platform
import subprocess
import locale
import re
import psutil


def run_smartctl_command(command):
    """Запускает smartctl и возвращает вывод или None при ошибке"""
    encoding = locale.getpreferredencoding()
    try:
        return subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding)
    except subprocess.CalledProcessError as e:
        print(f"SMART недоступен для команды: {' '.join(command)}:\n{e}")
    except Exception as e:
        print(f"Ошибка при выполнении команды: {e}")
    return None


def get_disk_list():
    """Получение списка дисков для Windows и Linux"""
    if platform.system() == "Linux":
        try:
            result = subprocess.check_output(["lsblk", "-d", "-n", "-o", "NAME"]).decode().strip().split("\n")
            return [f"/dev/{disk.strip()}" for disk in result if disk.strip()]
        except Exception as e:
            print(f"Ошибка получения списка дисков: {e}")
            return []
    elif platform.system() == "Windows":
        try:
            result = subprocess.check_output(["smartctl", "--scan"]).decode().strip().split("\n")
            disks = []
            for line in result:
                parts = re.split(r'\s+', line, maxsplit=3)
                if len(parts) >= 2:
                    disks.append([parts[0], ' '.join([parts[1], parts[2]])])
            print(disks)
            return disks
        except Exception as e:
            print(f"Ошибка получения списка дисков: {e}")
            return []
    else:
        print(f"ОС не поддерживается")
        return []


def parse_smart_output(output):
    """Парсит SMART-данные из вывода smartctl"""
    data = {}
    if not output:
        return data

    for line in output.split('\n'):
        temp_match = re.search(r'Temperature.*?(\d+)\s*C', line)
        if temp_match:
            data['Температура'] = int(temp_match.group(1))

        power_on_match = re.search(r'Power_On_Hours\s+\S+\s+\S+\s+(\d+)', line)
        if power_on_match:
            data['Общее время работы'] = int(power_on_match.group(1))

    return data


def get_partition_info():
    """Собирает информацию о разделах (точка монтирования, размер, свободное место)"""
    partitions_data = {}

    if platform.system() == "Linux":
        try:
            result = subprocess.check_output(["lsblk", "-P", "-o", "NAME,MOUNTPOINT,SIZE,FSUSED,FSAVAIL"]).decode()
            for line in result.splitlines():
                partition_info = {}
                matches = re.findall(r'(\w+)="([^"]*)"', line)

                name, mount, size, used, avail = None, None, None, None, None
                for key, value in matches:
                    if key == "NAME":
                        name = f"/dev/{value}"
                    elif key == "MOUNTPOINT":
                        mount = value
                    elif key == "SIZE":
                        size = value
                    elif key == "FSUSED":
                        used = value
                    elif key == "FSAVAIL":
                        avail = value

                if name:
                    partitions_data[name] = {
                        "Точка монтирования": mount or "Не смонтирован",
                        "Общий объем": size or "Неизвестно",
                        "Использовано": used or "Неизвестно",
                        "Свободно": avail or "Неизвестно",
                    }

        except Exception as e:
            print(f"Ошибка получения разделов: {e}")

    elif platform.system() == "Windows":
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions_data[part.device] = {
                    "Точка монтирования": part.mountpoint,
                    "Общий объем": f"{usage.total / (1024 ** 3):.2f} GB",
                    "Использовано": f"{usage.used / (1024 ** 3):.2f} GB",
                    "Свободно": f"{usage.free / (1024 ** 3):.2f} GB",
                }
            except PermissionError:
                pass  # Игнорируем недоступные разделы

    return partitions_data


def get_disks_data():
    """Собирает SMART-данные"""
    disks = get_disk_list()
    if not disks:
        print("Диски не найдены.")
        return

    all_data = {}

    for disk in disks:
        disk_name = disk[0]  # Имя диска
        disk_interface = disk[1] if len(disk) > 1 else ""

        command = ["smartctl", "-i"]
        #if disk_interface:
        #    command.append(disk_interface)
        command.append(disk_name)

        result = run_smartctl_command(command)
        if result:
            disk_data = parse_smart_output(result)
            all_data[disk_name] = {"SMART": disk_data}

    # Добавляем информацию о разделах
    partitions = get_partition_info()
    for part, info in partitions.items():
        all_data[part] = info

    # Вывод информации
    for disk, info in all_data.items():
        print(f"\nДиск/Раздел: {disk}")
        for key, value in info.items():
            print(f"  {key}: {value}")

    return all_data


# Запускаем сбор данных
#get_disks_data()
get_disk_list()