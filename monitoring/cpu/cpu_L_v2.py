import psutil


def get_cpu_names():
    cpu_names = set()  # Используем множество, чтобы избежать дублирования имен
    try:
        # Читаем файл /proc/cpuinfo и собираем имена процессоров
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    cpu_names.add(line.split(":")[1].strip())
    except Exception as e:
        return f"Ошибка при получении имен процессоров: {e}"

    return list(cpu_names)  # Возвращаем список уникальных имен процессоров


def gather_cpu_info():
    # Получаем информацию о процессорах
    cpu_freq = psutil.cpu_freq()
    logical_cpus = psutil.cpu_count(logical=True)
    physical_cpus = psutil.cpu_count(logical=False)

    # Получаем имена процессоров
    cpu_names = get_cpu_names()

    # Получаем загрузку процессора
    cpu_usage = psutil.cpu_percent(percpu=False, interval=1)

    # Выводим информацию о процессорах
    print("Информация о процессорах:")
    print("--------------------------------------------------")
    for cpu_name in cpu_names:
        print(f"Имя: {cpu_name}")
    print(f"Физических ядер: {physical_cpus}")
    print(f"Логических процессоров: {logical_cpus}")
    print(f"Максимальная частота: {cpu_freq.max} MHz")
    print(f"Текущая частота: {cpu_freq.current} MHz")
    print(f"Загрузка процессора: {cpu_usage}%")
    print("--------------------------------------------------")


if __name__ == "__main__":
    gather_cpu_info()
