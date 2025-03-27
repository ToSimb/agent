import requests
import time


URL = f"http://127.0.0.1:8080/freon/25_2"
# URL = f"http://192.168.123.61:9002/api/v1/system"
COUNT_BOARDS = 6

class FreonB:
    def __init__(self):
        self.vus = {}
        self.conn = False
        fa = self.send_req()
        if fa is not None:
            self.conn = True
            for i in fa["rows"]:
                if i["name"]:
                    self.vus[i["name"]] = Vu_fb(i["name"])
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
        fb = self.send_req()
        if fb is not None:
            self.conn = True
            print("есть связь")
            for i in fb["rows"]:
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

    def get_item2(self, vu: str, board_index: int,metric_id: str):
        try:
            return self.vus.get(vu).get_item(board_index, metric_id)
        except:
            print(f"ошибка - {vu}: {metric_id}")
            return None

class Vu_fb:
    def __init__(self, ip_address: str):
        self.params = {
            "name": ip_address,
            "taskId": None,
            "state": None,
        }
        self.boards = {}
        for board_index in range(COUNT_BOARDS):
            self.boards[board_index] = Board_fb(board_index)

    def update(self, line):
        self.params["taskId"] = line["taskId"]
        self.params["state"] = line["state"]
        state_disconnect = False
        if self.params["state"] == "disconnected":
            state_disconnect = True
        for board_index in range(COUNT_BOARDS):
            self.boards[board_index].update(line["stat"]["units"][board_index], state_disconnect)

    def get_params_all(self):
        result = self.params.copy()
        for board_index in range(COUNT_BOARDS):
            result[f"units_{board_index}"] = self.boards[board_index].get_params_all()
        return result

    def get_item(self, board_index: int, metric_id: str):
        try:
            return self.boards.get(board_index).get_metric(metric_id)
        except:
            print(f"ошибка - {board_index}: {metric_id}")
            return None

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

class Board_fb:
    def __init__(self, board_index: int):
        self.params = {
            "index": board_index,
            "unit.state": None,
            "unit.P": None,
            "unit.T": None,
            "unit.U": None,
            "unit.I": None
        }

    def update(self, line: dict, state_disconnect):
        self.params.update(self.parse_response_data_FB(line,state_disconnect))


    def parse_response_data_FB(self, line: dict, state_disconnect):
        i_unit_state = line.get("state")
        if state_disconnect:
            i_unit_state = "disconnected"
        line_data = {
            "unit.state": i_unit_state,
            "unit.P": line.get("P"),
            "unit.T": line.get("T"),
            "unit.U": line.get("U"),
            "unit.I": line.get("I")
        }
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



