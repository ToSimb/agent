from disk_WL import get_disk_data
import psutil
import time
import re


def replace_device_names(device_name):
    match = re.match(r"/dev/sd([a-z])", device_name)
    if match:
        index = ord(match.group(1)) - ord('a')  # Преобразуем 'a' -> 0, 'b' -> 1 и т.д.
        return f"PhysicalDrive{index}"
    return device_name  # Если не соответствует формату, возвращаем как есть


def get_disk_speed():
    # Получаем начальные данные для каждого диска
    disk_io_start = psutil.disk_io_counters(perdisk=True)
    time.sleep(0.1)
    disk_io_end = psutil.disk_io_counters(perdisk=True)
    data = {}

    # Рассчитываем скорость чтения/записи по каждому диску
    for disk, io_start in disk_io_start.items():
        io_end = disk_io_end[disk]
        read_speed = (io_end.read_bytes - io_start.read_bytes)
        write_speed = (io_end.write_bytes - io_start.write_bytes)
        data[disk] = {"read_speed": read_speed, "write_speed": write_speed}
    return data


def all_disk():
    start_time = time.time()
    disk_info = get_disk_data()
    disk_info = {replace_device_names(k): v for k, v in disk_info.items()}
    disk_speed = get_disk_speed()
    dict_disk = {}

    for key in set(disk_info.keys()).union(disk_speed.keys()):
        dict_disk[key] = {**disk_info.get(key, {}), **disk_speed.get(key, {})}

    list_disk = [{"name": key, **value} for key, value in dict_disk.items()]
    print("Время сбора параметров DISK:", time.time() - start_time)
    return list_disk

if __name__ == "__main__":
    print(all_disk())