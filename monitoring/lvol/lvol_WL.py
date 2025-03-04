import psutil


def get_lvol_data():
    # Получаем список всех разделов
    partitions = psutil.disk_partitions()
    data = []

    # Проходимся по каждому разделу и получаем информацию о нем
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            current_lvol = dict()
            current_lvol['name'] = partition.device
            current_lvol['mountpoint'] = partition.mountpoint
            current_lvol['total'] = usage.total
            current_lvol['free'] = usage.free
            current_lvol['used'] = usage.used
            data.append(current_lvol)
        except Exception as e:
            print(f"Ошибка получения данных о разделах: {e}")
    return data