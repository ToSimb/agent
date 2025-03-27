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
    cpu_prime, time_cpu_int = measure_execution_time(CPUsMonitor)
    _, time_cpu_update = measure_execution_time(cpu_prime.update)
    cpu_objects, time_cpu_get_obj = measure_execution_time(cpu_prime.get_objects_describtion)

    cpu_file_name = 'settings_file/cpu.txt'
    if not os.path.isfile(cpu_file_name):
        with open(cpu_file_name, 'w') as cpu_file:
            cpu_file_return = {}
            for index_cpu in cpu_objects:
                cpu_file_return[cpu_objects[index_cpu]] = None
            print(cpu_file_return)
            json.dump(cpu_file_return, cpu_file, indent=4)

    print(" * " * 10)
    print('CPU start time:', time_cpu_int)
    print('CPU update time:', time_cpu_update)
    print('CPU get object time:', time_cpu_get_obj)
    print(" * " * 10)

def main():
    cpu_start()
    print("- - -"*10)

if __name__ == "__main__":
    main()