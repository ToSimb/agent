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
        monitors = {
            'core': CPUsMonitor(),
            # 'ram': RAMMonitor(),
            # 'disk': DiskMonitor(),
            # и т.д.
        }
        # cpu_prime = CPUsMonitor()
        # cpu_file_name = 'monitoring/settings_file/cpu_final.txt'
        # create_index_for_any(cpu_file_name, cpu_prime)

        # cpu_update_thread = threading.Thread(target=periodic_update, args=(cpu_prime, 1))
        # cpu_update_thread.start()

        threads = []
        for prefix, monitor in monitors.items():
            create_index_for_any(f'monitoring/_settings_file/{prefix}_final.txt', monitor)
            t = threading.Thread(target=periodic_update, args=(monitor, 1))
            t.start()
            threads.append(t)

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
                            print(metric_id.split('.')[0])
                            obj_monitor = monitors.get(metric_id.split('.')[0])
                            if obj_monitor:
                                print(obj_monitor)
                                pf = obj_monitor.get_item_and_metric(item_id, metric_id)
                                if pf is not None:
                                    params.append(
                                        {'item_id': item_id,
                                         'metric_id': metric_id,
                                         't': time_index,
                                         'v': pf})
                                else:
                                    print(time.time(), "не собрано", item_id, metric_id, pf, "!!!!!!!!!!!!!!!1")
                            else:
                                print(f"[WARN] Не найден монитор для метрики {metric_id}")
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
        print("Остановка потоков...")
        stop_event.set()  # сигнал всем потокам на завершение

        for thread in threads:
            thread.join()
            print("Поток завершён")

        if CONN:
            CONN.close()
            print("Соединение с БД закрыто")

        print("Все потоки завершены. Выход из программы.")

if __name__ == "__main__":
    main()