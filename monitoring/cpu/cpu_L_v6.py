import subprocess
import psutil
import time


def get_cpu_mapping():
    """Получает привязку логических ядер к физическим процессорам"""
    cmd = "lscpu -e=CPU,SOCKET,NODE"
    output = subprocess.check_output(cmd, shell=True, text=True).strip()
    lines = output.split("\n")[1:]  # Пропускаем заголовок

    cpu_mapping = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            cpu_id = int(parts[0])
            socket_id = int(parts[1])
            cpu_mapping[cpu_id] = socket_id

    return cpu_mapping


def get_cpu_usage():
    """Получает загрузку каждого логического процессора"""
    return psutil.cpu_percent(percpu=True)


def get_cpu_times():
    """Получает подробную статистику времени работы логических ядер"""
    times = psutil.cpu_times_percent(percpu=True)
    return [{
        "Пользовательские операции": round(t.user, 2),
        "Системные операции": round(t.system, 2),
        "Программные прерывания": round(t.irq, 2),
        "Аппаратные прерывания": round(t.softirq, 2),
        "Простой": round(t.idle, 2),
        "Ожидание операций ввода/вывода": round(t.iowait, 2) if hasattr(t, 'iowait') else 0.0
    } for t in times]


def get_physical_cpu_info(cpu_mapping):
    """Собирает параметры для каждого физического процессора"""
    physical_cpus = set(cpu_mapping.values())
    cpu_freq = psutil.cpu_freq()

    result = {}
    for socket in physical_cpus:
        logical_cores = [core for core, sock in cpu_mapping.items() if sock == socket]
        physical_core_count = len(set(logical_cores)) // psutil.cpu_count(logical=True) * psutil.cpu_count(
            logical=False)
        result[socket] = {
            "Загрузка": round(sum(get_cpu_usage()[core] for core in logical_cores) / len(logical_cores), 2),
            "Частота": round(cpu_freq.current, 2) if cpu_freq else -1,
            "Физические ядра": physical_core_count,
            "Логические ядра": len(logical_cores)
        }

    return result


def main():
    cpu_mapping = get_cpu_mapping()
    cpu_usage = get_cpu_usage()
    cpu_times = get_cpu_times()
    physical_cpu_info = get_physical_cpu_info(cpu_mapping)

    print("Физические процессоры:")
    for socket, info in physical_cpu_info.items():
        print(f"  Процессор {socket}: загрузка {info['Загрузка']}%, частота {info['Частота']} MHz, "
              f"физ. ядер {info['Физические ядра']}, лог. ядер {info['Логические ядра']}")

    print("\nЛогические ядра:")
    for core, socket in cpu_mapping.items():
        print(f"  Ядро {core} (проц. {socket}): загрузка {cpu_usage[core]}%, "
              f"user {cpu_times[core]['Пользовательские операции']}%, "
              f"system {cpu_times[core]['Системные операции']}%, "
              f"irq {cpu_times[core]['Программные прерывания']}%, "
              f"softirq {cpu_times[core]['Аппаратные прерывания']}%, "
              f"idle {cpu_times[core]['Простой']}%, "
              f"iowait {cpu_times[core]['Ожидание операций ввода/вывода']}%")


if __name__ == "__main__":
    start = time.time()  # Исправлено: добавлен вызов функции
    main()  # Добавлен вызов функции main()
