import psutil
import platform
import wmi
import subprocess



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


def get_cpu_time_irq():
    """Возвращает процент времени, которое центральный процессор тратит на обработку аппаратных прерываний"""
    try:
        if platform.system() == "Linux":
            return get_irq_time_linux()
        elif platform.system() == "Windows":
            return get_irq_time_windows()
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку аппаратных прерываний\": \n{e}")
        return -1


def get_irq_time_linux():
    """Возвращает процент времени на аппаратные прерывания для Linux"""
    with open("/proc/stat") as file:
        line = file.readline()
        fields = list(map(int, line.strip().split()[1:]))
        total_time = sum(fields)
        irq_time = fields[5]
        return (irq_time / total_time) * 100


def get_irq_time_windows():
    """Получает процент времени на аппаратные прерывания для Windows"""
    # try:
    #     c = wmi.WMI(namespace="root\\CIMV2")
    #     perf_data = c.Win32_PerfFormattedData_Counters_ProcessorInformation()
    #     for instance in perf_data:
    #         if instance.Name == "_Total":
    #             return float(instance.PercentInterruptTime)
    # except Exception as e:
    #     print(f"Ошибка при получении IRQ Time через WMI: {e}")
    #     return -1
    raise ValueError("На windows не реализован сбор параметра \"Процент времени CPU на обработку аппаратных прерываний\"")


def get_cpu_time_soft_irq():
    """Возвращает процент времени, которое центральный процессор тратит на обработку программных прерываний"""
    try:
        if platform.system() == "Linux":
            return get_softirq_time_linux()
        elif platform.system() == "Windows":
            return get_dpc_time_windows()
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку программных прерываний\": \n{e}")
        return -1


def get_softirq_time_linux():
    """Получение процента времени на программные прерывания для Linux"""
    with open("/proc/stat") as file:
        line = file.readline()
        fields = list(map(int, line.strip().split()[1:]))
        total_time = sum(fields)
        softirq_time = fields[7]
        return (softirq_time / total_time) * 100


def get_dpc_time_windows():
    """Получение процента времени для DPC (Deferred Procedure Calls) на Windows"""
    # try:
    #     c = wmi.WMI(namespace="root\\CIMV2")
    #     perf_data = c.Win32_PerfFormattedData_Counters_ProcessorInformation()
    #     for instance in perf_data:
    #         if instance.Name == "_Total":
    #             return float(instance.PercentDPCTime)
    # except Exception as e:
    #     print(f"Ошибка при получении DPC Time через WMI: {e}")
    #     return -1
    raise ValueError("На windows не реализован сбор параметра \"Процент времени CPU на обработку программных прерываний\"")


def get_cpu_time_idle():
    """Возвращает процент времени, которое центральный процессор простаивает"""
    try:
        psutil.cpu_times_percent(interval=1)
        return psutil.cpu_times_percent(interval=1).idle
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени простоя CPU\": \n{e}")
        return -1


def get_cpu_time_io_wait():
    """Возвращает процент времени, которое центральный процессор простаивает в ожидании результатов операций ввода/вывода"""
    try:
        if platform.system() == "Linux":
            return psutil.cpu_times_percent(interval=1).iowait
        elif platform.system() == "Windows":
            return get_cpu_time_io_wait_windows()
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени простоя CPU в ожидании результатов операций ввода/вывода\": \n{e}")
        return -1


def get_cpu_time_io_wait_windows():
    # try:
    #     c = wmi.WMI(namespace="root\\CIMV2")
    #     processor_data = c.Win32_PerfFormattedData_Counters_ProcessorInformation()
    #     for instance in processor_data:
    #         if instance.Name == "_Total":
    #             idle_time = float(instance.PercentIdleTime)
    #             processor_time = float(instance.PercentProcessorTime)
    #             # Формула: I/O Wait ~ Idle Time - Processor Time (приближение)
    #             io_wait_time = max(idle_time - processor_time, 0)
    #             return io_wait_time
    # except Exception as e:
    #     print(f"Ошибка при получении I/O Wait через WMI: {e}")
    #     return -1
    raise ValueError("На windows не реализован сбор параметра \"Процент времени простоя CPU в ожидании результатов операций ввода/вывода\"")


print(f"1. Физические ядра: {get_cpu_physical_core_count()}")
print(f"2. Логические ядра: {get_cpu_logical_core_count()}")
print(f"3. Загрузка логических процессоров: {get_cpu_usage_per_core()}")
print(f"4. Количество прерываний: {get_interrupt_count()}")
print(f"5. Процент времени процессора на пользовательские операции: {get_cpu_time_user()}")
print(f"6. Процент времени процессора на системные операции: {get_cpu_time_system()}")
print(f"7. Процент времени процессора на аппаратные прерывания: {get_cpu_time_irq()}")
print(f"8. Процент времени процессора на программные прерывания: {get_cpu_time_soft_irq()}")
print(f"9. Процент времени простоя процессора: {get_cpu_time_idle()}")
print(f"10. Процент времени процессора на ожидание результатов операций ввода-вывода: {get_cpu_time_io_wait()}")