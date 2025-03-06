import psutil
import time
from concurrent.futures import ThreadPoolExecutor

def get_usage(partition):
    """Получаем данные о разделе"""
    try:
        usage = psutil.disk_usage(partition.mountpoint)
        return {
            'name': partition.device,
            'mountpoint': partition.mountpoint,
            'total': usage.total or -1,
            'free': usage.free or -1,
            'used': usage.used or -1
        }
    except Exception as e:
        print(f"Ошибка получения данных о разделе {partition.device}: {e}")
        return None

def get_lvol_data():
    """Получаем информацию о всех разделах с оптимизацией"""
    start_time = time.time()
    partitions = psutil.disk_partitions()
    data = []

    # Используем ThreadPoolExecutor для параллельной обработки данных о разделах
    with ThreadPoolExecutor() as executor:
        results = executor.map(get_usage, partitions)

        data = [result for result in results if result is not None]
    print("Время сбора параметров LVOL:", time.time() - start_time)
    return data, time.time() - start_time