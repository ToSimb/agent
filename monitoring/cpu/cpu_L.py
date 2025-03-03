from .cpu_WL import (get_cpu_logical_core_count, get_cpu_physical_core_count)
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
    """
    Получает процент загрузки CPU с помощью команды top.
    """
    try:
        # Запускаем команду top в режиме.batch (без интерактивного режима) и получаем один снимок данных
        result = subprocess.run(['top', '-bn1'], stdout=subprocess.PIPE, text=True)
        output = result.stdout

        # Обновленное регулярное выражение для поиска строки с загрузкой CPU
        cpu_line_pattern = re.compile(
            r'^%Cpu\(s\):\s*'  # Начало строки "%Cpu(s):"
            r'(?P<user>\d+\.\d+)'  # Процент времени пользовательских процессов
            r'\s*us,\s*'  # Слово "us" и пробелы
            r'(?P<system>\d+\.\d+)'  # Процент времени системных процессов
            r'\s*sy,\s*'  # Слово "sy" и пробелы
            r'(?P<nice>\d+\.\d+)'  # Процент времени процессов с измененным приоритетом
            r'\s*ni,\s*'  # Слово "ni" и пробелы
            r'(?P<idle>\d+\.\d+)'  # Процент времени простоя
            r'\s*id,\s*'  # Слово "id" и пробелы
            r'(?P<io>\d+\.\d+)'  # Процент времени ожидания I/O
            r'\s*wa,\s*'  # Слово "wa" и пробелы
            r'(?P<hi>\d+\.\d+)'  # Процент времени аппаратных прерываний
            r'\s*hi,\s*'  # Слово "hi" и пробелы
            r'(?P<si>\d+\.\d+)'  # Процент времени программных прерываний
            r'\s*si,\s*'  # Слово "si" и пробелы
            r'(?P<st>\d+\.\d+)?'  # Необязательное поле "st" (steal time)
            , re.MULTILINE)

        match = cpu_line_pattern.search(output)
        if match:
            # Создаем словарь с процентами загрузки CPU
            cpu_usage = {
                "user": float(match.group("user")),
                "system": float(match.group("system")),
                "idle": float(match.group("idle")),
                "io": float(match.group("io")),
                "hi": float(match.group("hi")),
                "si": float(match.group("si")),
            }
            return cpu_usage
        else:
            print("Не удалось найти данные о загрузке CPU.")
            return {}

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}

def all_cpu():
    data = {**parse_proc_stat(), **get_cpu_usage()}
    data['cpu_logical_core_count'] = get_cpu_logical_core_count()
    data['cpu_physical_core_count'] = get_cpu_physical_core_count()
    return data

if __name__ == "__main__":
    print(all_cpu())