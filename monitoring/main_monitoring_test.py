import threading
import json
import time

from cpu.cpu import CPUsMonitor

stop_event = threading.Event()

def periodic_update(object_monitor, interval):
    while not stop_event.is_set():
        time_start = time.time()
        object_monitor.update()
        time_update = time.time() - time_start
        if time_update < interval:
            time.sleep(interval - time_update)

def create_index_for_cpu(object_monitor):
    cpu_file_name = 'settings_file/cpu.txt'

    with open(cpu_file_name, 'r') as cpu_file:
        cpu_file_index = json.load(cpu_file)
        object_monitor.create_index(cpu_file_index)

def get_metrics():
    # считываем с файла!
    prototype_list = {
        '12': {
            'core.user.time': 1,
            'core.system.time': 2,
            'core.irq.time': 3,
            'core.softirq.time': 1,
            'core.idle.time': 1,
            'core.iowait': 2,
            'core.load': 3
        },
        '13': {
            'core.user.time': 1,
            'core.system.time': 2,
            'core.irq.time': 3,
            'core.softirq.time': 1,
            'core.idle.time': 1,
            'core.iowait': 2,
            'core.load': 3
        },
        '16': {
            'core.user.time': 1,
            'core.system.time': 2
        },
    }
    value_dict = {}
    for item_id, metrics in prototype_list.items():
        for metric_id, time_value in metrics.items():
            if time_value not in value_dict:
                value_dict[time_value] = []
            # Добавляем пару (внешний ключ, внутренний ключ) в список
            value_dict[time_value].append((item_id, metric_id))
    return value_dict

def main():
    cpu_prime = CPUsMonitor()
    create_index_for_cpu(cpu_prime)

    cpu_update_thread = threading.Thread(target=periodic_update, args=(cpu_prime, 1))
    cpu_update_thread.start()

    prototype_list_cpu = get_metrics()
    try:
        print(prototype_list_cpu)
        while True:
            time_start = time.time()
            time_index = int(time_start)
            print(time_index)
            params = []
            for time_value, data in prototype_list_cpu.items():
                if time_index % time_value == 0:
                    for item_id, metric_id in data:
                        aaa = cpu_prime.get_item(item_id, metric_id)
                        params.append(aaa)
                        print(time.time(), item_id, metric_id, aaa)
            print(f"!! СОБРАНО МЕТРИК {len(params)}")
            print("___________________")
            time_gets = time.time() - time_start
            time.sleep(1 - time_gets)

    except Exception as e:
        print(e)
    finally:
        stop_event.set()
        cpu_update_thread.join()
        print("Поток завершен.")

if __name__ == "__main__":
    main()