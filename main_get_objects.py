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


def cpu_start():
    cpu_prime, time_cpu_init = measure_execution_time(CPUsMonitor)
    _, time_cpu_update = measure_execution_time(cpu_prime.update)
    cpu_objects_descr, time_cpu_get_obj = measure_execution_time(cpu_prime.get_objects_description)
    cpu_data, time_data = measure_execution_time(cpu_prime.get_all)

    cpu_file_name = 'monitoring/settings_file/cpu_raw.txt'
    if save_file(cpu_file_name, cpu_objects_descr):
        logger_monitoring.info(f"Файл {cpu_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {cpu_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'CPU initialization time:   {time_cpu_init}')
    logger_monitoring.info(f'CPU update time:           {time_cpu_update}')
    logger_monitoring.info(f'CPU get object time:       {time_cpu_get_obj}')
    logger_monitoring.info(f'CPU get date time:         {time_data}')
    logger_monitoring.info(" * " * 10)

    file_date = 'monitoring/settings_file/cpu_date.txt'
    save_file_data(file_date, cpu_data)


def gpu_start():
    gpu_prime, time_gpu_init = measure_execution_time(GPUsMonitor)
    _, time_gpu_update = measure_execution_time(gpu_prime.update)
    gpu_objects_descr, time_gpu_get_obj = measure_execution_time(gpu_prime.get_objects_description)
    gpu_data, time_data = measure_execution_time(gpu_prime.get_all)

    gpu_file_name = 'monitoring/settings_file/gpu_raw.txt'
    if save_file(gpu_file_name, gpu_objects_descr):
        logger_monitoring.info(f"Файл {gpu_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {gpu_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'GPU initialization time:   {time_gpu_init}')
    logger_monitoring.info(f'GPU update time:           {time_gpu_update}')
    logger_monitoring.info(f'GPU get object time:       {time_gpu_get_obj}')
    logger_monitoring.info(f'GPU get date time:         {time_data}')
    logger_monitoring.info(" * " * 10)

    file_date = 'monitoring/settings_file/gpu_date.txt'
    save_file_data(file_date, gpu_data)

def system_start():
    system_prime, time_system_init = measure_execution_time(SystemMonitor)
    _, time_system_update = measure_execution_time(system_prime.update)
    system_objects_descr, time_system_get_obj = measure_execution_time(system_prime.get_objects_description)
    system_data, time_data = measure_execution_time(system_prime.get_all)

    system_file_name = 'monitoring/settings_file/system_raw.txt'
    if save_file(system_file_name, system_objects_descr):
        logger_monitoring.info(f"Файл {system_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {system_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'SYSTEM initialization time:   {time_system_init}')
    logger_monitoring.info(f'SYSTEM update time:           {time_system_update}')
    logger_monitoring.info(f'SYSTEM get object time:       {time_system_get_obj}')
    logger_monitoring.info(f'SYSTEM get date time:         {time_data}')
    logger_monitoring.info(" * " * 10)

    file_date = 'monitoring/settings_file/system_date.txt'
    save_file_data(file_date, system_data)

def lvol_start():
    lvol_prime, time_lvol_init = measure_execution_time(LvolsMonitor)
    _, time_lvol_update = measure_execution_time(lvol_prime.update)
    lvol_objects_descr, time_lvol_get_obj = measure_execution_time(lvol_prime.get_objects_description)
    lvol_data, time_data = measure_execution_time(lvol_prime.get_all)

    lvol_file_name = 'monitoring/settings_file/lvol_raw.txt'
    if save_file(lvol_file_name, lvol_objects_descr):
        logger_monitoring.info(f"Файл {lvol_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {lvol_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'LVOL initialization time:   {time_lvol_init}')
    logger_monitoring.info(f'LVOL update time:           {time_lvol_update}')
    logger_monitoring.info(f'LVOL get object time:       {time_lvol_get_obj}')
    logger_monitoring.info(f'LVOL get date time:         {time_data}')
    logger_monitoring.info(" * " * 10)

    file_data = 'monitoring/settings_file/lvol_data.txt'
    save_file_data(file_data, lvol_data)

def eth_port_start():
    eth_port_prime, time_eth_port_init = measure_execution_time(EthPortMonitor)
    _, time_eth_port_update = measure_execution_time(eth_port_prime.update)
    eth_port_objects_descr, time_eth_port_get_obj = measure_execution_time(eth_port_prime.get_objects_description)
    eth_port_data, time_data = measure_execution_time(eth_port_prime.get_all)

    eth_port_file_name = 'monitoring/settings_file/eth_port_raw.txt'
    if save_file(eth_port_file_name, eth_port_objects_descr):
        logger_monitoring.info(f"Файл {eth_port_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {eth_port_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'ETH_PORT initialization time:   {time_eth_port_init}')
    logger_monitoring.info(f'ETH_PORT update time:           {time_eth_port_update}')
    logger_monitoring.info(f'ETH_PORT get object time:       {time_eth_port_get_obj}')
    logger_monitoring.info(f'ETH_PORT get date time:         {time_data}')
    logger_monitoring.info(" * " * 10)

    file_date = 'monitoring/settings_file/eth_port_data.txt'
    save_file_data(file_date, eth_port_data)

def f_a_start():
    f_a_prime, time_f_a_init = measure_execution_time(FreonA, "monitoring/freon_a/freon_dict.txt")
    _, time_f_a_update = measure_execution_time(f_a_prime.update)
    f_a_objects_descr, time_f_a_get_obj = measure_execution_time(f_a_prime.get_objects_description)
    fa, time_f_a_get_params = measure_execution_time(f_a_prime.get_all)


    f_a_file_name = 'monitoring/settings_file/f_a_raw.txt'
    if save_file(f_a_file_name, f_a_objects_descr):
        logger_monitoring.info(f"Файл {f_a_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {f_a_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'F-A initialization time:   {time_f_a_init}')
    logger_monitoring.info(f'F-A update time:           {time_f_a_update}')
    logger_monitoring.info(f'F-A get object time:       {time_f_a_get_obj}')
    logger_monitoring.info(f'F-A get params time:       {time_f_a_get_params}')
    logger_monitoring.info(" * " * 10)

    file_date = 'monitoring/settings_file/f_a_data.txt'
    save_file_data(file_date, fa)

def f_b_start():
    f_b_prime, time_f_b_init = measure_execution_time(FreonB, "monitoring/freon_b/freon_dict.txt")
    _, time_f_b_update = measure_execution_time(f_b_prime.update)
    f_b_objects_descr, time_f_b_get_obj = measure_execution_time(f_b_prime.get_objects_description)
    fb, time_f_b_get_params = measure_execution_time(f_b_prime.get_all)


    f_b_file_name = 'monitoring/settings_file/f_b_raw.txt'
    if save_file(f_b_file_name, f_b_objects_descr):
        logger_monitoring.info(f"Файл {f_b_file_name} создан, требуется его заполнение!")
    else:
        logger_monitoring.info(f"Уже имеется файл: {f_b_file_name}")

    logger_monitoring.info(" * " * 10)
    logger_monitoring.info(f'F-B initialization time:   {time_f_b_init}')
    logger_monitoring.info(f'F-B update time:           {time_f_b_update}')
    logger_monitoring.info(f'F-B get object time:       {time_f_b_get_obj}')
    logger_monitoring.info(f'F-B get params time:       {time_f_b_get_params}')
    logger_monitoring.info(" * " * 10)

    file_date = 'monitoring/settings_file/f_a_data.txt'
    save_file_data(file_date, fb)

def main():
    logger_monitoring.info("- - -"*10)
    cpu_start()
    logger_monitoring.info("- - -"*10)
    gpu_start()
    logger_monitoring.info("- - -"*10)
    system_start()
    logger_monitoring.info("- - -"*10)
    lvol_start()
    logger_monitoring.info("- - -"*10)
    eth_port_start()
    logger_monitoring.info("- - -"*10)
    # f_a_start()
    # logger_monitoring.info("- - -"*10)
    # f_b_start()
    # logger_monitoring.info("- - -"*10)


if __name__ == "__main__":
    main()