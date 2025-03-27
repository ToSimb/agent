import requests
import time

URL = f"http://127.0.0.1:8080/freon/22"
# URL = f"http://192.168.123.61:9002/api/v1/system"


class FreonA:
    def __init__(self):
        self.vus = {}
        self.conn = False
        fa = self.send_req()
        if fa is not None:
            self.conn = True
            for i in fa["rows"]:
                if i["name"]:
                    self.vus[i["name"]] = Board_f_a(i["name"])
                else:
                    print("!!!!!!!!!!!!!!!!!!!1")
        else:
            print("нет соединения при init")
        print(f"Количество узлов {len(self.vus)}")

    def send_req(self):
        try:
            response = requests.get(URL)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при обращении к API: {e}")
            return None

    def update(self):
        fa = self.send_req()
        if fa is not None:
            self.conn = True
            print("есть связь")
            for i in fa["rows"]:
                if i["name"]:
                    self.vus[i["name"]].update(i)
        else:
            self.conn = False

    def get_all(self):
        for vu in self.vus.values():
            aaa = vu.get_params_all()
            print(aaa)

    def get_item_all(self, vu: str):
        try:
            return self.vus.get(vu).get_params_all()
        except:
            return None

    def get_item(self, vu: str, metric_id: str):
        try:
            return self.vus.get(vu).get_metric(metric_id)
        except:
            print(f"ошибка - {vu}: {metric_id}")
            return None

class Board_f_a:
    def __init__(self, ip_address: str):
        self.params = {
            "name": ip_address,
            "taskId": None,
            "state": None,
            "coord": None,
            "unit.P": None,
            "unit.T": None,
            "unit.U": None,
            "unit.I": None
        }

    def update(self, line:dict):
        self.params.update(self.parse_response_data_FA(line))

    def parse_response_data_FA(self, line:dict):
        i_stat = line.get("stat")
        line_data = {
            "name": line.get("name"),
            "taskId": line.get("taskId"),
            "state": line.get("state"),
        }
        if i_stat != {}:
            stat_data = {
                "coord": i_stat.get("coord"),
                "unit.P": i_stat.get("units")[0].get("P"),
                "unit.T": i_stat.get("units")[0].get("T"),
                "unit.U": i_stat.get("units")[0].get("U"),
                "unit.I": i_stat.get("units")[0].get("I"),
            }
            line_data.update(stat_data)
        return line_data

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

