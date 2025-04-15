import json
import time
import os
import math
from functools import reduce

from storage.settings_handler import (get_settings,
                                      get_file_mtime)

from logger.logger_monitoring import logger_monitoring

from config import (DEBUG_MODE)

def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

def open_file(file_name):
    if os.path.isfile(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8-sig') as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            logger_monitoring.error(f"Ошибка при чтении файла {file_name}: {e}")
            return None
    else:
        logger_monitoring.error(f"Файл {file_name} не найден.")
        return None

def save_file_data(file_name, any_objects):
    with open(file_name, 'w', encoding='utf-8-sig') as file:
        # Предполагаем, что any_objects - это список
        json.dump(any_objects, file, ensure_ascii=False, indent=4)
        return True

def crate_items_agent_reg_response():
    agent_reg_response = open_file("agent_reg_response.json")
    items_agent_reg_response = {}

    for item in agent_reg_response.get('item_id_list'):
        items_agent_reg_response[item.get('full_path')] = item.get('item_id')
    return items_agent_reg_response

def create_index_for_any(items_agent_reg_response, file_name, object_monitor):
    file_index = open_file(file_name)

    index_dict = {}
    index_list = []

    for item_key, item_data in file_index.items():
        if item_data in items_agent_reg_response:
            index_dict[item_key] = items_agent_reg_response[item_data]

    object_monitor.create_index(index_dict)
    for line, value in index_dict.items():
        if value is not None:
            index_list.append(value)

    return index_list

def compare_full_paths(scheme_data, agent_reg_response_data):
    scheme_paths = set(item['full_path'] for item in scheme_data['scheme']['item_id_list'])
    registration_paths = set(item['full_path'] for item in agent_reg_response_data['item_id_list'])

    only_in_scheme = scheme_paths - registration_paths
    only_in_registration = registration_paths - scheme_paths

    if only_in_scheme:
        logger_monitoring.debug("Есть в agent_scheme, но нет в registration:")
        for path in sorted(only_in_scheme):
            logger_monitoring.debug(f"  {path}")

    if only_in_registration:
        logger_monitoring.debug("Есть в agent_reg_response, но нет в scheme:")
        for path in sorted(only_in_registration):
            logger_monitoring.debug(f"  {path}")

    return bool(only_in_scheme or only_in_registration)

def build_metric_tuples():
    """
    result = [(item_id, metric_id, query_interval),..], построенный по шаблонам.
    """
    agent_scheme = open_file("agent_scheme.json")
    agent_reg_reg = open_file("agent_reg_response.json")
    if compare_full_paths(agent_scheme, agent_reg_reg):
        return False
    result = []

    # 1. Собираем словарь: metric_id - значение query_interval
    metric_intervals = {
        metric["metric_id"]: metric["query_interval"]
        for metric in agent_scheme["scheme"].get("metrics", [])
    }

    # 2. Собираем словарь: template_id - список metric_id
    template_metrics = {
        template["template_id"]: template.get("metrics", [])
        for template in agent_scheme["scheme"].get("templates", [])
    }

    # 3. Обработка item_id_list из ответа сервера
    for item in agent_reg_reg.get("item_id_list", []):
        item_id = item.get("item_id")
        full_path = item.get("full_path")

        # Получаем последний шаблон из full_path, например: cpu_v1[0] -> cpu_v1
        template_with_index = full_path.split("/")[-1]
        template_id = template_with_index.split("[")[0]

        # Получаем метрики, связанные с шаблоном
        metrics = template_metrics.get(template_id, None)
        if metrics is None:
            logger_monitoring.error(f"Не найден шаблон {template_id}")
            return False
        for metric_id in metrics:
            query_interval = metric_intervals.get(metric_id)
            if query_interval is not None:
                result.append((item_id, metric_id, query_interval))
            else:
                logger_monitoring.error(f"Не найден interval для метрики {metric_id}")
                return False
    save_file_data("storage/metric_interval_list.json", result)
    return True

def get_metrics_polling_plan():
    """
    value_dict (dict[int, list[tuple[str, str]]]):
        Словарь, где ключ — интервал,
        значение — список пар (item_id, metric_id)
    item_all_interval (dict[str, set[int]]):
        Словарь, где ключ — item_id,
        значение — множество интервалов, с которыми он должен опрашиваться.
    """
    mil = open_file('storage/metric_interval_list.json')
    mil_227 = open_file('storage/metric_info_227.json')

    if mil is None:
        return None, None
    if mil_227 is not None:
        mil = merge_metric_intervals(mil, mil_227)

    value_dict = {}
    item_all_interval = {}
    for line in mil:
        if line[2] not in value_dict:
            value_dict[line[2]] = []
        value_dict[line[2]].append((line[0], line[1]))
        if line[0] not in item_all_interval:
            item_all_interval[line[0]] = set()
        item_all_interval[line[0]].add(line[2])

    return value_dict, item_all_interval

def update_metrics_polling():
    mil = open_file('storage/metric_interval_list.json')
    mil_227 = open_file('storage/metric_info_227.json')

    if mil_227 is not None:
        mil = merge_metric_intervals(mil, mil_227)

    value_dict = {}
    for line in mil:
        if line[2] not in value_dict:
            value_dict[line[2]] = []
        value_dict[line[2]].append((line[0], line[1]))

    return value_dict

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

def wait_for_start_signal():
    while True:
        _,_,status_rest_client = get_settings()
        if status_rest_client:
            break
        logger_monitoring.error("REST CLIENT не запущен")
        time.sleep(60)

def get_launch_timestamp():
    last_modified_time = get_file_mtime()
    if last_modified_time is None:
        logger_monitoring.error("Не удалось получить время изменения файла.")
        return -1, -1

    _, user_query_interval_revision, rest_client_start = get_settings()
    if not DEBUG_MODE:
        if rest_client_start is not True:
            logger_monitoring.error("Не удалось получить время изменения файла.")
            return -1, -1

    return last_modified_time, user_query_interval_revision