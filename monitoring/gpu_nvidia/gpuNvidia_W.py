import subprocess
from concurrent.futures import ThreadPoolExecutor
import time

def parse_gpu_data(line):
    """Парсит строку данных о GPU и возвращает словарь с информацией"""
    values = line.split(", ")
    return {
        "Index": int(values[0]) or -1,
        "UUID": values[1],
        "Model": values[2],
        "Core Clock (MHz)": int(values[3]) or -1,
        "Memory Clock (MHz)": int(values[4]) or -1,
        "GPU Utilization (%)": int(values[5]) or -1,
        "Memory Utilization (%)": int(values[6]) or -1,
        "Memory Used (MB)": int(values[7]) or -1,
        "Fan Speed (%)": int(values[8]) or -1,
        "Temperature (C)": int(values[9]) or -1
    }


def all_gpu():
    """Получает данные о всех видеокартах через nvidia-smi"""
    start_time = time.time()
    try:
        # Выполняем команду nvidia-smi и получаем данные в csv-формате
        result = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=index,uuid,name,clocks.gr,clocks.mem,utilization.gpu,utilization.memory,memory.used,fan.speed,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )

        lines = result.stdout.strip().split("\n")

        # Используем ThreadPoolExecutor для параллельной обработки строк
        with ThreadPoolExecutor() as executor:
            gpus_data = list(executor.map(parse_gpu_data, lines))
        print("Время сбора параметров GPU:", time.time() - start_time)
        return gpus_data

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении nvidia-smi: {e}")
        return []
    except Exception as e:
        print(f"Неизвестная ошибка при мониторинге Nvidia GPU: {e}")
        return []


if __name__ == "__main__":
    print(all_gpu())
