import locale
import subprocess
import time
import re

def measure_time(func, *args, **kwargs):
    """Функция для измерения времени выполнения другой функции."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

def replace_device_names(device_name):
    match = re.match(r"/dev/sd([a-z])", device_name)
    if match:
        index = ord(match.group(1)) - ord('a')  # Преобразуем 'a' -> 0, 'b' -> 1 и т.д.
        return index
    return None


def get_physical_disk_io_speed():
    cmd = 'wmic path Win32_PerfFormattedData_PerfDisk_PhysicalDisk get Name,DiskReadBytesPersec,DiskWriteBytesPersec'

    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        print(result)
        lines = result.strip().split("\n")
        # print(lines)
        disk_speeds = {}

        for line in lines[1:]:  # Пропускаем заголовок
            data = line.split()
            if len(data) >= 3:
                disk_name, read_speed, write_speed = data[2], data[0], data[1]

                # Пропускаем строку "_Total"
                if disk_name == "_Total":
                    continue

                # Проверяем, являются ли значения числами перед преобразованием
                if read_speed.isdigit() and write_speed.isdigit():
                    disk_speeds[disk_name] = {"read": int(read_speed), "write": int(write_speed)}

        return disk_speeds

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return {}


def get_disk_list():
    """Получение списка дисков"""
    try:
        result = run_smartctl_command(['smartctl', '--scan']).strip().split("\n")
        disks = [[line.split()[0], line.split()[1], line.split()[2]] for line in result if line.strip()]
        return disks
    except Exception as e:
        return []


def run_smartctl_command(command):
    """Запускает smartctl и возвращает вывод или None при ошибке"""
    try:
        encoding = locale.getpreferredencoding()
        return subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding)
    except subprocess.CalledProcessError:
        return None


def parse_disk(disk):
    current_disk_data = {
        "Temperature": -1,
        "Power_On_Hours": -1,
        "Read_Error_Rate": -1,
        "Seek_Error_Rate": -1,
        "Reallocated_Sector_Ct": -1
    }
    result = run_smartctl_command(['smartctl', '-A', disk[1], disk[2], disk[0]])
    if result:
        for line in result.splitlines():
            if "Temperature_Celsius" in line:
                current_disk_data["Temperature"] = int(line.split()[-1])
            elif "Temperature:" in line:
                current_disk_data["Temperature"] = int(line.split()[-2])
            elif "Power_On_Hours" in line or "Power On Hours:" in line:
                current_disk_data["Power_On_Hours"] = int(line.split()[-1])
            elif "Raw_Read_Error_Rate" in line or "Read_Error_Rate" in line:
                current_disk_data["Read_Error_Rate"] = int(line.split()[-1])
            elif "Seek_Error_Rate" in line:
                current_disk_data["Seek_Error_Rate"] = int(line.split()[-1])
            elif "Reallocated_Sector_Ct" in line:
                current_disk_data["Reallocated_Sector_Ct"] = int(line.split()[-1])
    return current_disk_data


# Запись в файл вместо вывода в консоль
with open("disks.txt", "w", encoding="utf-8") as file:
    disks, time_disks = measure_time(get_disk_list)
    if not disks:
        file.write("Диски не найдены.\n")
        exit(0)

    file.write(f"Количество дисков: {len(disks)}\n")
    file.write(f"Время получения списка дисков: {time_disks:.4f} секунд\n\n")

    disk_speeds, time_disk_speeds = measure_time(get_physical_disk_io_speed)
    file.write(f"Время получения скорости дисков: {time_disk_speeds:.4f} секунд\n\n")
    file.write("-" * 25 + "\n")

    try:
        for disk in disks:
            file.write(f"Диск: {disk[0]}\n")
            current_disk_data, time_current_disk_data = measure_time(parse_disk, disk)
            id_disk = replace_device_names(disk[0])
            file.write(f"  Температура: {current_disk_data['Temperature']} °C\n")
            file.write(f"  Общее время работы: {current_disk_data['Power_On_Hours']} часов\n")
            file.write(f"  Частота ошибок чтения: {current_disk_data['Read_Error_Rate']}\n")
            file.write(f"  Частота ошибок позиционирования: {current_disk_data['Seek_Error_Rate']}\n")
            file.write(f"  Количество переназначенных секторов: {current_disk_data['Reallocated_Sector_Ct']}\n")
            file.write(f" + Время получения данных: {time_current_disk_data:.4f} секунд\n")
            if id_disk is not None:
                print(disk_speeds)
                speeds_disk = disk_speeds[str(id_disk)]
                file.write(f"  Скорость чтения: {speeds_disk['read']} байт/сек\n")
                file.write(f"  Скорость записи: {speeds_disk['write']} байт/сек\n")
            file.write("-" * 25 + "\n")
    except Exception as e:
        file.write(f"Ошибка обработки вывода smartctl -A: {e}\n")
