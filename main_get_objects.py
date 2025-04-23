from monitoring.service import (measure_execution_time,
                                open_file,
                                save_file_data)
from monitoring.cpu.cpu import CPUsMonitor
from monitoring.gpu_nvidia.gpu_nvidia import GPUsMonitor
from monitoring.system.system import SystemMonitor
from monitoring.eth_port.eth_port import EthPortMonitor
from monitoring.lvol.lvol import LvolsMonitor
from monitoring.disk.disk import DisksMonitor
from monitoring.disk_lite.disk_lite import DisksLiteMonitor
# from monitoring.switch.switch import Switch
from monitoring.freon_a.freon_a import FreonA
from monitoring.freon_b.freon_b import FreonB

from logger.logger_monitoring import logger_monitoring

PEREDELAY = []

def compare_interface_keys(tag, dict1, dict2):
    """
    Сравнивает ключи двух словарей (например, сетевых интерфейсов).
    Выводит различия и возвращает True, если ключи одинаковые, иначе False.
    """
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    if keys1 != keys2:
        logger_monitoring.error(f"Списки интерфейсов по '{tag}' отличаются - ВНИМАНИЕ")
        logger_monitoring.error(f"Только в первом(old): {keys1 - keys2}")
        logger_monitoring.error(f"Только во втором:(new) {keys2 - keys1}")
        return True
    else:
        logger_monitoring.info(f"Интерфейсы по '{tag}' совпадают.")
        return False

def monitor_start(monitor_class, tag, ip_addr = None):
    global PEREDELAY
    if ip_addr is None:
        monitor_instance, time_init = measure_execution_time(monitor_class)
    else:
        time_init = 0
        monitor_instance = monitor_class(ip_addr)
    _, time_update = measure_execution_time(monitor_instance.update)
    objects_descr, time_get_obj = measure_execution_time(monitor_instance.get_objects_description)
    data, time_data = measure_execution_time(monitor_instance.get_all)

    settings_file = f'_settings_file/raw/{tag}.txt'

    objects_key_old = open_file(settings_file)
    objects_key = {}
    for index_cpu in objects_descr:
        objects_key[objects_descr[index_cpu]] = None

    if objects_key_old is not None:
        if compare_interface_keys(tag, objects_key_old, objects_key):
            PEREDELAY.append(tag)
    else:
        PEREDELAY.append(tag)
    save_file_data(settings_file, objects_key)
    logger_monitoring.info( "\n" + " * " * 10 + "\n"
                            f"  {tag.upper()} timings:\n"
                            f"      Initialization time:   {time_init}\n"
                            f"      Update time:           {time_update}\n"
                            f"      Get object time:       {time_get_obj}\n"
                            f"      Get data time:         {time_data}\n"
                            + " * " * 10)

    data_file = f'_settings_file/data/{tag}.txt'
    save_file_data(data_file, data)


def main():
    logger_monitoring.info("- - -" * 10)
    monitors = [
        # (CPUsMonitor, 'cpu'),
        # (GPUsMonitor, 'gpu'),
        # (SystemMonitor, 'system'),
        # (LvolsMonitor, 'lvol'),
        (DisksMonitor, 'disk'),
        (DisksLiteMonitor, 'disk_lite'),
        # (EthPortMonitor, 'if'),
        (FreonA, 'f_a'),
        # (FreonB, 'f_b'),
        # (Switch, 'switch_dlink_dgs_1210_28x_me_0', '10.70.0.250'), # Это из схемы
        #
        # (Switch, 'switch_mikrotik_crS312_4c_8xg_rm_0', '192.168.0.201'), # Это из схемы
        # (Switch, 'switch_mikrotik_crS312_4c_8xg_rm_1', '192.168.0.202'),  # Это из схемы
        # (Switch, 'switch_mikrotik_crS312_4c_8xg_rm_2', '192.168.0.203'),  # Это из схемы
        # (Switch, 'switch_mikrotik_crS312_4c_8xg_rm_3', '192.168.0.204'),  # Это из схемы
        # (Switch, 'switch_mikrotik_crS312_4c_8xg_rm_4', '192.168.0.205'),  # Это из схемы
        # (Switch, 'switch_mikrotik_crS312_4c_8xg_rm_5', '192.168.0.206'),  # Это из схемы
        #
        # (Switch, 'switch_dlink_dgs_1210_52_me_0', '10.90.90.91'),  # Это из схемы
        # (Switch, 'switch_dlink_dgs_1210_52_me_1', '10.90.90.92'),  # Это из схемы
        # (Switch, 'switch_dlink_dgs_1210_52_me_2', '10.90.90.93'),  # Это из схемы
    ]
    for line in monitors:
        if len(line) == 2:
            monitor_class, tag = line
            monitor_start(monitor_class, tag)
        elif len(line) == 3:
            monitor_class, tag, ip_addr = line
            monitor_start(monitor_class, tag, ip_addr)
    logger_monitoring.info(f"Обрати внимание на {PEREDELAY}")


if __name__ == "__main__":
    main()
