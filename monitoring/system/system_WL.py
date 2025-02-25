import platform
import psutil
import os


def get_system_load():
    """Возвращает среднюю загрузку системы"""
    try:
        if platform.system() == "Linux":
            load1, load5, load15 = os.getloadavg()
            return load1
        elif platform.system() == "Windows":
            cpu_percent = psutil.cpu_percent(interval=1)
            return cpu_percent
    except Exception as e:
        print(f"Ошибка сбора параметра \"Средняя загрузка системы\": \n{e}")
        return -1


def get_uptime():
    """Возвращает время непрерывной работы системы"""
    try:
        boot_time = psutil.boot_time()
        current_time = psutil.time.time()
        uptime_seconds = int(current_time - boot_time)
        return uptime_seconds
    except Exception as e:
        print(f"Ошибка сбора параметра \"Время непрерывной работы системы\": \n{e}")
        return -1


print(f"1. Средняя загрузка системы: {get_system_load()}")
print(f"2. Время непрерывной работы системы: {get_uptime()}")