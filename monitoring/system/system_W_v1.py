import psutil
import time

def measure_time(func, *args, **kwargs):
    """Функция для измерения времени выполнения другой функции."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

# Засекаем общее время выполнения
time_start = time.time()

uptime_seconds, uptime_time = measure_time(lambda: time.time() - psutil.boot_time())
vm, vm_time = measure_time(psutil.virtual_memory)
swap, swap_time = measure_time(psutil.swap_memory)
cpu_load, cpu_load_time = measure_time(psutil.cpu_percent, interval=0.1)
physical_cores, physical_cores_time = measure_time(psutil.cpu_count, logical=False)
logical_cores, logical_cores_time = measure_time(psutil.cpu_count, logical=True)
cpu_stats, cpu_stats_time = measure_time(psutil.cpu_stats)  # Получаем статистику CPU

# Засекаем время начала вывода в консоль
parse_start = time.time()

# Формируем строку с системной информацией
output = []
output.append(f"Аптайм (секунды): {uptime_seconds:.2f}")
output.append(f"Виртуальная память - всего: {vm.total} байт")
output.append(f"Виртуальная память - использовано: {vm.used} байт")
output.append(f"Виртуальная память - свободно: {vm.free} байт")
output.append(f"Файл подкачки - всего: {swap.total} байт")
output.append(f"Файл подкачки - использовано: {swap.used} байт")
output.append(f"Файл подкачки - свободно: {swap.free} байт")
output.append(f"Загрузка CPU: {cpu_load:.2f}%")
output.append(f"Физические ядра: {physical_cores}")
output.append(f"Логические ядра: {logical_cores}")
output.append(f"Прерывания в системе: {cpu_stats.interrupts}")  # Добавлен вывод количества прерываний

# Засекаем время окончания вывода
parse_end = time.time()

# Добавляем информацию о времени выполнения запросов
output.append("\nВремя выполнения запросов:")
output.append(f"Аптайм: {uptime_time:.5f} секунд")
output.append(f"Виртуальная память: {vm_time:.5f} секунд")
output.append(f"Файл подкачки: {swap_time:.5f} секунд")
output.append(f"Загрузка CPU: {cpu_load_time:.5f} секунд")
output.append(f"Физические ядра: {physical_cores_time:.5f} секунд")
output.append(f"Логические ядра: {logical_cores_time:.5f} секунд")
output.append(f"Прерывания в системе: {cpu_stats_time:.5f} секунд")

# Вывод времени парсинга (вывода)
parse_time = parse_end - parse_start
output.append(f"\nВремя вывода данных: {parse_time:.5f} секунд")

# Общее время выполнения кода
time_end = time.time()
output.append(f"Общее время выполнения кода: {time_end - time_start:.5f} секунд")

# Сохраняем данные в файл
with open("system_info.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(output))

print("Данные успешно сохранены в system_info.txt")
