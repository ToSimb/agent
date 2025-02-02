import platform
import psutil
import os

# Поменять на try

def get_system_load():
    """Возвращает среднюю загрузку системы"""
    if platform.system() == "Linux":
        load1, load5, load15 = os.getloadavg()
        return load1 or -1
    elif platform.system() == "Windows":
        cpu_percent = psutil.cpu_percent(interval=1)
        return cpu_percent or -1


def get_uptime():
    """Возвращает время непрерывной работы системы"""
    boot_time = psutil.boot_time()
    current_time = psutil.time.time()
    uptime_seconds = int(current_time - boot_time)
    return uptime_seconds or -1


print(f"1. Средняя загрузка системы: {get_system_load()}")
print(f"2. Время непрерывной работы системы: {get_uptime()}")