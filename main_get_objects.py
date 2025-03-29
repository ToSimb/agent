from monitoring.service import (measure_execution_time,
                                save_file)
from monitoring.cpu.cpu import CPUsMonitor
from monitoring.gpu_nvidia.gpu_nvidia import GPUsMonitor
from monitoring.system.system import SystemMonitor

from logger.logger_monitoring import logger_monitoring


def cpu_start():
    cpu_prime, time_cpu_init = measure_execution_time(CPUsMonitor)
    _, time_cpu_update = measure_execution_time(cpu_prime.update)
    cpu_objects_descr, time_cpu_get_obj = measure_execution_time(cpu_prime.get_objects_description)

    cpu_file_name = 'monitoring/settings_file/cpu_raw.txt'
    if save_file(cpu_file_name, cpu_objects_descr):
        logger_monitoring.info(f"Файл {cpu_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {cpu_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'CPU initialization time:   {time_cpu_init}')
    logger_monitoring.info(f'CPU update time:           {time_cpu_update}')
    logger_monitoring.info(f'CPU get object time:       {time_cpu_get_obj}')
    logger_monitoring.info(" * " * 10)

    aa = cpu_prime.get_all()
    for aaa in aa:
        print(aaa)

def gpu_start():
    gpu_prime, time_gpu_init = measure_execution_time(GPUsMonitor)
    _, time_gpu_update = measure_execution_time(gpu_prime.update)
    gpu_objects_descr, time_gpu_get_obj = measure_execution_time(gpu_prime.get_objects_description)

    gpu_file_name = 'monitoring/settings_file/gpu_raw.txt'
    if save_file(gpu_file_name, gpu_objects_descr):
        logger_monitoring.info(f"Файл {gpu_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {gpu_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'GPU initialization time:   {time_gpu_init}')
    logger_monitoring.info(f'GPU update time:           {time_gpu_update}')
    logger_monitoring.info(f'GPU get object time:       {time_gpu_get_obj}')
    logger_monitoring.info(" * " * 10)
    aa = gpu_prime.get_all()
    print(aa)

def system_start():
    system_prime, time_system_init = measure_execution_time(SystemMonitor)
    _, time_system_update = measure_execution_time(system_prime.update)
    system_objects_descr, time_system_get_obj = measure_execution_time(system_prime.get_objects_description)

    system_file_name = 'monitoring/settings_file/system_raw.txt'
    if save_file(system_file_name, system_objects_descr):
        logger_monitoring.info(f"Файл {system_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {system_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'SYSTEM initialization time:   {time_system_init}')
    logger_monitoring.info(f'SYSTEM update time:           {time_system_update}')
    logger_monitoring.info(f'SYSTEM get object time:       {time_system_get_obj}')
    logger_monitoring.info(" * " * 10)
    aa = system_prime.get_all()
    print(aa)

def main():
    logger_monitoring.info("- - -"*10)
    cpu_start()
    logger_monitoring.info("- - -"*10)
    gpu_start()
    logger_monitoring.info("- - -"*10)
    system_start()
    logger_monitoring.info("- - -"*10)

if __name__ == "__main__":
    main()