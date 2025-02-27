from cpu_WL import (get_cpu_logical_core_count, get_cpu_physical_core_count)
import psutil


def get_cpu_usage_per_core():
    """Возвращает загрузку каждого логического процессора"""
    try:
        return psutil.cpu_percent(interval=1, percpu=True)
    except Exception as e:
        print(f"Ошибка сбора параметра \"Загрузка логических процессоров\": \n{e}")
        return -1


def get_interrupt_count():
    """Возвращает количество прерываний в системе"""
    try:
        return psutil.cpu_stats().interrupts
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество прерываний в системе\": \n{e}")
        return -1


def get_cpu_time_user():
    """Возвращает процент времени, которое центральный процессор тратит на обработку пользовательских операций"""
    try:
        return psutil.cpu_times_percent(interval=1).user
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку пользовательских операций\": \n{e}")
        return -1


def get_cpu_time_system():
    """Возвращает процент времени, которое центральный процессор тратит на обработку системных операций"""
    try:
        return psutil.cpu_times_percent(interval=1).system
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку системных операций\": \n{e}")
        return -1


def get_cpu_time_idle():
    """Возвращает процент времени, которое центральный процессор простаивает"""
    try:
        psutil.cpu_times_percent(interval=1)
        return psutil.cpu_times_percent(interval=1).idle
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени простоя CPU\": \n{e}")
        return -1


def get_cpu_time_irq():
    """Возвращает процент времени, которое центральный процессор тратит на обработку аппаратных прерываний"""
    try:
        pass
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку аппаратных прерываний\": \n{e}")
        return -1


def get_cpu_time_soft_irq():
    """Возвращает процент времени, которое центральный процессор тратит на обработку программных прерываний"""
    try:
        pass
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку программных прерываний\": \n{e}")
        return -1


def get_cpu_time_io_wait():
    """Возвращает процент времени, которое центральный процессор простаивает в ожидании результатов операций ввода/вывода"""
    try:
        pass
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени простоя CPU в ожидании результатов операций ввода/вывода\": \n{e}")
        return -1


def all_cpu():
    data = {
        "physical_core": get_cpu_physical_core_count(),
        "logical_core": get_cpu_logical_core_count(),
        "usage_per_core": get_cpu_usage_per_core(),
        "interrupt_count": get_interrupt_count(),
        "cpu_user_proc": get_cpu_time_user(),
        "cpu_system_proc": get_cpu_time_system(),
        "cpu_irq_proc": get_cpu_time_irq(),
        "cpu_soft_irq_proc": get_cpu_time_soft_irq(),
        "cpu_idle_proc": get_cpu_time_idle(),
        "cpu_io_wait_proc": get_cpu_time_io_wait()
    }
    return data
