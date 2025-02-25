import psutil

def get_cpu_physical_core_count():
    """Возвращает количество физических ядер"""
    try:
        return psutil.cpu_count(logical=False)
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество физических ядер\": \n{e}")
        return -1


def get_cpu_logical_core_count():
    """Возвращает количество логических ядер"""
    try:
        return psutil.cpu_count(logical=True)
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество логических ядер\": \n{e}")
        return -1


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