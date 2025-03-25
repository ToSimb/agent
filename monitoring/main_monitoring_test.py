import json
import time
import os

from cpu.cpu import CPUsMonitor

def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

def cpu_start():
    cpu_instance, time_cpu_int = measure_execution_time(CPUsMonitor)
    _, time_cpu_update = measure_execution_time(cpu_instance.update)
    cpu_objects, time_cpu_get_obj = measure_execution_time(cpu_instance.get_objects)

    cpu_file_name = 'settings_file/cpu.txt'
    if not os.path.isfile(cpu_file_name):
        with open(cpu_file_name, 'w') as cpu_file:
            cpu_file_return = {}
            for index_cpu in cpu_objects:
                cpu_file_return[cpu_objects[index_cpu]] = None
            print(cpu_file_return)
            json.dump(cpu_file_return, cpu_file, indent=4)
        return 0
    with open(cpu_file_name, 'r') as cpu_file:
        cpu_file_index = json.load(cpu_file)
        index_list = cpu_instance.create_index(cpu_file_index)










cpu_start()