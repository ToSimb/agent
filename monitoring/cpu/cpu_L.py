from cpu_WL import (get_cpu_logical_core_count, get_cpu_physical_core_count)
import subprocess
import re

def parse_proc_stat():
    """Собирает статистику CPU из /proc/stat"""
    cpu_data = {}
    try:
        with open("/proc/stat", "r") as f:
            lines = f.readlines()
        cpu_loads = []
        for line in lines[1:]:
            if line.startswith("intr"):
                cpu_data["interrupts"] = int(line.split()[1])
            if line.startswith("cpu"):
                cpu_fields = line.split()
                cpu_loads.append(100 - (int(cpu_fields[4]) / sum(map(int, cpu_fields[1:])) * 100))
        cpu_data["cpu_loads"] = cpu_loads
        return cpu_data
    except Exception as e:
        print(f"Ошибка при обработке /proc/stat: {e}")
        return None


def get_cpu_usage():
    """ Получает процент загрузки CPU с помощью команды top. """
    try:
        result = subprocess.run(['top', '-bn1'], stdout=subprocess.PIPE, text=True)
        output = result.stdout
        cpu_line_pattern = re.compile(r'^%Cpu\(s\):\s*(?P<user>\d+\.\d+)\s*u,\s*'                                     
                                      r'(?P<system>\d+\.\d+)\s*s,\s*'
                                      r'(?P<idle>\d+\.\d+)\s*i,\s*'
                                      r'(?P<io>\d+\.\d+)\s*wa,\s*'
                                      r'(?P<hi>\d+\.\d+)\s*hi,\s*'
                                      r'(?P<si>\d+\.\d+)\s*si,\s*', re.MULTILINE)

        match = cpu_line_pattern.search(output)
        if match:
            cpu_usage = {
                "user": float(match.group("user")),  # Процент времени, потраченного на выполнение пользовательских процессов
                "system": float(match.group("system")),  # Процент времени, потраченного на выполнение системных процессов
                "idle": float(match.group("idle")),  # Процент времени простоя
                "io": float(match.group("io")),  # Процент времени, потраченного на ожидание ввода-вывода (I/O)
                "hi": float(match.group("hi")),  # Процент времени обработки аппаратных прерываний
                "si": float(match.group("si")),  # Процент времени обработки программных прерываний
            }
            return cpu_usage
        else:
            print("Не удалось найти данные о загрузке CPU.")
            return {}

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}


stat = {**parse_proc_stat(), **get_cpu_usage}
stat['cpu_logical_core_count'] = get_cpu_logical_core_count()
stat['cpu_physical_core_count'] = get_cpu_physical_core_count()

print(stat)