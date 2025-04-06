import os
import re

from monitoring.service import (open_file,
                                save_file_data)

agent_reg_response = open_file("agent_reg_response.json")

items = {}

for item in agent_reg_response.get('item_id_list'):
    items[item.get('full_path')] = item.get('item_id')

print(items)

folder_path = 'monitoring/_settings_file'

files = os.listdir(folder_path)

for file_name in files:
    if 'proc' in file_name:
        status_update = False
        obj_proc = open_file(f'{folder_path}/{file_name}')
        for item_key, item_data in obj_proc.items():
            if item_data in items:
                obj_proc[item_key] = items[item_data]
                status_update = True
        if status_update:
            file_name = file_name.replace('proc', 'final')
            save_file_data(f'{folder_path}/{file_name}', obj_proc)
