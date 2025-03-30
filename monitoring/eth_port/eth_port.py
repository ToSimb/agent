import psutil
import time

INTERVAL = 0.5

class EthPortMonitor:
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
                    print(f'Для индекса {index} нет значения')
        self.update_eth_ports_of_update(eth_ports_list)
        print("Индексы для ETH_PORT обновлены")

    def update_eth_ports_of_update(self, eth_ports_list: list):
        """
        Пример eth_ports_list: ['lo', 'enp34s0']
        """
        for key in self.eth_ports_to_update.keys():
            if key in eth_ports_list:
                self.eth_ports_to_update[key] = True
            else:
                self.eth_ports_to_update[key] = False
        print("Значения условий изменения портов изменены")

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
            print(f"ошибка - {item_id}: {metric_id}")
            return None

class EthPort:
    def __init__(self, eth_port_name: str, ):
        self.name = eth_port_name
        bandwidth_stats = psutil.net_if_stats()
        bandwidth_stat = bandwidth_stats.get(self.name, None)
        self.max_bandwidth = int(bandwidth_stat.speed * 125000) if bandwidth_stat.speed != 0.0 else None
        self.params = {
            "port.in.bytes": None,
            "port.in.packets": None,
            "port.in.speed": None,
            "port.in.load": None,
            "port.out.errors": None,
            "port.out.bytes": None,
            "port.out.packets": None,
            "port.in.errors": None,
            "port.out.speed": None,
            "port.out.load": None
        }

    def update(self, first_stats_eth_port, second_stats_eth_port):
        in_speed = round(float(second_stats_eth_port.bytes_recv - first_stats_eth_port.bytes_sent) / INTERVAL, 2)
        out_speed = round(float(second_stats_eth_port.bytes_sent - first_stats_eth_port.bytes_sent) / INTERVAL, 2)

        if self.max_bandwidth is None:
            in_load = None
            out_load = None
        else:
            in_load = round((in_speed / float(self.max_bandwidth)) * 100.0, 2)
            out_load =  round((out_speed / float(self.max_bandwidth)) * 100.0, 2)

        result = {
            "port.in.bytes": second_stats_eth_port.bytes_recv,
            "port.in.packets": second_stats_eth_port.packets_recv,
            "port.in.speed": in_speed,
            "port.in.load": in_load,
            "port.out.errors": second_stats_eth_port.errout,
            "port.out.bytes": second_stats_eth_port.bytes_sent,
            "port.out.packets": second_stats_eth_port.packets_sent,
            "port.in.errors": second_stats_eth_port.errin,
            "port.out.speed": out_speed,
            "port.out.load": out_load
        }
        self.params.update(result)

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
