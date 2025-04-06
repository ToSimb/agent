from monitoring.service import (measure_execution_time,
                                save_file,
                                save_file_data)
from monitoring.cpu.cpu import CPUsMonitor
from monitoring.gpu_nvidia.gpu_nvidia import GPUsMonitor
from monitoring.system.system import SystemMonitor
from monitoring.eth_port.eth_port import EthPortMonitor
from monitoring.lvol.lvol import LvolsMonitor
from monitoring.freon_a.freon_a import FreonA
from monitoring.freon_b.freon_b import FreonB

from logger.logger_monitoring import logger_monitoring


def monitor_start(monitor_class, tag):
    monitor_instance, time_init = measure_execution_time(monitor_class)
    _, time_update = measure_execution_time(monitor_instance.update)
    objects_descr, time_get_obj = measure_execution_time(monitor_instance.get_objects_description)
    data, time_data = measure_execution_time(monitor_instance.get_all)

    settings_file = f'monitoring/_settings_file/{tag}_raw.txt'
    if save_file(settings_file, objects_descr):
        logger_monitoring.info(f"Файл {settings_file} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {settings_file}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'{tag.upper()} initialization time:   {time_init}')
    logger_monitoring.info(f'{tag.upper()} update time:           {time_update}')
    logger_monitoring.info(f'{tag.upper()} get object time:       {time_get_obj}')
    logger_monitoring.info(f'{tag.upper()} get data time:         {time_data}')
    logger_monitoring.info(" * " * 10)

    data_file = f'monitoring/_params_all_objs/{tag}_data.txt'
    save_file_data(data_file, data)

def main():
    logger_monitoring.info("- - -" * 10)
    monitors = [
        (CPUsMonitor, 'cpu'),
        (GPUsMonitor, 'gpu'),
        (SystemMonitor, 'system'),
        (LvolsMonitor, 'lvol'),
        (EthPortMonitor, 'eth_port'),
        # (FreonA, 'f_a'),
        # (FreonB, 'f_b')
    ]
    for monitor_class, tag in monitors:
        monitor_start(monitor_class, tag)
        logger_monitoring.info("- - -" * 10)


if __name__ == "__main__":
    main()