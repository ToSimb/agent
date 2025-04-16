import os
import re

from monitoring.service import (open_file,
                                save_file_data)

FA_VU_NO_FULL = 30

agent_scheme = open_file("agent_scheme.json")
# agent_scheme = open_file("create_scheme/agent_scheme.json")
# print(agent_scheme)

item_path = {}
for item in agent_scheme.get('scheme').get('item_id_list'):
    item_full_path = item.get('full_path')
    numbers = re.findall(r'\[(\d+)\]', item_full_path)
    if 'system_' in item_full_path.split('/')[-1]:
        item_path[f"chassis:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - system:{numbers[-1]}")
    elif 'chassis_' in item_full_path.split('/')[-1]:
        item_path[f"chassis:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - system:{numbers[-1]}")
    elif 'core_' in item_full_path.split('/')[-1]:
        item_path[f"cpu:{numbers[-2]}:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - cpu:{numbers[-2]}:{numbers[-1]}")
    elif 'gpu_' in item_full_path.split('/')[-1]:
        item_path[f"gpu:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - gpu:{numbers[-1]}")
    elif 'lvol_' in item_full_path.split('/')[-1]:
        item_path[f"lvol:{numbers[-1]}"] = item_full_path
        # print(f"{item.get('full_path')} - lvol:{numbers[-1]}")
    # if 'vus_fa_1' in item_full_path:
    #     print(f"{item_full_path} - самостоятельно установить")
    elif 'vu_fa_37' in item_full_path:
        if len(numbers) > 3:
            if 'temperature' in item_full_path:
                index = numbers[-4]
                if int(index) >= FA_VU_NO_FULL:
                    index = int(index) + 1
                item_path[f"fa:{index}:{numbers[-3]}:{numbers[-2]}:T:{numbers[-1]}"] = item_full_path
            elif 'current' in item_full_path:
                index = numbers[-4]
                if int(index) >= FA_VU_NO_FULL:
                    index = int(index) + 1
                item_path[f"fa:{index}:{numbers[-3]}:{numbers[-2]}:I:{numbers[-1]}"] = item_full_path
            elif 'voltage' in item_full_path:
                index = numbers[-4]
                if int(index) >= FA_VU_NO_FULL:
                    index = int(index) + 1
                item_path[f"fa:{index}:{numbers[-3]}:{numbers[-2]}:U:{numbers[-1]}"] = item_full_path
            else:
                index = numbers[-3]
                if int(index) >= FA_VU_NO_FULL:
                    index = int(index) + 1
                item_path[f"fa:{index}:{numbers[-2]}:{numbers[-1]}"] = item_full_path
    elif 'vu_fb_20' in item_full_path:
        if 'vu_fb_20' in item_full_path.split('/')[-1]:
            item_path[f"fb:{numbers[-1]}"] = item_full_path
        elif 'board_fb' in item_full_path.split('/')[-1]:
            item_path[f"fb:{numbers[-2]}:board:{numbers[-1]}"] = item_full_path
        elif 'temperature' in item_full_path.split('/')[-1]:
            item_path[f"fb:{numbers[-3]}:board:{numbers[-2]}:T:{numbers[-1]}"] = item_full_path
        elif 'current' in item_full_path.split('/')[-1]:
            item_path[f"fb:{numbers[-3]}:board:{numbers[-2]}:I:{numbers[-1]}"] = item_full_path
        elif 'voltage' in item_full_path.split('/')[-1]:
            item_path[f"fb:{numbers[-3]}:board:{numbers[-2]}:U:{numbers[-1]}"] = item_full_path
        elif 'connection' in item_full_path.split('/')[-1]:
            item_path[f"fb:{numbers[-2]}:connection"] = item_full_path

# print("Пути из схемы:")
# for item in item_path:
#     print(item)


folder_path = 'monitoring/_settings_file'

files = os.listdir(folder_path)
for file_name in files:
    if 'raw' in file_name:
        no_path = []
        status_update = False
        obj_raw = open_file(f'{folder_path}/{file_name}')
        for item_key, item_data in obj_raw.items():
            if item_key in item_path:
                obj_raw[item_key] = item_path[item_key]
                status_update = True
            else:
                no_path.append(item_key)
        if status_update:
            file_name = file_name.replace('raw', 'proc')
            save_file_data(f'{folder_path}/{file_name}', obj_raw)
            print(f"ФАЙЛ {file_name} изменен!")
            print(f"Не хватает описания для {len(no_path)}")
