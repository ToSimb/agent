import json
import pynvml

def initialize_nvml():
    """Инициализация NVML"""
    try:
        pynvml.nvmlInit()
    except Exception as e:
        print(f"Ошибка инициализации NVML: {e}")

def get_device_count():
    """Возвращает количество доступных GPU"""
    try:
        return pynvml.nvmlDeviceGetCount()
    except Exception as e:
        print(f"Нет доступа ни к одному GPU: {e}")

def get_gpu_info(handle):
    """Возвращает информацию о видеокарте"""
    try:
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return {
            "UUID": pynvml.nvmlDeviceGetUUID(handle),
            "Model": pynvml.nvmlDeviceGetName(handle).decode(),
            "Core Clock (MHz)": pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS),
            "Memory Clock (MHz)": pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM),
            "GPU Utilization (%)": pynvml.nvmlDeviceGetUtilizationRates(handle).gpu,
            "Memory Utilization (%)": pynvml.nvmlDeviceGetUtilizationRates(handle).memory,
            "Memory Used (MB)": memory_info.used,
            "Memory Total (MB)": memory_info.total,
            "Fan Speed (%)": pynvml.nvmlDeviceGetFanSpeed(handle),
            "Temperature (C)": pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        }
    except Exception as e:
        print(f"Ошибка получения информации о GPU: {e}")

def get_all_gpus_info():
    """Собирает данные о всех доступных GPU и возвращает JSON"""
    initialize_nvml()
    gpus_data = []
    try:
        device_count = get_device_count()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpus_data.append(get_gpu_info(handle))
    finally:
        pynvml.nvmlShutdown()
    return json.dumps(gpus_data, indent=4)

if __name__ == "__main__":
    print(get_all_gpus_info())
