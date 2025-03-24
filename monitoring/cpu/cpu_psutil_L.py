import psutil
import time

def get_cpu_stats():
    # Получаем информацию о логических процессорах
    cpu_count = psutil.cpu_count(logical=True)
    cpu_stats = []

    # Получаем загрузку процессора для всех логических процессоров
    loads = psutil.cpu_percent(interval=0.1, percpu=True)
    # Получаем время процессора для всех логических процессоров
    times = psutil.cpu_times(percpu=True)

    for i in range(cpu_count):
        print(times[i])
        user_time = times[i].user
        system_time = times[i].system
        idle_time = times[i].idle
        irq_time = times[i].irq  # Время на аппаратные прерывания
        softirq_time = times[i].softirq  # Время на программные прерывания (DPC)
        iowait_time = times[i].iowait  # Время ожидания ввода-вывода

        # Формируем словарь с данными для каждого логического процессора
        total_time = user_time + system_time + idle_time + irq_time + softirq_time + iowait_time
        cpu_stats.append({
            'logical_processor': i,
            'load_percent': loads[i],
            'user_time_percent': (user_time / total_time) * 100,
            'system_time_percent': (system_time / total_time) * 100,
            'irq_time_percent': (irq_time / total_time) * 100,
            'softirq_time_percent': (softirq_time / total_time) * 100,
            'iowait_time_percent': (iowait_time / total_time) * 100,
            'idle_time_percent': (idle_time / total_time) * 100,
        })

    return cpu_stats


if __name__ == "__main__":
    start_time = time.time()  # Запоминаем время начала
    cpu_stats = get_cpu_stats()
    end_time = time.time()  # Запоминаем время окончания

    elapsed_time = end_time - start_time  # Вычисляем время выполнения

    # Записываем результаты в файл
    with open("cpu_psutil.txt", "w") as f:
        for stat in cpu_stats:
            f.write(f"Логический процессор {stat['logical_processor']}:\n")
            f.write(f"  🔹 Загрузка процессора: {stat['load_percent']}%\n")
            f.write(f"  🔹 Процент времени в пользовательском режиме: {stat['user_time_percent']:.2f}%\n")
            f.write(f"  🔹 Процент времени в системном режиме: {stat['system_time_percent']:.2f}%\n")
            f.write(f"  🔹 Процент времени на аппаратные прерывания: {stat['irq_time_percent']:.2f}%\n")
            f.write(f"  🔹 Процент времени на программные прерывания (DPC): {stat['softirq_time_percent']:.2f}%\n")
            f.write(f"  🔹 Процент времени на ожидание ввода-вывода: {stat['iowait_time_percent']:.2f}%\n")
            f.write(f"  🔹 Процент времени простоя: {stat['idle_time_percent']:.2f}%\n")
            f.write("\n")

        f.write(f"Время выполнения: {elapsed_time:.4f} секунд\n")
