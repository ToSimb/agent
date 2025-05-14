import psutil
import time
import json
import os

from monitoring.base import BaseObject, SubObject

from logger.logger_mon_eth_port import logger_monitoring

INTERVAL = 0.5

class EthPortMonitor(BaseObject):
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            eth_ports (dict): Словарь, где ключ - имя сетевого интерфейса,
                            а значением - объект класса EthPort, представляющий ядро процессора.
                            Пример: {'lo': <__main__.EthPort object at 0x7388406140d0>,
                                     'enp34s0': <__main__.EthPort object at 0x738840614370>}
            eth_ports_info (dict): Словарь, где ключ - имя сетевого интерфейса,
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'lo': 'eth:lo',
                                        'enp34s0': 'eth:enp34s0'}
            item_index (dict): Словарь, где ключ - это будущий item_id из схемы,
                                а значением - объект класса Core.
                                (по факту мы делаем новые ссылки на объекты)
                                Пример: {'22': <__main__.EthPort object at 0x7388406140d0>,
                                        '23': <__main__.EthPort object at 0x738840614370>}
            eth_ports_to_update (dict): Уникальная переменная, которая указывает какие порты обновлять
                            Пример: {'lo': True, 'enp34s0': False}
        """
        super().__init__()
        self.eth_ports = {}
        self.eth_ports_info = {}
        self.eth_ports_to_update = {}
        self.item_index = {}
        for eth_port_name in psutil.net_io_counters(pernic=True).keys():
            self.eth_ports[eth_port_name] = EthPort(eth_port_name)
            self.eth_ports_info[eth_port_name] = f"eth:{eth_port_name}"
            self.eth_ports_to_update[eth_port_name] = True

    def get_objects_description(self):
        return self.eth_ports_info

    def create_index(self, eth_port_dict):
        """
        Пример eth_port_dict: {
            'eth:lo': '32',
            'eth:enp34s0': '33'
            }
        """
        eth_ports_list = []
        for index in eth_port_dict:
            if eth_port_dict[index] is not None:
                for key, value in self.eth_ports_info.items():
                    if value == index:
                        eth_ports_list.append(key)
                        self.item_index[str(eth_port_dict[index])] = self.eth_ports.get(key, None)
                        break
                else:
                    logger_monitoring.debug(f'Для индекса {index} нет значения')
        self.update_eth_ports_of_update(eth_ports_list)
        logger_monitoring.info("Индексы для ETH_PORT (if) обновлены")

    def update_eth_ports_of_update(self, eth_ports_list: list):
        """
        Пример eth_ports_list: ['lo', 'enp34s0']
        """
        for key in self.eth_ports_to_update.keys():
            if key in eth_ports_list:
                self.eth_ports_to_update[key] = True
            else:
                self.eth_ports_to_update[key] = False
        logger_monitoring.info("Значения условий изменения портов изменены")

    def update(self):
        first_stats = psutil.net_io_counters(pernic=True)
        time.sleep(INTERVAL)
        second_stats = psutil.net_io_counters(pernic=True)
        for key in self.eth_ports_to_update.keys():
            if self.eth_ports_to_update[key]:
                self.eth_ports[key].update(first_stats[key], second_stats[key])

    def get_all(self):
        return_list = []
        for key in self.eth_ports_to_update.keys():
            if self.eth_ports_to_update[key]:
                result = self.eth_ports[key].get_params_all()
                return_list.append({key: result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except:
            logger_monitoring.error(f"Ошибка при вызове item_id - {item_id}: {metric_id}")
            return None


class EthPort(SubObject):
    def __init__(self, eth_port_name: str, ):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(script_dir, "if_dict.txt")
        file_max_bandwidth = self.__open_dict(file_name)
        self.name = eth_port_name
        if self.name in file_max_bandwidth.keys():
            self.max_bandwidth = file_max_bandwidth[self.name]
        else:
            bandwidth_stats = psutil.net_if_stats()
            bandwidth_stat = bandwidth_stats.get(self.name, None)
            self.max_bandwidth = int(bandwidth_stat.speed * 125000) if bandwidth_stat.speed != 0.0 else None
        logger_monitoring.debug(f"{self.name} : {self.max_bandwidth}")
        self.params = {
            "if.in.bytes": None,
            "if.in.packets": None,
            "if.in.speed": None,
            "if.in.load": None,
            "if.out.errors": None,
            "if.out.bytes": None,
            "if.out.packets": None,
            "if.in.errors": None,
            "if.out.speed": None,
            "if.out.load": None
        }

    @staticmethod
    def __open_dict(file_name):
        try:
            with open(file_name, "r", encoding="utf-8-sig") as f:
                file_dict = json.load(f)
                return file_dict
        except Exception as e:
            logger_monitoring.error(f"Ошибка при прочтении файла конфигурации для Портов - {e}")
            return None

    def update(self, first_stats_eth_port=None, second_stats_eth_port=None):
        in_speed = round(float(second_stats_eth_port.bytes_recv - first_stats_eth_port.bytes_recv) / INTERVAL, 2)
        out_speed = round(float(second_stats_eth_port.bytes_sent - first_stats_eth_port.bytes_sent) / INTERVAL, 2)

        if self.max_bandwidth is None:
            in_load = None
            out_load = None
        else:
            in_load = round((in_speed / float(self.max_bandwidth)) * 100.0, 2)
            out_load =  round((out_speed / float(self.max_bandwidth)) * 100.0, 2)

        result = {
            "if.in.bytes": second_stats_eth_port.bytes_recv,
            "if.in.packets": second_stats_eth_port.packets_recv,
            "if.in.speed": in_speed,
            "if.in.load": in_load,
            "if.out.errors": second_stats_eth_port.errout,
            "if.out.bytes": second_stats_eth_port.bytes_sent,
            "if.out.packets": second_stats_eth_port.packets_sent,
            "if.in.errors": second_stats_eth_port.errin,
            "if.out.speed": out_speed,
            "if.out.load": out_load
        }
        self.params.update(result)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    if metric_id in ["if.in.speed", "if.in.load", "if.out.speed", "if.out.load"]:
                        result = self.validate_double(result)
                    else:
                        result = self.validate_integer(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None