import subprocess
import time


def measure_time(func, *args, **kwargs):
    """Функция для измерения времени выполнения другой функции."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start


def parse_gpu_data(line):
    """Парсит строку данных о GPU и возвращает словарь с информацией"""
    values = line.split(", ")
    return {
        "Index": int(values[0]),
        "UUID": values[1],
        "Model": values[2],
        "Core Clock (MHz)": int(values[3]) ,
        "Memory Clock (MHz)": int(values[4]) ,
        "GPU Utilization (%)": int(values[5]) ,
        "Memory Utilization (%)": int(values[6]),
        "Memory Used (MB)": int(values[7]) ,
        "Fan Speed (%)": int(values[8]),
        "Temperature (C)": int(values[9])
    }


def all_gpu():
    """Получает данные о всех видеокартах через nvidia-smi"""
    try:
        # Выполняем команду nvidia-smi и получаем данные в csv-формате
        result, time_result = measure_time(subprocess.run,
                                           ["nvidia-smi",
                                            "--query-gpu=index,uuid,name,clocks.gr,clocks.mem,utilization.gpu,utilization.memory,memory.used,fan.speed,temperature.gpu",
                                            "--format=csv,noheader,nounits"],
                                           capture_output=True, text=True, check=True
                                           )
        # Получаем строки с данными из результата выполнения команды
        lines = result.stdout.strip().split("\n")  # здесь мы обращаемся к stdout объекта
        time_start_pars = time.time()
        gpu_data_list = list(map(parse_gpu_data, lines))
        gpus_data_time = time.time() - time_start_pars  # Время парсинга данных

        return gpu_data_list, time_result, gpus_data_time

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении nvidia-smi: {e}")
        return [], 0, 0  # Возвращаем пустые значения в случае ошибки
    except Exception as e:
        print(f"Неизвестная ошибка при мониторинге Nvidia GPU: {e}")
        return [], 0, 0  # Возвращаем пустые значения в случае ошибки


def log_output(f, *args, **kwargs):
    """Функция для записи в файл и вывода в консоль"""
    print(*args, **kwargs)  # Выводим в консоль
    f.write("".join(str(arg) + "\n" for arg in args))  # Записываем в файл


if __name__ == "__main__":
    gpus_data, time_to_get_data, gpus_data_time = all_gpu()

    # Проверка на наличие данных перед записью в файл
    with open("gpu_data.txt", "w", encoding="utf-8") as f:
        if gpus_data:
            log_output(f, f"Время получения данных о GPU: {time_to_get_data:.4f} секунд")
            log_output(f, f"Время парсинга данных о GPU: {gpus_data_time:.4f} секунд")
            log_output(f, "\nИнформация о GPU:\n")

            # Для каждого GPU записываем его параметры и выводим в консоль
            for gpu in gpus_data:
                log_output(f, f"GPU {gpu['Index']} ({gpu['Model']}):")
                log_output(f, f"  UUID: {gpu['UUID']}")
                log_output(f, f"  Тактовая частота ядра (МГц): {gpu['Core Clock (MHz)']}")
                log_output(f, f"  Тактовая частота памяти (МГц): {gpu['Memory Clock (MHz)']}")
                log_output(f, f"  Загрузка GPU (%): {gpu['GPU Utilization (%)']}")
                log_output(f, f"  Загрузка памяти (%): {gpu['Memory Utilization (%)']}")
                log_output(f, f"  Используемая память (МБ): {gpu['Memory Used (MB)']}")
                log_output(f, f"  Скорость вентилятора (%): {gpu['Fan Speed (%)']}")
                log_output(f, f"  Температура (°C): {gpu['Temperature (C)']}")
                log_output(f, "-" * 40)
        else:
            log_output(f, "Нет данных о GPU для записи.")