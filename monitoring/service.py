import json
import time
import os
import math
from functools import reduce

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
        index_list = []
        file_index = json.load(cpu_file)
        object_monitor.create_index(file_index)
        for line, value in file_index.items():
            index_list.append(value)
        return index_list

def get_metrics_polling_plan():
    """
    value_dict (dict[int, list[tuple[str, str]]]):
        Словарь, где ключ — интервал,
        значение — список пар (item_id, metric_id)
    item_all_interval (dict[str, set[int]]):
        Словарь, где ключ — item_id,
        значение — множество интервалов, с которыми он должен опрашиваться.
    """
    mil = open_file('metric_interval.json')

    mil_227 = open_file('metric_info_227.json')
    if mil_227 is not None:
        mil = merge_metric_intervals(mil, mil_227)

    value_dict = {}
    item_all_interval = {}
    for line in mil:
        if line[2] not in value_dict:
            value_dict[line[2]] = []
        # Добавляем пару (внешний ключ, внутренний ключ) в список
        value_dict[line[2]].append((line[0], line[1]))
        if line[0] not in item_all_interval:
            item_all_interval[line[0]] = set()
        item_all_interval[line[0]].add(line[2])

    return value_dict, item_all_interval

def merge_metric_intervals(mil: list, mil_227: list) -> list:

    mil_227_map = {
        (item_id, metric_id): interval
        for item_id, metric_id, interval in mil_227
    }

    result = []
    for item_id, metric_id, interval in mil:
        key = (item_id, metric_id)
        new_interval = mil_227_map.get(key, interval)
        result.append([item_id, metric_id, new_interval])

    return result

def calculate_gcd_for_group(item_ids, interval_map):
    intervals = set()

    for item_id in item_ids:
        item_intervals = interval_map.get(item_id, set())
        intervals.update(i for i in item_intervals if i != 0)
    if not intervals:
        return None
    return reduce(math.gcd, intervals)