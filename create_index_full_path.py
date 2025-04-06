import os
import re

from monitoring.service import (open_file,
                                save_file_data)

agent_scheme = open_file("agent_scheme.json")
print(agent_scheme)

item_path = {}
for item in agent_scheme.get('scheme').get('item_id_list'):
    item_full_path = item.get('full_path')
    numbers = re.findall(r'\[(\d+)\]', item_full_path)
    if 'system' in item_full_path.split('/')[-1]:
        item_path[f"chassis:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - system:{numbers[-1]}")
    if 'core' in item_full_path.split('/')[-1]:
        item_path[f"cpu:{numbers[-2]}:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - cpu:{numbers[-2]}:{numbers[-1]}")
    if 'gpu' in item_full_path.split('/')[-1]:
        item_path[f"gpu:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - gpu:{numbers[-1]}")
    if 'agent' in item_full_path.split('/')[-1]:
        print(item_full_path)

print(item_path)

folder_path = 'monitoring/_settings_file'

files = os.listdir(folder_path)
for file_name in files:
    if 'raw' in file_name:
        print(file_name)
        status_update = False
        obj_raw = open_file(f'{folder_path}/{file_name}')
        for item_key, item_data in obj_raw.items():
            if item_key in item_path:
                print(item_key)
                obj_raw[item_key] = item_path[item_key]
                status_update = True
            # else:
            #     print(f"нет такого элемента {item_key}")
        if status_update:
            file_name = file_name.replace('raw', 'proc')
            save_file_data(f'{folder_path}/{file_name}', obj_raw)
