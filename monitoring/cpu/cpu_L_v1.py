import subprocess
import time
import re


def run_command(command):
    """Запускает команду в shell и возвращает результат."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True, shell=True)
    output, _ = process.communicate()
    return output


def get_cpu_info():
    """Получает информацию о процессоре через lscpu."""
    start_time = time.time()
    output = run_command("lscpu")
    cpu_info = {}

    for line in output.split("\n"):
        parts = line.split(":")
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            if key == "Model name":
                cpu_info["Name"] = value
            elif key == "CPU MHz":
                cpu_info["CurrentClockSpeed"] = float(value)
            elif key == "CPU(s)":
                cpu_info["NumberOfLogicalProcessors"] = int(value)
            elif key == "Core(s) per socket":
                cpu_info["NumberOfCores"] = int(value)

    print("Время сбора параметров CPU:", time.time() - start_time)
    return [{"Type": "CPU", **cpu_info}]


def get_logical_core_info():
    """Получает загрузку логических ядер через mpstat."""
    start_time = time.time()
    output = run_command("mpstat -P ALL")
    logical_cores = []

    lines = output.split("\n")
    for line in lines:
        print(line)
        parts = re.split(r'\s+', line.strip())
        if len(parts) > 10 and parts[1].isdigit():
            logical_cores.append({
                "Type": "logical core",
                "CoreID": int(parts[1]),
                "PercentIdleTime": float(parts[-1].replace(",", ".")),
                "PercentProcessorTime": 100.0 - float(parts[-1].replace(",", ".")),
            })

    print("Время сбора параметров логических ядер:", time.time() - start_time)
    return logical_cores


def save_to_file(data, filename="cpu_l.txt"):
    """Сохраняет данные в файл."""
    with open(filename, "w") as file:
        for item in data:
            file.write(str(item) + "\n")


def all_cpu():
    """Получает информацию о CPU и логических ядрах последовательно."""
    start_time = time.time()

    cpu_result = get_cpu_info()
    logical_core_result = get_logical_core_info()

    print("Полное время сбора параметров CPU:", time.time() - start_time)
    return cpu_result + logical_core_result


if __name__ == "__main__":
    results = all_cpu()
    save_to_file(results)
