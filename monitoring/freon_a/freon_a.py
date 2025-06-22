import json
import requests
import os
from monitoring.base import BaseObject, SubObject

from logger.logger_mon_fa import logger_monitoring
from config import (URL_FA, DEBUG_MODE)

if DEBUG_MODE:
    URL_FA = f"http://127.0.0.1:8080/freon/22"


HASH_STATE = {
    "started": "OK",
    "disconnected": "FATAL",
    "idle": "OK",
    "sleep": "ERROR"
}

class FreonA(BaseObject):
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            vus (dict): Словарь, где ключ - ip-address платы ++ может быть дополнение,
                            а значением - объект класса Board_f_a(Unit_T,...).
                            Пример: {'192.168.86.194': <__main__.Board_f_a object at 0x79c9c8b41100>,
                                    '192.168.86.188': <__main__.Board_f_a object at 0x79c9c8b18700>, ...,

                                    '192.168.87.24:T:0': <__main__.Unit_T object at 0x76c321ebb220>}
            vus_info (dict): Словарь, где ключ  - ip-address платы  ++ может быть дополнение,
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'192.168.85.137': 'fa:1:1',
                                        '192.168.85.28': 'fa:1:2', ... ,

                                        192.168.87.24:T:0': 'fa:1:2:T:0', ...

                                        'connection': 'fa:connection'}
            item_index: Словарь, где ключ - это будущий item_id из схемы,
                        а значением - объект класса Board_f_a(Unit_T,...).
                        (по факту мы делаем новые ссылки на объекты)
                            Пример: {'1111': <__main__.Board_f_a object at 0x79c9c8b41100>,
                                     '1112': <__main__.Board_f_a object at 0x79c9c8b18700>, .. }
        """
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = script_dir + "/freon_dict.txt"
        self.vus = {}
        self.vus_info = {}
        self.conn = "FATAL"
        self.connection = []
        self.item_index = {}
        fa = self.__send_req()
        if fa is not None:
            self.conn = "OK"
        else:
            logger_monitoring.error("нет соединения с Ф-А при init")

        file_dict = self.__open_dict(file_name)
        if file_dict is not None:
            for i in file_dict.keys():
                self.vus[i] = Board_fa(i)
                units_T, units_U, units_I = self.vus[i].get_all_obj()
                for index_T in units_T.keys():
                    self.vus[f"{i}:T:{index_T}"] = units_T[index_T]
                for index_U in units_U.keys():
                    self.vus[f"{i}:U:{index_U}"] = units_U[index_U]
                for index_I in units_I.keys():
                    self.vus[f"{i}:I:{index_I}"] = units_I[index_I]
            for index_vu in file_dict.keys():
                if index_vu in self.vus:
                    path = f"fa:{file_dict[index_vu]['x']-1}:{self.__get_address_full_board(int(file_dict[index_vu]['y']))}"
                    self.vus_info[f"connection:{file_dict[index_vu]['x']-1}"] = f"fa:{file_dict[index_vu]['x']-1}:connection"
                    self.vus_info[index_vu] = path
                    for index in range(6):
                        self.vus_info[f"{[index_vu][0]}:T:{index}"] = f"{path}:T:{index}"
                    for index in range(6):
                        self.vus_info[f"{[index_vu][0]}:U:{index}"] = f"{path}:U:{index}"
                    for index in range(6):
                        self.vus_info[f"{[index_vu][0]}:I:{index}"] = f"{path}:I:{index}"
                else:
                    logger_monitoring.error(f"ERROR: нет {index_vu} в списке объектов!")
        else:
            logger_monitoring.error("файл пустой")
        if (len(self.vus)+1) == len(self.vus_info):
            logger_monitoring.info("ВСЕ ОБЪЕКТЫ СОЗДАНЫ")

    @staticmethod
    def __get_address_full_board(index):
        replacement_str_map = {
            1: '0:0',
            3: '0:1',
            2: '1:0',
            4: '1:1',
            5: '2:0',
            7: '2:1',
            6: '3:0',
            8: '3:1',
            9: '4:0',
            11: '4:1',
            10: '5:0',
            12: '5:1',
            13: '6:0',
            15: '6:1',
            14: '7:0',
            16: '7:1',
        }
        return replacement_str_map.get(index)

    @staticmethod
    def __open_dict(file_name):
        try:
            with open(file_name, "r", encoding='utf-8-sig') as f:
                file_dict = json.load(f)
                return file_dict
        except Exception as e:
            logger_monitoring.error(f"Ошибка при прочтении файла конфигурации для ФА - {e}")
            return None

    @staticmethod
    def __send_req():
        try:
            response = requests.get(URL_FA, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger_monitoring.error(f"Ошибка при обращении к API: {e}")
            return None

    def get_objects_description(self):
        return self.vus_info

    def create_index(self, fa_dict):
        """
        Пример fa_dict:
            {
                'fa:31:1': 1212,
                'fa:31:2': 1213, ...
                'fa:38:16:I:2': 1222, ..
                'fa:connection': 1200
            }
        """
        for index in fa_dict:
            if fa_dict[index] is not None:
                if "connection" in index:
                    self.connection.append(str(fa_dict[index]))
                else:
                    for key, value in self.vus_info.items():
                        if value == index:
                            self.item_index[str(fa_dict[index])] = self.vus.get(key, None)
                            break
                    else:
                        logger_monitoring.debug(f'Для индекса {index} нет значения')
        logger_monitoring.info("Индексы для Ф-А обновлены")

    def update(self):
        fa = self.__send_req()
        if fa is not None:
            self.conn = "OK"
            for i in fa["rows"]:
                if i["name"]:
                    self.vus[i["name"]].update(i)
        else:
            self.conn = "FATAL"

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


class Board_fa(SubObject):
    def __init__(self, ip_address: str):
        super().__init__()
        self.units_T = {}
        self.units_U = {}
        self.units_I = {}
        self.params = {
            "asic.name": ip_address,
            "asic.taskId": None,
            "asic.state": None,
            "asic.P": None,
        }
        for index in range(6):
            self.units_T[index] = Unit_T()
            self.units_U[index] = Unit_U()
            self.units_I[index] = Unit_I()

    def get_all_obj(self):
        return self.units_T, self.units_U, self.units_I

    def update(self, line: dict):
        params, units_T_data, units_U_data, units_I_data = self.__parse_response_data_FA(line)
        if units_T_data:
            for index in range(len(units_T_data)):
                self.units_T[index].update(units_T_data[index])
        if units_U_data:
            for index in range(len(units_U_data)):
                self.units_U[index].update(units_U_data[index])
        if units_I_data:
            for index in range(len(units_I_data)):
                self.units_I[index].update(units_I_data[index])
        self.params.update(params)

    @staticmethod
    def __parse_response_data_FA(line: dict):
        i_stat = line.get("stat")
        line_data = {
            "asic.name": line.get("name"),
            "asic.taskId": line.get("taskId"),
            "asic.state": line.get("state"),
        }
        units_T_data = None
        units_U_data = None
        units_I_data = None
        if i_stat != {}:
            stat_data = {
                "asic.P": i_stat.get("units")[0].get("P"),
            }
            units_T_data = i_stat.get("units")[0].get("T")
            units_U_data = i_stat.get("units")[0].get("U")
            units_I_data = i_stat.get("units")[0].get("I")
            line_data.update(stat_data)
        return line_data, units_T_data, units_U_data, units_I_data

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    if metric_id in ["asic.name"]:
                        result = self.validate_string(result)
                    elif metric_id in ["asic.taskId"]:
                        result = self.validate_integer(result)
                    elif metric_id in ["asic.P"]:
                        result = self.validate_double(result)
                    else:
                        result = self.validate_state(HASH_STATE.get(result, None))
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
