from cpu_WL import (get_cpu_time_idle, get_cpu_time_user, get_cpu_time_system, get_cpu_usage_per_core,
                    get_cpu_logical_core_count, get_cpu_physical_core_count, get_interrupt_count)


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