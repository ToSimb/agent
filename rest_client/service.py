import json
import sys
import time

from storage.sqlite_commands import (select_params,
                                     delete_params)
from config import (MAX_NUMBER_OF_PF,
                    RETENTION_TIME_S)


from logger.logger_rest_client import logger_rest_client

def open_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            content = json.load(file)
            return content
    except FileNotFoundError:
        logger_rest_client.error(f"Нет файла {file_path}")
        return None
    except json.JSONDecodeError:
        logger_rest_client.error(f"Ошибка при декодировании JSON - {file_path}")
        sys.exit(1)
    except Exception as e:
        logger_rest_client.error(f"Ошибка: {e}")
        sys.exit(1)

def save_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logger_rest_client.info(f"Данные успешно сохранены в {file_path}")
    except Exception as e:
        logger_rest_client.info(f"Ошибка при сохранении файла: {e}")
        sys.exit(1)

def collecting_params(CONN):
    while True:
        logger_rest_client.info("--------------------")
        params = select_params(CONN, MAX_NUMBER_OF_PF)
        logger_rest_client.info(f"DB: Получено данных: {len(params)}")
        if len(params) > 0:
            ids_delete_list = verification_data(params)
            if len(ids_delete_list) > 0:
                count_delete = delete_params(CONN, ids_delete_list)
                logger_rest_client.info(f"DB: Удаленно {count_delete} устаревших данных!!!")
                return [], [], count_delete
            else:
                ids_list, value = transform_data(params)
                return ids_list, value, 0
        else:
            return [], [], 0

def verification_data(params):
    ids_delete_list = []
    current_time = time.time()
    for item in params:
        item_dict = json.loads(item[1])
        t = item_dict['t']
        if t < current_time - RETENTION_TIME_S:
            ids_delete_list.append(item[0])
    return ids_delete_list

def transform_data(params):
    ids_list = []
    result = {}
    for item in params:
        item_dict = json.loads(item[1])
        t = item_dict['t']
        ids_list.append(item[0])
        item_id = item_dict['item_id']
        metric_id = item_dict['metric_id']
        v = str(item_dict['v'])
        # v = v.replace(',', '.')
        comment = item_dict.get('comment')
        etmax = item_dict.get('etmax')
        etmin = item_dict.get('etmin')
        key = (item_id, metric_id)
        if key not in result:
            result[(item_id, metric_id)] = {
                'item_id': item_id,
                'metric_id': metric_id,
                'data': []
            }
        data_item = {
            't': t,
            'v': v
        }
        if comment is not None:
            data_item['comment'] = comment
        if etmax is not None:
            data_item['etmax'] = etmax
        if etmin is not None:
            data_item['etmin'] = etmin
        result[key]['data'].append(data_item)
    logger_rest_client.info(f"Собрано {len(ids_list)} метрик")

    output_data = sorted(result.values(), key=lambda x: (x['item_id'], x['metric_id']))

    return ids_list, output_data

def filter_for_mil(file_name_agent_reg_response, result_response):
    agent_reg_response = open_file(file_name_agent_reg_response)

    item_ids = [data['item_id'] for data in agent_reg_response['item_id_list']]

    result = [
        (entry['item_id'], entry['metric_id'], entry['user_query_interval'])
        for entry in result_response['metric_info_list']
        if entry['item_id'] in item_ids
    ]

    return result

def compare_full_paths(scheme_data, agent_reg_response_data):
    scheme_paths = set(item['full_path'] for item in scheme_data['scheme']['item_id_list'])
    registration_paths = set(item['full_path'] for item in agent_reg_response_data['item_id_list'])

    only_in_scheme = scheme_paths - registration_paths
    only_in_registration = registration_paths - scheme_paths

    if only_in_scheme:
        logger_rest_client.debug("Есть в agent_scheme, но нет в registration:")
        for path in sorted(only_in_scheme):
            logger_rest_client.debug(f"  {path}")

    if only_in_registration:
        logger_rest_client.debug("Есть в agent_reg_response, но нет в scheme:")
        for path in sorted(only_in_registration):
            logger_rest_client.debug(f"  {path}")

    return bool(only_in_scheme or only_in_registration)