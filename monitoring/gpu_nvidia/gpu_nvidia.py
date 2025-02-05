import pynvml


def initialize_nvml():
    """Инициализация NVML"""
    try:
        pynvml.nvmlInit()
    except Exception as e:
        print(f"Ошибка инициализации NVML: {e}")
        return -1


def get_device_count():
    """Возвращает количество доступных GPU"""
    try:
        return pynvml.nvmlDeviceGetCount()
    except Exception as e:
        print(f"Нет доступа ни к одному GPU: {e}")
        return -1


def get_gpu_uuid(handle):
    try:
        return pynvml.nvmlDeviceGetUUID(handle)
    except Exception as e:
        print(f"Ошибка получения UUID: {e}")
        return -1


def get_gpu_model(handle):
    try:
        return pynvml.nvmlDeviceGetName(handle).decode()
    except Exception as e:
        print(f"Ошибка получения модели GPU: {e}")
        return -1


def get_core_clock(handle):
    try:
        return pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
    except Exception as e:
        print(f"Ошибка получения частоты видео-ядра: {e}")
        return -1


def get_memory_clock(handle):
    try:
        return pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
    except Exception as e:
        print(f"Ошибка получения частоты памяти: {e}")
        return -1


def get_gpu_utilization(handle):
    try:
        return pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
    except Exception as e:
        print(f"Ошибка получения загрузки GPU: {e}")
        return -1


def get_memory_utilization(handle):
    try:
        return pynvml.nvmlDeviceGetUtilizationRates(handle).memory
    except Exception as e:
        print(f"Ошибка получения загрузки памяти GPU: {e}")
        return -1


def get_memory_info(handle):
    try:
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return memory_info.used // (1024 * 1024), memory_info.total // (1024 * 1024)
    except Exception as e:
        print(f"Ошибка получения информации о памяти: {e}")
        return -1


def get_fan_speed(handle):
    try:
        return pynvml.nvmlDeviceGetFanSpeed(handle)
    except Exception as e:
        print(f"Ошибка получения скорости вентиляторов: {e}")
        return -1


def get_temperature(handle):
    try:
        return pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    except Exception as e:
        print(f"Ошибка получения температуры GPU: {e}")
        return -1


def collect_gpu_data():
    """Собирает данные о всех доступных GPU"""
    gpu_data = []
    device_count = get_device_count()

    if device_count == 0:
        print("Нет доступных GPU.")
        return

    for i in range(device_count):
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpu_info = {
                "UUID": get_gpu_uuid(handle),
                "Model": get_gpu_model(handle),
                "Core Clock (MHz)": get_core_clock(handle),
                "Memory Clock (MHz)": get_memory_clock(handle),
                "GPU Utilization (%)": get_gpu_utilization(handle),
                "Memory Utilization (%)": get_memory_utilization(handle),
                "Memory Used (MB)": get_memory_info(handle)[0],
                "Memory Total (MB)": get_memory_info(handle)[1],
                "Fan Speed (%)": get_fan_speed(handle),
                "Temperature (C)": get_temperature(handle)
            }
            gpu_data.append(gpu_info)
        except Exception as e:
            print(f"Ошибка обработки данных GPU {i}: {e}")

    return gpu_data


def main():
    initialize_nvml()
    gpu_info = collect_gpu_data()

    if gpu_info:
        for idx, gpu in enumerate(gpu_info):
            print(f"=== GPU #{idx + 1} ===")
            for key, value in gpu.items():
                print(f"{key}: {value}")
            print("=================")

    pynvml.nvmlShutdown()

if __name__ == "__main__":
    main()