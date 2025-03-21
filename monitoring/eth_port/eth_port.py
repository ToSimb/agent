import psutil
import time

INTERVAL = 0.5

class EthPortMonitor:
    def __init__(self):
        self.eth_ports = {}
        self.eth_ports_to_update = {}
        for eth_port_name in psutil.net_io_counters(pernic=True).keys():
            self.eth_ports[eth_port_name] = EthPort(eth_port_name)
            self.eth_ports_to_update[eth_port_name] = True

    def get_eth_ports_of_update(self):
        return self.eth_ports_to_update

    def update_eth_ports_of_update(self, eth_ports_list: list):
        for key in self.eth_ports_to_update.keys():
            if key in eth_ports_list:
                self.eth_ports_to_update[key] = True
            else:
                self.eth_ports_to_update[key] = False

    def update(self):
        first_stats = psutil.net_io_counters(pernic=True)
        time.sleep(INTERVAL)
        second_stats = psutil.net_io_counters(pernic=True)
        for key in self.eth_ports_to_update.keys():
            if self.eth_ports_to_update[key]:
                self.eth_ports[key].update(first_stats[key], second_stats[key])

    def get_all(self):
        for key in self.eth_ports_to_update.keys():
            if self.eth_ports_to_update[key]:
                print(self.eth_ports[key].get_params_all())

    def get_item_all(self, eth_port_name: str):
        try:
            return self.eth_ports.get(eth_port_name).get_params_all()
        except:
            return None

    def get_item(self, eth_port_name: str, metric_id:str):
        try:
            return self.eth_ports.get(eth_port_name).get_metric(metric_id)
        except:
            print(f"ошибка - {eth_port_name}: {metric_id}")
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
        return self.params.get(metric_id, None)