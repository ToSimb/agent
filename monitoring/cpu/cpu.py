import psutil

#     общее количество физических ядер центральных процессоров в системе
#     общее количество логических ядер центральных процессоров в системе
def get_cpu_core_counts():
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    return physical_cores, logical_cores

# physical, logical = get_cpu_core_counts()
# print(f"Физические ядра: {physical}, Логические ядра: {logical}")

#      загрузка каждого логического процессора
def get_cpu_usage_per_core(interval=1):
    return psutil.cpu_percent(interval=interval, percpu=True)
# cpu_loads = get_cpu_usage_per_core()
# for i, load in enumerate(cpu_loads):
#     print(f"Логическое ядро {i + 1}: {load}% загрузка")

#     количество прерываний в системе
def get_interrupt_count():
    return psutil.cpu_stats().interrupts

# interrupt_count = get_interrupt_count()
# print(f"Количество аппаратных прерываний: {interrupt_count}")


def get_cpu_time_distribution(interval=1):
    cpu_times_percent = psutil.cpu_times_percent(interval=interval)
    return {
        "user_time": cpu_times_percent.user,
        "system_time": cpu_times_percent.system,
        "idle_time": cpu_times_percent.idle
    }

cpu_times = get_cpu_time_distribution()
print(f"Процент времени пользовательских операций: {cpu_times['user_time']}%")
print(f"Процент времени системных операций: {cpu_times['system_time']}%")
print(f"Процент простоя: {cpu_times['idle_time']}%")
