import sys
import threading
import json
import time
import signal
import atexit

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
from monitoring.disk_lite.disk_lite import DisksLiteMonitor
from monitoring.eth_port.eth_port import EthPortMonitor
from monitoring.freon_a.freon_a import FreonA
from monitoring.freon_b.freon_b import FreonB
from monitoring.switch.switch import Switch
from storage.sqlite_commands import (create_connection,
                                     check_db,
                                     insert_params)
from storage.settings_handler import (get_file_mtime,
                                      get_settings)
from logger.logger_monitoring import logger_monitoring
from config import (DEBUG_MODE)


def signal_handler(sig, frame):
    logger_monitoring.info(f"Получен сигнал завершения: {sig}")
    cleanup_and_exit()

def cleanup_and_exit():
    logger_monitoring.info("Завершение приложения...")
    stop_event.set()

    for thread in threading.enumerate():
        if thread.name.endswith('_update') and thread.is_alive():
            logger_monitoring.info(f"Ожидание завершения потока {thread.name}...")
            thread.join(timeout=5)

    if CONN:
        CONN.close()
        logger_monitoring.info("Соединение с БД закрыто.")

    logger_monitoring.info("Программа завершена.")
    sys.exit(0)

stop_event = threading.Event()
CONN = None

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_and_exit)


# ___________________________________
monitor_configs = [
    {
        'name': 'system',
        'monitor_class': SystemMonitor,
        'settings_file': '_settings_file/proc/system.txt',
    },
    {
        'name': 'cpu',
        'monitor_class': CPUsMonitor,
        'settings_file': '_settings_file/proc/cpu.txt',
    },
    # {
    #     'name': 'gpu',
    #     'monitor_class': GPUsMonitor,
    #     'settings_file': '_settings_file/proc/gpu.txt',
    # },
    {
        'name': 'lvol',
        'monitor_class': LvolsMonitor,
        'settings_file': '_settings_file/proc/lvol.txt',
    },
    {
        'name': 'disk',
        'monitor_class': DisksMonitor,
        'settings_file': '_settings_file/proc/disk.txt',
    },
    {
        'name': 'if',
        'monitor_class': EthPortMonitor,
        'settings_file': '_settings_file/proc/if.txt',
    },
    # {
    #     'name': 'f_a',
    #     'monitor_class': FreonA,
    #     'settings_file': '_settings_file/proc/f_a.txt',
    # },
    # {
    #     'name': 'f_b',
    #     'monitor_class': FreonB,
    #     'settings_file': '_settings_file/proc/f_b.txt',
    # },
    {
        'name': 'switch_dlink_dgs_1210_28x_me_0',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_dlink_dgs_1210_28x_me_0.txt',
        'ip': "10.70.0.250"
    },
    {
        'name': 'switch_mikrotik_crS312_4c_8xg_rm_0',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_mikrotik_crS312_4c_8xg_rm_0.txt',
        'ip': "192.168.0.201"
    },
    {
        'name': 'switch_mikrotik_crS312_4c_8xg_rm_1',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_mikrotik_crS312_4c_8xg_rm_1.txt',
        'ip': "192.168.0.202"
    },
    {
        'name': 'switch_mikrotik_crS312_4c_8xg_rm_2',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_mikrotik_crS312_4c_8xg_rm_2.txt',
        'ip': "192.168.0.203"
    },
    {
        'name': 'switch_mikrotik_crS312_4c_8xg_rm_3',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_mikrotik_crS312_4c_8xg_rm_3.txt',
        'ip': "192.168.0.204"
    },
    {
        'name': 'switch_mikrotik_crS312_4c_8xg_rm_4',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_mikrotik_crS312_4c_8xg_rm_4.txt',
        'ip': "192.168.0.205"
    },
    {
        'name': 'switch_mikrotik_crS312_4c_8xg_rm_5',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_mikrotik_crS312_4c_8xg_rm_5.txt',
        'ip': "192.168.0.206"
    },
    {
        'name': 'switch_dlink_dgs_1210_52_me_0',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_dlink_dgs_1210_52_me_0.txt',
        'ip': "10.90.90.91"
    },
    {
        'name': 'switch_dlink_dgs_1210_52_me_1',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_dlink_dgs_1210_52_me_1.txt',
        'ip': "10.90.90.92"
    },
    {
        'name': 'switch_dlink_dgs_1210_52_me_2',
        'monitor_class': Switch,
        'settings_file': '_settings_file/proc/switch_dlink_dgs_1210_52_me_2.txt',
        'ip': "10.90.90.93"
    },
]
# ___________________________________

# def periodic_update(object_monitor, interval):
#     while not stop_event.is_set():
#         time_start = time.time()
#         object_monitor.update()
#         time_update = time.time() - time_start
#         if time_update < interval:
#             time.sleep(interval - time_update)
#     logger_monitoring.info(f"Поток завершился {object_monitor.name}")

def periodic_update(object_monitor):
    while not stop_event.is_set():
        time_start = time.time()
        object_monitor.update()
        time_update = time.time() - time_start

        with object_monitor.interval_lock:
            current_interval = object_monitor.update_interval
        if time_update < current_interval:
            time.sleep(current_interval - time_update)

    logger_monitoring.info(f"Поток завершился {object_monitor.name}")

def main():
    try:
        global CONN
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
            ip_true = config.get('ip', None)
            if ip_true is None:
                monitor = monitor_class()
            else:
                monitor = monitor_class(ip_true)
            monitor.update_interval = 1
            monitor.interval_lock = threading.Lock()
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
            with monitor.interval_lock:
                monitor.update_interval = update_interval
            logger_monitoring.info(f" Для [{name}] получен interval update = {update_interval}")

            if update_interval is None:
                logger_monitoring.info(f" Для [{name}] нет потока!!")
                continue  # или throw

            thread = threading.Thread(
                target=periodic_update,
                args=(monitor, ),
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
                    metrics_polling_plan, item_all_interval = get_metrics_polling_plan()
                    logger_monitoring.info("Обновлено MIL")
                    # дописать код, который остановит потоки и создаст их заново

                    for name, data in monitors.items():
                        monitor = data['monitor']
                        new_interval = calculate_gcd_for_group(data['index_list'], item_all_interval)
                        if new_interval is not None:
                            with monitor.interval_lock:
                                monitor.update_interval = new_interval
                            logger_monitoring.info(f"Для [{name}] обновлён interval: {new_interval}")

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
            thread.join(timeout=5)
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
        sys.exit(1)
    # создание и проверка промежуточных файлов
    main()
