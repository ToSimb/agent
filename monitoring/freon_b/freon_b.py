import requests
import json
import os
from monitoring.base import BaseObject, SubObject

from logger.logger_mon_fb import logger_monitoring
from config import (URL_FB, DEBUG_MODE)

if DEBUG_MODE:
    URL_FB = f"http://127.0.0.1:8080/freon/25_2"

COUNT_BOARDS = 6
COUNT_SENSOR_T = 13
COUNT_SENSOR_U = 14
COUNT_SENSOR_I = 14

HASH_STATE = {
    "started": "OK",
    "disconnected": "FATAL",
    "idle": "OK",
    "sleep": "ERROR"
}

class FreonB(BaseObject):
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            vus (dict): Словарь, где ключ - ip-address узла + дополнение в зависимости от объекта,
                            а значением - объект класса Vu_fb(Board_fb, Unit_T,...), представляющий ядро процессора.
                            Пример: {'192.168.0.1': <__main__.Vu_fb object at 0x723c888ad190>, ..

                                    '192.168.0.1:board:0': <__main__.Board_fb object at 0x76008a5eb760>, ..

                                    192.168.0.60:board:4:T:0 <__main__.Unit_T object at 0x794412cf1040>}
            vus_info (dict): Словарь, где ключ  - ip-address узла  + дополнение в зависимости от объекта,
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'192.168.0.60': 'fb:60', ..

                                        '192.168.0.60:board:0': 'fb:60:board:0', ..

                                        192.168.0.60:board:5:T:0': 'fb:60:board:5:T:0', ...

                                        '192.168.0.60:connection': 'fb:60:connection'}
            item_index: Словарь, где ключ - это будущий item_id из схемы,
                        а значением - объект класса Vu_fb(Board_fb, Unit_T,...).
                        (по факту мы делаем новые ссылки на объекты)
                            Пример: {'1111': <__main__.Vu_fb object at 0x71621921d580, ..

                                     '1112': <__main__.Board_fb object at 0x7162191bb5b0>, ..

                                     '1121': <__main__.Unit_T object at 0x7162191d5640>, .. }
        """
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = script_dir + "/freon_dict.txt"
        self.vus = {}
        self.vus_info = {}
        self.item_index = {}
        self.conn = "FATAL"
        self.connection = []
        fb = self.__send_req()
        if fb is not None:
            self.conn = "OK"
        else:
            logger_monitoring.error("нет соединения с Ф-Б при init")
        file_dict = self.__open_dict(file_name)

        if file_dict is not None:
            for i in file_dict.keys():
                self.vus[i] = Vu_fb(i)
                boards = self.vus[i].get_all_obj()
                for index in range(len(boards)):
                    self.vus[f"{i}:board:{index}"] = boards[index]
                    units_T, units_U, units_I = boards[index].get_all_obj()
                    for index_T in range(COUNT_SENSOR_T):
                        self.vus[f"{i}:board:{index}:T:{index_T}"] = units_T[index_T]
                    for index_U in range(COUNT_SENSOR_U):
                        self.vus[f"{i}:board:{index}:U:{index_U}"] = units_U[index_U]
                    for index_I in range(COUNT_SENSOR_I):
                        self.vus[f"{i}:board:{index}:I:{index_I}"] = units_I[index_I]
            for index_vu in file_dict.keys():
                if index_vu in self.vus:
                    # path_id = f"fb:{int(file_dict[index_vu]['x'])-1}:{int(file_dict[index_vu]['y'])-1}"
                    index_vu_int = (int(file_dict[index_vu]['y'])-1) + (int(file_dict[index_vu]['x'])-1)*20
                    path_id = f"fb:{index_vu_int}"
                    self.vus_info[index_vu] = path_id
                    self.vus_info[f'connection:{index_vu_int}'] = f'{path_id}:connection'
                    for index in range(COUNT_BOARDS):
                        self.vus_info[f"{index_vu}:board:{index}"] = f"{path_id}:board:{index}"
                        for index_T in range(COUNT_SENSOR_T):
                            self.vus_info[f"{index_vu}:board:{index}:T:{index_T}"] = f"{path_id}:board:{index}:T:{index_T}"
                        for index_U in range(COUNT_SENSOR_U):
                            self.vus_info[f"{index_vu}:board:{index}:U:{index_U}"] = f"{path_id}:board:{index}:U:{index_U}"
                        for index_I in range(COUNT_SENSOR_I):
                            self.vus_info[f"{index_vu}:board:{index}:I:{index_I}"] = f"{path_id}:board:{index}:I:{index_I}"

                else:
                    logger_monitoring.debug(f"ERROR: нет {index_vu} в списке объектов!")

        else:
            logger_monitoring.error("файл пустой")

        if (len(self.vus) + 1) == len(self.vus_info):
            logger_monitoring.info("ВСЕ ОБЪЕКТЫ СОЗДАНЫ")
        logger_monitoring.info(f"Количество узлов {len(self.vus)}")

    @staticmethod
    def __open_dict(file_name):
        try:
            with open(file_name, "r", encoding='utf-8-sig') as f:
                file_dict = json.load(f)
                return file_dict
        except Exception as e:
            logger_monitoring.error(f"Ошибка при прочтении файла конфигурации для ФБ - {e}")
            return None

    @staticmethod
    def __send_req():
        try:
            response = requests.get(URL_FB, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger_monitoring.error(f"Ошибка при обращении к API: {e}")
            return None

    def get_objects_description(self):
        return self.vus_info

    def create_index(self, fb_dict):
        """
        Пример fb_dict:
            {
                'fb:3:20': 1212,
                'fb:3:20:board:0': 1213, ...
                'fb:3:20:board:5:T:0': 1222, ..
                'fb:connection': 1200
            }
        """
        for index in fb_dict:
            if fb_dict[index] is not None:
                if "connection" in index:
                    self.connection.append(str(fb_dict[index]))
                else:
                    for key, value in self.vus_info.items():
                        if value == index:
                            self.item_index[str(fb_dict[index])] = self.vus.get(key, None)
                            break
                    else:
                        logger_monitoring.error(f'Для индекса {index} нет значения')

    def update(self):
        try:
            fb = self.__send_req()
            if fb is not None:
                self.conn = "OK"
                for i in fb["rows"]:
                    if i["name"]:
                        self.vus[i["name"]].update(i)
            else:
                self.conn = "FATAL"
        except Exception as e:
            self.conn = "FATAL"
            logger_monitoring.error(f"Ошибка при update у FreonB - {e}")

    def get_all(self):
        """
            Возвращает все параметры, кроме connection
        """
        return_list = []
        for vu in self.vus.keys():
            result = self.vus[vu].get_params_all()
            return_list.append({vu: result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            if item_id in self.connection:
                if metric_id == "connection.state":
                    return self.validate_state(self.conn)
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            logger_monitoring.error(f"Ошибка при вызове item_id - {item_id}: {metric_id} - {e}")
            return None


class Vu_fb(SubObject):
    def __init__(self, ip_address: str):
        super().__init__()
        self.params = {
            "asic.name": ip_address,
            "asic.taskId": None,
            "asic.state": None,
        }
        self.boards = {}
        for board_index in range(COUNT_BOARDS):
            self.boards[board_index] = Board_fb()

    def get_all_obj(self):
        return self.boards

    def update(self, line):
        try:
            self.params["asic.taskId"] = line["taskId"]
            self.params["asic.state"] = line["state"]
            state_disconnect = False
            if self.params["asic.state"] == "disconnected":
                state_disconnect = True
            for board_index in range(COUNT_BOARDS):
                self.boards[board_index].update(line["stat"]["units"][board_index], state_disconnect)
        except Exception as e:
            logger_monitoring.error(f"Ошибка при update у Vu_fb - {e}")

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result_params = self.params[metric_id]
                result = None
                if result_params is not None:
                    self.params[metric_id] = None
                    if metric_id in ["asic.name"]:
                        result = self.validate_string(result_params)
                    elif metric_id in ["asic.taskId"]:
                        result = self.validate_integer(result_params)
                    elif metric_id in ["asic.P"]:
                        result = self.validate_double(result_params)
                    elif metric_id in ["asic.state"]:
                        result = self.validate_state(HASH_STATE.get(result_params, None))
                    else:
                        logger_monitoring.error(f"такого быть не должно, но что то тут не явно {metric_id}")
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Board_fb(SubObject):
    def __init__(self):
        super().__init__()
        self.units_T = {}
        self.units_U = {}
        self.units_I = {}
        self.params = {
            "asic.state": None,
            "asic.P": None,
            "asic.maxT": None
        }
        for index in range(COUNT_SENSOR_T):
            self.units_T[index] = Unit_T()
        for index in range(COUNT_SENSOR_U):
            self.units_U[index] = Unit_U()
        for index in range(COUNT_SENSOR_I):
            self.units_I[index] = Unit_I()

    def get_all_obj(self):
        return self.units_T, self.units_U, self.units_I

    def update(self, line: dict, state_disconnect):
        try:
            line_data, units_T_data, units_U_data, units_I_data = self.__parse_response_data_FB(line, state_disconnect)
            self.params.update(line_data)
            if units_T_data:
                for index in range(COUNT_SENSOR_T):
                    self.units_T[index].update(units_T_data[index])
            if units_U_data:
                for index in range(COUNT_SENSOR_U):
                    self.units_U[index].update(units_U_data[index])
            if units_I_data:
                for index in range(COUNT_SENSOR_I):
                    self.units_I[index].update(units_I_data[index])
        except Exception as e:
            logger_monitoring.error(f"Ошибка при update у Board_fb - {e}")


    @staticmethod
    def __parse_response_data_FB(line: dict, state_disconnect):
        i_unit_state = line.get("state")
        if state_disconnect:
            i_unit_state = "disconnected"
        line_data = {
            "asic.state": i_unit_state,
            "asic.P": line.get("P"),
            "asic.maxT": line.get("maxT"),
        }
        return line_data, line.get("T"), line.get("U"), line.get("I")

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result_params = self.params[metric_id]
                result = None
                if result_params is not None:
                    self.params[metric_id] = None
                    if metric_id in ["asic.maxT", "asic.P"]:
                        result = self.validate_double(result_params)
                    elif metric_id in ["asic.state"]:
                        result = self.validate_state(HASH_STATE.get(result_params, None))
                    else:
                        logger_monitoring.error(f"такого быть не должно, но что то тут не явно {metric_id}")
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Unit_T(SubObject):
    def __init__(self):
        super().__init__()
        self.params = {
            "asic.T": None,
        }

    def update(self, params):
        self.params["asic.T"] = params

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    result = self.validate_double(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Unit_U(SubObject):
    def __init__(self):
        super().__init__()
        self.params = {
            "asic.U": None,
        }

    def update(self, params):
        self.params["asic.U"] = params

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    result = self.validate_double(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Unit_I(SubObject):
    def __init__(self):
        super().__init__()
        self.params = {
            "asic.I": None,
        }

    def update(self, params):
        self.params["asic.I"] = params

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    result = self.validate_double(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None
