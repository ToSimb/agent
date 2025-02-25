import psutil
from cpu_WL import (get_cpu_time_idle, get_cpu_time_user, get_cpu_time_system, get_cpu_usage_per_core,
                    get_cpu_logical_core_count, get_cpu_physical_core_count, get_interrupt_count)

def get_cpu_time_io_wait():
    """Возвращает процент времени, которое центральный процессор простаивает в ожидании результатов операций ввода/вывода"""
    try:
        return psutil.cpu_times_percent(interval=1).iowait
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени простоя CPU в ожидании результатов операций ввода/вывода\": \n{e}")
        return -1


def get_cpu_time_irq():
    """Возвращает процент времени, которое центральный процессор тратит на обработку аппаратных прерываний"""
    try:
        with open("/proc/stat") as file:
            line = file.readline()
            fields = list(map(int, line.strip().split()[1:]))
            if len(fields) < 6:
                raise ValueError("Недостаточно данных в /proc/stat")            
            total_time = sum(fields)
            irq_time = fields[5]
            return (irq_time / total_time) * 100 if total_time > 0 else 0.0
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку аппаратных прерываний\": \n{e}")
        return -1


def get_cpu_time_soft_irq():
    """Возвращает процент времени, которое центральный процессор тратит на обработку программных прерываний"""
    try:
        with open("/proc/stat") as file:
            line = file.readline()
            fields = list(map(int, line.strip().split()[1:]))
            if len(fields) < 7:
                raise ValueError("Недостаточно данных в /proc/stat")
            total_time = sum(fields)
            softirq_time = fields[6]
            return (softirq_time / total_time) * 100 if total_time > 0 else 0.0
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени CPU на обработку программных прерываний\": \n{e}")
        return -1


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