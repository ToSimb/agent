import threading
import json
import time

from monitoring.service import (create_index_for_any,
                                get_metrics_test)
from monitoring.cpu.cpu import CPUsMonitor
from storage.sqlite_commands import (create_connection,
                                     check_db,
                                     insert_params)

stop_event = threading.Event()

def periodic_update(object_monitor, interval):
    while not stop_event.is_set():
        time_start = time.time()
        object_monitor.update()
        time_update = time.time() - time_start
        if time_update < interval:
            time.sleep(interval - time_update)

def main():
    try:
        CONN = create_connection()
        cpu_prime = CPUsMonitor()
        cpu_file_name = 'monitoring/settings_file/cpu_final.txt'
        create_index_for_any(cpu_file_name, cpu_prime)

        cpu_update_thread = threading.Thread(target=periodic_update, args=(cpu_prime, 1))
        cpu_update_thread.start()

        prototype_list_cpu = get_metrics_test()

        print(prototype_list_cpu)
        while True:
            time_start = time.time()
            time_index = int(time_start)
            print(time_index)
            params = []
            for time_value, data in prototype_list_cpu.items():
                if time_value > 0:
                    if time_index % time_value == 0:
                        for item_id, metric_id in data:
                            pf = cpu_prime.get_item_and_metric(item_id, metric_id)
                            if pf is not None:
                                params.append(
                                    {'item_id': item_id,
                                     'metric_id': metric_id,
                                     't': time_index,
                                     'v': pf})
                            else:
                                print(time.time(), "не собрано", item_id, metric_id, pf, "!!!!!!!!!!!!!!!1")
            print(f"!! СОБРАНО МЕТРИК {len(params)}")
            time_1 = time.time()
            insert_params(CONN, params)
            print("Время запись в БД ",time_1 - time_start)
            print("___________________")
            time_gets = time.time() - time_start

            time.sleep(1 - time_gets)

    except Exception as e:
        print(e)
    finally:
        CONN.close()
        stop_event.set()
        cpu_update_thread.join()
        print("Поток завершен.")

if __name__ == "__main__":
    main()