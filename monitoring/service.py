import json
import time
import os

def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

def open_file(file_name):
    if os.path.isfile(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Ошибка при чтении файла {file_name}: {e}")
            return None
    else:
        print(f"Файл {file_name} не найден.")
        return None

def save_file(file_name, any_objects):
    if not os.path.isfile(file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file_return = {}
            for index_cpu in any_objects:
                file_return[any_objects[index_cpu]] = None
            json.dump(file_return, file, ensure_ascii=False, indent=4)
            return True
    return False

def save_file_data(file_name, any_objects):
    with open(file_name, 'w', encoding='utf-8') as file:
        # Предполагаем, что any_objects - это список
        json.dump(any_objects, file, ensure_ascii=False, indent=4)
        return True

def create_index_for_any(file_name, object_monitor):
    with open(file_name, 'r') as cpu_file:
        file_index = json.load(cpu_file)
        object_monitor.create_index(file_index)

def get_metrics_test():
    # считываем с файла!
    prototype_list = {
        '12': {
            'core.user.time111111': 1,
            'core.system.time': 2,
            'core.irq.time': 3,
            'core.softirq.time': 1,
            'core.idle.time': 1,
            'core.iowait': 2,
            'core.load': 3
        },
        '13': {
            'core.user.time': 1,
            'core.system.time': 2,
            'core.irq.time': 3,
            'core.softirq.time': 1,
            'core.idle.time': 1,
            'core.iowait': 2,
            'core.load': 3
        },
        '16': {
            'core.user.time': 1,
            'core.system.time': 2
        },
    }
    value_dict = {}
    for item_id, metrics in prototype_list.items():
        for metric_id, time_value in metrics.items():
            if time_value not in value_dict:
                value_dict[time_value] = []
            # Добавляем пару (внешний ключ, внутренний ключ) в список
            value_dict[time_value].append((item_id, metric_id))
    return value_dict