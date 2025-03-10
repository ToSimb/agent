import requests
import time

URL = f"http://127.0.0.1:8080/freon/25_2"
# URL = f"http://192.168.123.61:9002/api/v1/system"


def parse_response_data_FA (fa: dict):
    data_dict = []
    ips = []
    error_ips = []
    for i in fa["rows"]:
        if i.get("name") is not ips:
            ips.append(i.get("name"))
            i_stat = i.get("stat")
            if i_stat != {}:
                i_data = {
                    "name": i.get("name"),
                    "taskId": i.get("taskId"),
                    "state": i.get("state"),
                    "coord": i_stat.get("coord"),
                    "unit.P": i_stat.get("units")[0].get("P"),
                    "unit.T": i_stat.get("units")[0].get("T"),
                    "unit.U": i_stat.get("units")[0].get("U"),
                    "unit.I": i_stat.get("units")[0].get("I"),
                }
                data_dict.append(i_data)

        else:
            error_ips.append(i.get("name"))
        if len(error_ips) > 0:
            print("Ошибка в получении JSON")
    return data_dict

def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Ошибка при обращении к API: {e}")
        return None

start_time = time.time()
fa = get_data_from_api(URL)
get_time = time.time()

with open("freon_b.txt", "w", encoding="utf-8") as file:
    file.write(f"время получения данных: {get_time - start_time}\n")

    if fa is not None:
        file.write("Есть связь\n")
        data_dict = parse_response_data_FA(fa)
        id_count = len(data_dict)
        parser_time = time.time()
        file.write(f"Время парсинга: {parser_time - get_time}\n")
        file.write(f"Количество собранных узлов: {id_count}\n")
        file.write("- - " * 10 + "\n")

        for i in data_dict:
            file.write(f"    сетевой адрес вычислительного блока ЗМСН            {i['name']}\n")
            file.write(f"    состояние                                           {i['state']}\n")
            file.write(f"    координаты                                          {i['coord']}\n")
            file.write(f"    идентификатор решаемой задачи                       {i['taskId']}\n")
            file.write(f"    температуры вычислительных плат с ЗМСН              {i['unit.T']}\n")
            file.write(f"    ток питания вычислительных плат с ЗМСН              {i['unit.I']}\n")
            file.write(f"    напряжение питания вычислительных плат с ЗМСН       {i['unit.U']}\n")
            file.write(f"    потребляемая мощность вычислительных плат с ЗМСН    {i['unit.P']}\n")
            file.write("-" * 30 + "\n")
print("     freon_b.txt")

