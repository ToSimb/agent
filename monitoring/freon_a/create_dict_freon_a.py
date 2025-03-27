import requests
import json

URL = f"http://127.0.0.1:8080/freon/22"
# URL = f"http://192.168.123.61:9002/api/v1/system"

def get_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Ошибка при обращении к API: {e}")
        return None

data_list = []
fa = get_data_from_api(URL)
if fa is not None:
    print("есть связь")
    for i in fa["rows"]:
        if i["name"]:
            coord = None
            if i.get("stat") != {}:
                coord = i.get("stat").get("coord")
            data_list.append((i["name"], coord))

data_list.sort(key=lambda item: (item[1]['x'] if item[1] is not None else float('-inf'),
                                   item[1]['y'] if item[1] is not None else float('-inf')))

fa_dict = {name: {"x": coord['x'], "y": coord['y']} if coord is not None else None for name, coord in data_list}

with open('freon_dict.txt', 'w') as file:
    json.dump(fa_dict, file, indent=4)