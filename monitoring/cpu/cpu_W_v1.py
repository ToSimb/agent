import time
import wmi

def safe_getattr(obj, attr, default=-1):
    """Безопасное получение атрибута объекта. Если атрибут недоступен — возвращает default."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default

def get_cpu_info():
    time_start = time.time()
    c = wmi.WMI()
    time_get_c = time.time()

    # Открываем файл для записи
    with open("cpu1.txt", "w", encoding="utf-8") as f:
        # Получаем данные по каждому процессору
        cpus = c.Win32_Processor()
        time_get_cpus = time.time()
        f.write(f"Общее количество процессоров в системе: {len(cpus)}\n" + "-" * 50 + "\n")

        for cpu in cpus:
            cpu_id = safe_getattr(cpu, "DeviceID")
            f.write(f"Процессор: {cpu_id}\n")
            f.write(f"Имя: {safe_getattr(cpu, 'Name', 'Неизвестно').strip()}\n")
            f.write(f"Физических ядер: {safe_getattr(cpu, 'NumberOfCores')}\n")
            f.write(f"Логических процессоров: {safe_getattr(cpu, 'NumberOfLogicalProcessors')}\n")
            f.write(f"Максимальная частота: {safe_getattr(cpu, 'MaxClockSpeed')} MHz\n")
            f.write(f"Текущая частота: {safe_getattr(cpu, 'CurrentClockSpeed')} MHz\n")
            f.write(f"Загрузка процессора: {safe_getattr(cpu, 'LoadPercentage')}%\n")
            f.write("-" * 50 + "\n")
        time_pars_cpus = time.time()

        # Получаем статистику загрузки и прерываний по каждому логическому процессору
        perf_counters = c.Win32_PerfFormattedData_PerfOS_Processor()
        time_get_perf = time.time()
        for perf in perf_counters:
            if perf.Name.isdigit():  # Имя должно быть "0", "1" и т. д. (номер логического процессора)
                f.write(f"Статистика для логического процессора {perf.Name}\n")
                f.write(f"  🔹 Загрузка процессора: {safe_getattr(perf, 'PercentProcessorTime')}%\n")
                f.write(f"  🔹 Количество прерываний в секунду: {safe_getattr(perf, 'InterruptsPerSec')}\n")
                f.write(f"  🔹 Процент времени в пользовательском режиме: {safe_getattr(perf, 'PercentUserTime')}%\n")
                f.write(f"  🔹 Процент времени в системном режиме: {safe_getattr(perf, 'PercentPrivilegedTime')}%\n")
                f.write(f"  🔹 Процент времени на аппаратные прерывания: {safe_getattr(perf, 'PercentInterruptTime')}%\n")
                f.write(f"  🔹 Процент времени на программные прерывания (DPC): {safe_getattr(perf, 'PercentDPCTime')}%\n")
                f.write(f"  🔹 Процент времени простоя: {safe_getattr(perf, 'PercentIdleTime')}%\n")
                f.write("-" * 50 + "\n")
        time_pars_perf = time.time()


        # Записываем временные метки выполнения
        f.write(f"время объявления класса                       {time_get_c - time_start}\n")
        f.write(f"время получения информации по процессорам     {time_get_cpus - time_get_c}\n")
        f.write(f"время парсинга информации по процессорам      {time_pars_cpus - time_get_cpus}\n")
        f.write(f"время получения информации по потокам         {time_get_perf - time_pars_cpus}\n")
        f.write(f"время парсинга информации по потокам          {time_pars_perf - time_get_perf}\n")

# Запуск функции
get_cpu_info()
