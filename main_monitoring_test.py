import sys
import threading
import json
import time

from monitoring.service import (create_index_for_any,
                                get_metrics_polling_plan,
                                update_metrics_polling,
                                calculate_gcd_for_group,
                                wait_for_start_signal,
                                build_metric_tuples,
                                get_launch_timestamp,
                                crate_items_agent_reg_response)
from monitoring.system.system import SystemMonitor
from monitoring.cpu.cpu import CPUsMonitor
from monitoring.gpu_nvidia.gpu_nvidia import GPUsMonitor
from monitoring.lvol.lvol import LvolsMonitor
from monitoring.disk.disk import DisksMonitor
from monitoring.eth_port.eth_port import EthPortMonitor
from monitoring.freon_a.freon_a import FreonA
from monitoring.freon_b.freon_b import FreonB
from storage.sqlite_commands import (create_connection,
                                     check_db,
                                     insert_params)
from storage.settings_handler import (get_file_mtime,
                                      get_settings)
from logger.logger_monitoring import logger_monitoring
from config import (DEBUG_MODE)

stop_event = threading.Event()


# ___________________________________
monitor_configs = [
    {
        'name': 'system',
        'monitor_class': SystemMonitor,
        'settings_file': 'monitoring/_settings_file/system_proc.txt',
    },
    {
        'name': 'cpu',
        'monitor_class': CPUsMonitor,
        'settings_file': 'monitoring/_settings_file/cpu_proc.txt',
    },
    {
        'name': 'gpu',
        'monitor_class': GPUsMonitor,
        'settings_file': 'monitoring/_settings_file/gpu_proc.txt',
    },
    {
        'name': 'lvol',
        'monitor_class': LvolsMonitor,
        'settings_file': 'monitoring/_settings_file/lvol_proc.txt',
    },
    {
        'name': 'disk',
        'monitor_class': DisksMonitor,
        'settings_file': 'monitoring/_settings_file/disk_proc.txt',
    },
    {
        'name': 'if',
        'monitor_class': EthPortMonitor,
        'settings_file': 'monitoring/_settings_file/if_proc.txt',
    },
    # {
    #     'name': 'f_a',
    #     'monitor_class': FreonA,
    #     'settings_file': 'monitoring/_settings_file/f_a_proc.txt',
    # },
    # {
    #     'name': 'f_b',
    #     'monitor_class': FreonB,
    #     'settings_file': 'monitoring/_settings_file/f_b_proc.txt',
    # }
]
# ___________________________________

def periodic_update(object_monitor, interval):
    while not stop_event.is_set():
        time_start = time.time()
        object_monitor.update()
        time_update = time.time() - time_start
        if time_update < interval:
            time.sleep(interval - time_update)
    logger_monitoring.info(f"Поток завершился {object_monitor.name}")


def main():
    try:
        CONN = create_connection()

        monitors = {}
        item_monitor_map = {}
        threads = []
        last_modified_time, user_query_interval_revision = get_launch_timestamp()

        if last_modified_time == -1:
            logger_monitoring.error("REST CLIENT не запущен")
            exit(1)

        metrics_polling_plan, item_all_interval = get_metrics_polling_plan()

        if metrics_polling_plan is None:
            logger_monitoring.error("НЕТ ФАЙЛА с MIL")
            sys.exit(1)

        items_agent_reg_response = crate_items_agent_reg_response()
        for config in monitor_configs:
            monitor_class = config['monitor_class']

            monitor = monitor_class()

            index_list = create_index_for_any(items_agent_reg_response, config['settings_file'], monitor)

            for item_id in index_list:
                item_monitor_map[item_id] = monitor

            monitors[config['name']] = {
                'monitor': monitor,
                'index_list': index_list
            }

        # Добавляем интервал и поток для каждого монитора
        for name, data in monitors.items():
            monitor = data['monitor']

            update_interval = calculate_gcd_for_group(data['index_list'], item_all_interval)
            logger_monitoring.info(f" Для [{name}] получен interval update = {update_interval}")

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
            # блок о проверки обновления
            current_modified_time = get_file_mtime()
            if last_modified_time != current_modified_time:
                _, uqir_new, rest_client_start = get_settings()
                if not rest_client_start:
                    logger_monitoring.error("REST CLIENT закрылся")
                    sys.exit(1)
                if uqir_new != user_query_interval_revision:
                    user_query_interval_revision = uqir_new
                    metrics_polling_plan = update_metrics_polling()
                    logger_monitoring.info("Обновлено MIL")
                last_modified_time = current_modified_time
            # ______________

            time_start = time.time()
            time_index = int(time_start)
            params = []
            for time_value, data in metrics_polling_plan.items():
                if time_value > 0:
                    if tick_count % time_value == 0:
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
                                # else:
                                #     print(time.time(), "не собрано", item_id, metric_id, pf, "!!!!!!!!!!!!!!!1")
                            # else:
                            #     print(f"_________________________________________ {item_id} NOTNOT")
                # else:
                #     print(f"0: {data}")

            time_1 = time.time()
            insert_params(CONN, params)
            logger_monitoring.info(f"СОБРАНО МЕТРИК: {len(params)} | Время запись в БД: {time_1 - time_start}")
            time_gets = time.time() - time_start
            if time_gets < 1:
                time.sleep(1 - time_gets)
            tick_count = tick_count + 1

    except Exception as e:
        logger_monitoring.error(e)
    finally:
        logger_monitoring.info("Остановка потоков...")

        stop_event.set()

        for thread in threads:
            thread.join()
            logger_monitoring.info(f"Поток {thread.name} завершён.")

        if CONN is not None:
            CONN.close()
            logger_monitoring.info("Соединение с БД закрыто")

        logger_monitoring.info("Все потоки завершены. Выход из программы.")


if __name__ == "__main__":
    #в начале тут будет функция проверки, можно ли запускать приложение!!!!
    if not DEBUG_MODE:
        wait_for_start_signal()
    if not build_metric_tuples():
        logger_monitoring.error("REST CLIENT не запущен или проблема со схемами")
        exit(1)
    # создание и проверка промежуточных файлов
    main()
