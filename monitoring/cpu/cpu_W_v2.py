import time
import subprocess


def run_wmic(command):
    """Запускает команду wmic и возвращает результат в виде списка строк."""
    try:
        result = subprocess.check_output(command, shell=True, text=True, encoding="utf-8")
        return result.strip().split("\n")
    except Exception as e:
        return [f"Ошибка: {e}"]


def get_cpu_info():
    time_start = time.time()

    # Открываем файл для записи
    with open("2.txt", "w", encoding="utf-8") as f:
        # Получаем общую информацию о процессорах
        cpu_info = run_wmic(
            "wmic cpu get DeviceID, Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, CurrentClockSpeed, LoadPercentage /format:csv")
        time_get_cpus = time.time()

        f.write("Информация о процессорах:\n")
        f.write("-" * 50 + "\n")
        headers = []

        for i, line in enumerate(cpu_info):
            if i == 0:
                headers = line.split(",")
                continue
            values = line.split(",")
            if len(values) == len(headers):
                cpu_data = dict(zip(headers, values))
                f.write(f"Процессор: {cpu_data.get('DeviceID', 'Неизвестно')}\n")
                f.write(f"Имя: {cpu_data.get('Name', 'Неизвестно').strip()}\n")
                f.write(f"Физических ядер: {cpu_data.get('NumberOfCores', 'Неизвестно')}\n")
                f.write(f"Логических процессоров: {cpu_data.get('NumberOfLogicalProcessors', 'Неизвестно')}\n")
                f.write(f"Максимальная частота: {cpu_data.get('MaxClockSpeed', 'Неизвестно')} MHz\n")
                f.write(f"Текущая частота: {cpu_data.get('CurrentClockSpeed', 'Неизвестно')} MHz\n")
                f.write(f"Загрузка процессора: {cpu_data.get('LoadPercentage', 'Неизвестно')}%\n")
                f.write("-" * 50 + "\n")
        time_pars_cpus = time.time()

        cpu_info = run_wmic(
            "wmic cpu get CurrentClockSpeed, LoadPercentage /format:csv")
        time_get_cpus1 = time.time()

        f.write("Информация о процессорах:\n")
        f.write("-" * 50 + "\n")
        headers = []

        for i, line in enumerate(cpu_info):
            if i == 0:
                headers = line.split(",")
                continue
            values = line.split(",")
            if len(values) == len(headers):
                cpu_data = dict(zip(headers, values))
                f.write(f"Текущая частота: {cpu_data.get('CurrentClockSpeed', 'Неизвестно')} MHz\n")
                f.write(f"Загрузка процессора: {cpu_data.get('LoadPercentage', 'Неизвестно')}%\n")
                f.write("-" * 50 + "\n")
        time_pars_cpus1 = time.time()



        # Получаем статистику загрузки
        perf_info = run_wmic(
            "wmic path Win32_PerfFormattedData_PerfOS_Processor get Name, PercentProcessorTime, InterruptsPersec, PercentUserTime, PercentPrivilegedTime, PercentInterruptTime, PercentDPCTime, PercentIdleTime /format:csv")
        time_get_perf = time.time()

        headers = []
        for i, line in enumerate(perf_info):
            if i == 0:
                headers = line.split(",")
                continue
            values = line.split(",")
            if len(values) == len(headers):
                perf_data = dict(zip(headers, values))
                if perf_data.get("Name", "") and perf_data["Name"].isdigit():
                    f.write(f"Статистика для логического процессора {perf_data['Name']}\n")
                    f.write(f"  🔹 Загрузка процессора: {perf_data.get('PercentProcessorTime', 'Неизвестно')}%\n")
                    f.write(f"  🔹 Количество прерываний в секунду: {perf_data.get('InterruptsPersec', 'Неизвестно')}\n")
                    f.write(
                        f"  🔹 Процент времени в пользовательском режиме: {perf_data.get('PercentUserTime', 'Неизвестно')}%\n")
                    f.write(
                        f"  🔹 Процент времени в системном режиме: {perf_data.get('PercentPrivilegedTime', 'Неизвестно')}%\n")
                    f.write(
                        f"  🔹 Процент времени на аппаратные прерывания: {perf_data.get('PercentInterruptTime', 'Неизвестно')}%\n")
                    f.write(
                        f"  🔹 Процент времени на программные прерывания (DPC): {perf_data.get('PercentDPCTime', 'Неизвестно')}%\n")
                    f.write(f"  🔹 Процент времени простоя: {perf_data.get('PercentIdleTime', 'Неизвестно')}%\n")
                    f.write("-" * 50 + "\n")

        time_pars_perf = time.time()

        # Записываем временные метки выполнения
        f.write(f"время получения информации по процессорам     {time_get_cpus - time_start}\n")
        f.write(f"время парсинга информации по процессорам      {time_pars_cpus - time_get_cpus}\n")
        f.write(f"время получения информации по процессорам     {time_get_cpus1 - time_pars_cpus}\n")
        f.write(f"время парсинга информации по процессорам      {time_pars_cpus1 - time_get_cpus1}\n")
        f.write(f"время получения информации по потокам         {time_get_perf - time_pars_cpus1}\n")
        f.write(f"время парсинга информации по потокам          {time_pars_perf - time_get_perf}\n")


# Запуск функции
get_cpu_info()
