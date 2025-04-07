import sys
import threading
import json
import time
from platform import system

from monitoring.service import (create_index_for_any,
                                get_metrics_polling_plan,
                                calculate_gcd_for_group)
from monitoring.system.system import SystemMonitor
from monitoring.cpu.cpu import CPUsMonitor
from monitoring.gpu_nvidia.gpu_nvidia import GPUsMonitor
from storage.sqlite_commands import (create_connection,
                                     check_db,
                                     insert_params)

from config import (DEBUG_MODE)

stop_event = threading.Event()


# ___________________________________
monitor_configs = [
    {
        'name': 'system',
        'monitor_class': SystemMonitor,
        'settings_file': 'monitoring/_settings_file/system_final.txt',
    },
    {
        'name': 'cpu',
        'monitor_class': CPUsMonitor,
        'settings_file': 'monitoring/_settings_file/cpu_final.txt',
    },
    {
        'name': 'gpu',
        'monitor_class': GPUsMonitor,
        'settings_file': 'monitoring/_settings_file/gpu_final.txt',
    }
]
# ___________________________________

def periodic_update(object_monitor, interval):
    while not stop_event.is_set():
        time_start = time.time()
        object_monitor.update()
        time_update = time.time() - time_start
        if time_update < interval:
            time.sleep(interval - time_update)
    print(f"Поток завершился {object_monitor.name}")


def main():
    try:
        CONN = create_connection()

        monitors = {}
        item_monitor_map = {}
        threads = []

        for config in monitor_configs:
            monitor_class = config['monitor_class']

            monitor = monitor_class()

            index_list = create_index_for_any(config['settings_file'], monitor)

            for item_id in index_list:
                item_monitor_map[item_id] = monitor

            monitors[config['name']] = {
                'monitor': monitor,
                'index_list': index_list
            }

        prototype_list, item_all_interval = get_metrics_polling_plan()

        # Добавляем интервал и поток для каждого монитора
        for name, data in monitors.items():
            monitor = data['monitor']

            update_interval = calculate_gcd_for_group(data['index_list'], item_all_interval)
            print(f"[{name}] interval = {update_interval}")

            if update_interval is None:
                continue  # или throw

            thread = threading.Thread(
                target=periodic_update,
                args=(monitor, update_interval),
                name=f"{name}_update"
            )
            thread.start()
            threads.append(thread)

        tick_count = 1
        while True:
            # блок о проверки обвновления

            time_start = time.time()
            time_index = int(time_start)
            params = []
            for time_value, data in prototype_list.items():
                if time_value > 0:
                    if tick_count % time_value == 0:
                        print(f"_______ {time_value} _____")
                        for item_id, metric_id in data:
                            obj_item = item_monitor_map.get(item_id)
                            if obj_item is not None:
                                pf = obj_item.get_item_and_metric(str(item_id), metric_id)
                                if pf is not None:
                                    params.append(
                                        {'item_id': item_id,
                                         'metric_id': metric_id,
                                         't': time_index,
                                         'v': pf})
                                else:
                                    print(time.time(), "не собрано", item_id, metric_id, pf, "!!!!!!!!!!!!!!!1")
                            else:
                                print(f"_________________________________________ {item_id} NOTNOT")
                else:
                    print(f"0: {data}")
            print(f"!! СОБРАНО МЕТРИК {len(params)}")
            time_1 = time.time()
            insert_params(CONN, params)
            print("Время запись в БД ", time_1 - time_start)
            print("___________________")
            time_gets = time.time() - time_start
            if time_gets < 1:
                time.sleep(1 - time_gets)
            tick_count = tick_count + 1

    except Exception as e:
        print(e)
    finally:
        print("Остановка потоков...")

        stop_event.set()

        for thread in threads:
            thread.join()
            print(f"Поток {thread.name} завершён.")

        print("Поток завершен.")
        if CONN is not None:
            CONN.close()
            print("Соединение с БД закрыто")

        print("Все потоки завершены. Выход из программы.")


if __name__ == "__main__":
    #в начале тут будет функция проверки, можно ли запускать приложение!!!!
    # создание и проверка промежуточных файлов
    main()
