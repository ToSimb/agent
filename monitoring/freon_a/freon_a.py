import json
import requests

URL = f"http://127.0.0.1:8080/freon/22"
# URL = f"http://192.168.123.61:9002/api/v1/system"


class FreonA:
    def __init__(self, file_name):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            vus (dict): Словарь, где ключ - ip-address платы ++ может быть дополнение,
                            а значением - объект класса Core, представляющий ядро процессора.
                            Пример: {'192.168.86.194': <__main__.Board_f_a object at 0x79c9c8b41100>,
                                    '192.168.86.188': <__main__.Board_f_a object at 0x79c9c8b18700>, ...,

                                    '192.168.87.24:T:0': <__main__.Unit_T object at 0x76c321ebb220>}
            vus_info (dict): Словарь, где ключ  - ip-address платы  ++ может быть дополнение,
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'192.168.85.137': 'fa:1:1',
                                        '192.168.85.28': 'fa:1:2', ... ,

                                        192.168.87.24:T:0': 'fa:1:2:T:0', ...

                                        'agent_connection': 'fa:agent_connection'}
            item_index: Словарь, где ключ - это будущий item_id из схемы,
                        а значением - объект класса Core.
                        (по факту мы делаем новые ссылки на объекты)
                            Пример: {'1111': <__main__.Board_f_a object at 0x79c9c8b41100>,
                                     '1112': <__main__.Board_f_a object at 0x79c9c8b18700>, ...

                                     '1121':

                                     '1110': self.agent_connection }
            system (str): Название операционной системы (например, 'Linux').
        """
        self.vus = {}
        self.vus_info = {}
        self.conn = False
        self.agent_connection = -1
        self.item_index = {}
        fa = self.__send_req()
        if fa is not None:
            self.conn = True
            for i in fa["rows"]:
                if i["name"]:
                    self.vus[i["name"]] = Board_f_a(i["name"])
                    units_T, units_U, units_I = self.vus[i["name"]].get_all_obj()
                    for index_T in units_T.keys():
                        self.vus[f"{i['name']}:T:{index_T}"] = units_T[index_T]
                    for index_U in units_U.keys():
                        self.vus[f"{i['name']}:U:{index_U}"] = units_U[index_U]
                    for index_I in units_I.keys():
                        self.vus[f"{i['name']}:I:{index_I}"] = units_I[index_I]
                else:
                    print("ПРОБЛЕМА С ОТВЕТОМ ОТ Ф-А!")
        else:
            print("нет соединения с Ф-А при init")
        file_dict = self.__open_dict(file_name)
        if file_dict is not None:
            for index_vu in file_dict.keys():
                if index_vu in self.vus:
                    self.vus_info[index_vu] = f"fa:{file_dict[index_vu]['x']}:{file_dict[index_vu]['y']}"
                    for index in range(6):
                        self.vus_info[f"{[index_vu][0]}:T:{index}"] = \
                            f"fa:{file_dict[index_vu]['x']}:{file_dict[index_vu]['y']}:T:{index}"
                    for index in range(6):
                        self.vus_info[f"{[index_vu][0]}:U:{index}"] = \
                            f"fa:{file_dict[index_vu]['x']}:{file_dict[index_vu]['y']}:U:{index}"
                    for index in range(6):
                        self.vus_info[f"{[index_vu][0]}:I:{index}"] = \
                            f"fa:{file_dict[index_vu]['x']}:{file_dict[index_vu]['y']}:I:{index}"
                else:
                    print(f"ERROR: нет {index_vu} в списке объектов!")
            self.vus_info['agent_connection'] = 'fa:agent_connection'
        else:
            print("файл пустой")
        if (len(self.vus)+1) == len(self.vus_info):
            print("ВСЕ ОБЪЕКТЫ СОЗДАНЫ")

    @staticmethod
    def __open_dict(file_name):
        try:
            with open(file_name, "r") as f:
                file_dict = json.load(f)
                return file_dict
        except Exception as e:
            print(f"Ошибка при прочтении файла конфигурации для ФА - {e}")
            return None

    @staticmethod
    def __send_req():
        try:
            response = requests.get(URL)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при обращении к API: {e}")
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
                'agent_connection': 1200
            }
        """
        for index in fa_dict:
            if fa_dict[index] is not None:
                if index == "agent_connection":
                    self.agent_connection = fa_dict[index]
                else:
                    for key, value in self.vus_info.items():
                        if value == index:
                            self.item_index[str(fa_dict[index])] = self.vus.get(key, None)
                            break
                    else:
                        print(f'Для индекса {index} нет значения')
        print("Индексы для Ф-А обновлены")

    def update(self):
        fa = self.__send_req()
        if fa is not None:
            self.conn = True
            print("update")
            for i in fa["rows"]:
                if i["name"]:
                    self.vus[i["name"]].update(i)
        else:
            self.conn = False

    def get_all(self):
        """
            Возращает все параметры, кроме agent_connection
        """
        return_list = []
        for vu in self.vus.keys():
            result = self.vus[vu].get_params_all()
            return_list.append({vu :result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            if item_id in str(self.agent_connection):
                if metric_id == "agent_connection":
                    return self.conn
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            print(f"ошибка - {item_id}: {metric_id} - {e}")
            return None

class Board_f_a:
    def __init__(self, ip_address: str):
        self.units_T = {}
        self.units_U = {}
        self.units_I = {}
        self.params = {
            "name": ip_address,
            "taskId": None,
            "state": None,
            "unit.P": None,
        }
        for index in range(6):
            self.units_T[index] = Unit_T()
            self.units_U[index] = Unit_U()
            self.units_I[index] = Unit_I()

    def get_all_obj(self):
        return self.units_T, self.units_U, self.units_I

    def update(self, line:dict):
        params, units_T_data, units_U_data, units_I_data = self.parse_response_data_FA(line)
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

    def parse_response_data_FA(self, line:dict):
        i_stat = line.get("stat")
        line_data = {
            "name": line.get("name"),
            "taskId": line.get("taskId"),
            "state": line.get("state"),
        }
        units_T_data = None
        units_U_data = None
        units_I_data = None
        if i_stat != {}:
            stat_data = {
                "unit.P": i_stat.get("units")[0].get("P"),
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
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Unit_T:
    def __init__(self):
        self.params = {
            "unit.T": None,
        }

    def update(self, params):
        self.params["unit.T"] = params

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Unit_U:
    def __init__(self):
        self.params = {
            "unit.U": None,
        }

    def update(self, params):
        self.params["unit.U"] = params

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


class Unit_I:
    def __init__(self):
        self.params = {
            "unit.I": None,
        }

    def update(self, params):
        self.params["unit.I"] = params

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None