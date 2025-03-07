import psutil
import time

def measure_time(func, *args, **kwargs):
    """Функция для измерения времени выполнения другой функции."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start


def get_usage(partition):
    """Получаем данные о разделе"""
    try:
        start_time = time.time()  # Начало измерения времени
        usage = psutil.disk_usage(partition.mountpoint)
        end_time = time.time()  # Конец измерения времени

        # Возвращаем информацию о разделе вместе с временем получения данных
        return {
            'name': partition.device,
            'mountpoint': partition.mountpoint,
            'total': usage.total or -1,
            'free': usage.free or -1,
            'used': usage.used or -1,
            'time_to_get_info': end_time - start_time  # Время получения информации
        }
    except Exception as e:
        print(f"Ошибка получения данных о разделе {partition.device}: {e}")
        return None


# Открываем файл для записи
with open("lvol1.txt", "w", encoding="utf-8") as f:
    partitions, time_partitions = measure_time(psutil.disk_partitions)

    ## В ЛИНУКСЕ добавил проверка на loop
    for i in partitions:
        print(i)
    filtered_partitions = [p for p in partitions if 'loop' not in p.device]

    # Запись количества объектов (разделов диска)
    f.write(f"Количество ВСЕХ объектов (разделов диска): {len(partitions)}\n")
    f.write(f"Количество объектов (разделов диска): {len(filtered_partitions)}\n")
    # Для каждого раздела получаем его информацию и записываем в файл
    for partition in filtered_partitions:
        usage_info = get_usage(partition)
        if usage_info:
            f.write(f"Информация о разделе {usage_info['name']}:\n")
            f.write(f"  Точка монтирования: {usage_info['mountpoint']}\n")
            f.write(f"  Общий размер: {usage_info['total']} байт\n")
            f.write(f"  Свободное место: {usage_info['free']} байт\n")
            f.write(f"  Использованное место: {usage_info['used']} байт\n")
            f.write(f"  Время получения информации: {usage_info['time_to_get_info']:.4f} секунд\n")
            f.write("-" * 40 + "\n")

    # Запись времени выполнения всей программы
    f.write(f"Общее время выполнения: {time_partitions:.4f} секунд\n")

