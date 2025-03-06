import subprocess
import time
import re
import threading


def run_wmic_query(query):
    """Запускает WMIC команду и возвращает результат"""
    process = subprocess.Popen(query, stdout=subprocess.PIPE, text=True)
    output, _ = process.communicate()
    return output


def parse_wmic_output(output, expected_columns):
    """Оптимизированный парсинг WMIC вывода"""
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return []

    data_list = []
    for line in lines[1:]:  # Пропускаем заголовок
        parts = re.split(r',|\s{2,}', line.strip())
        if len(parts) >= expected_columns:
            data_list.append(parts)
    return data_list


def get_cpu_info():
    """Получает информацию о процессоре"""
    start_time = time.time()
    query = ('wmic cpu get Name, CurrentVoltage, LoadPercentage, '
             'NumberOfCores, NumberOfLogicalProcessors, CurrentClockSpeed')
    output = run_wmic_query(query)
    cpu_data = parse_wmic_output(output, 5)
    print("Время сбора параметров CPU:", time.time() - start_time)
    return [
        {
            "Type": "CPU",
            "Name": parts[3].strip(),
            "CurrentClockSpeed": int(parts[0]) if parts[0].isdigit() else -1,
            "CurrentVoltage": int(parts[1]) if parts[1].isdigit() else -1,
            "LoadPercentage": int(parts[2]) if parts[2].isdigit() else -1,
            "NumberOfCores": int(parts[4]) if parts[4].isdigit() else -1,
            "NumberOfLogicalProcessors": int(parts[5]) if parts[5].isdigit() else -1
        }
        for parts in cpu_data
    ]


def get_logical_core_info():
    """Получает информацию о логических ядрах"""
    start_time = time.time()
    query = ('wmic path Win32_PerfFormattedData_Counters_ProcessorInformation '
             'get Name, PercentProcessorTime, PercentInterruptTime, PercentDPCTime, '
             'PercentIdleTime, PercentUserTime, PercentPrivilegedTime, InterruptsPersec')
    output = run_wmic_query(query)
    logical_data = parse_wmic_output(output, 8)
    print("Время сбора параметров логических ядер:", time.time() - start_time)
    return [
        {
            "Type": "logical core",
            "ProcessorID": int(parts[1]) if parts[1].isdigit() else -1,
            "CoreID": int(parts[2]) if parts[2].isdigit() else -1,
            "PercentProcessorTime": int(parts[7]) if parts[7].isdigit() else -1,
            "PercentInterruptTime": int(parts[5]) if parts[5].isdigit() else -1,
            "PercentDPCTime": int(parts[3]) if parts[3].isdigit() else -1,
            "PercentIdleTime": int(parts[4]) if parts[4].isdigit() else -1,
            "PercentUserTime": int(parts[8]) if parts[8].isdigit() else -1,
            "PercentPrivilegedTime": int(parts[6]) if parts[6].isdigit() else -1,
            "InterruptsPersec": int(parts[0]) if parts[0].isdigit() else -1
        }
        for parts in logical_data if "_Total" not in parts
    ]


def save_to_file(data, filename="cpu_w.txt"):
    """Сохраняет данные в файл"""
    with open(filename, "w") as file:
        for item in data:
            file.write(str(item) + "\n")


def all_cpu():
    """Получает информацию о CPU и логических ядрах параллельно"""
    start_time = time.time()

    cpu_result = []
    logical_core_result = []

    # Запускаем два потока для ускорения
    cpu_thread = threading.Thread(target=lambda: cpu_result.extend(get_cpu_info()))
    logical_core_thread = threading.Thread(target=lambda: logical_core_result.extend(get_logical_core_info()))

    cpu_thread.start()
    logical_core_thread.start()
    cpu_thread.join()
    logical_core_thread.join()

    print("Полное время сбора параметров CPU:", time.time() - start_time)
    return cpu_result + logical_core_result


if __name__ == "__main__":
    results = all_cpu()
    # Сохраняем в файл
    save_to_file(results)
