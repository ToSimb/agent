import time

def get_cpu_info():
    cpu_info = {}
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith("processor"):
                processor_id = line.split(":")[1].strip()
                cpu_info[processor_id] = {}
            elif line.startswith("physical id"):
                physical_id = line.split(":")[1].strip()
                cpu_info[processor_id]['physical_id'] = physical_id
            elif line.startswith("core id"):
                core_id = line.split(":")[1].strip()
                cpu_info[processor_id]['core_id'] = core_id
            elif line.startswith("model name"):
                model_name = line.split(":")[1].strip()
                cpu_info[processor_id]['model_name'] = model_name

    return cpu_info

if __name__ == "__main__":
    start_time = time.time()  # Запоминаем время начала
    cpu_info = get_cpu_info()
    end_time = time.time()  # Запоминаем время окончания

    elapsed_time = end_time - start_time  # Вычисляем время выполнения

    # Записываем результаты в файл
    with open("cpu_cpuinfo_count.txt", "w") as f:
        for processor_id, info in cpu_info.items():
            physical_id = info.get('physical_id', 'N/A')
            core_id = info.get('core_id', 'N/A')
            model_name = info.get('model_name', 'N/A')
            f.write(f"Логический процессор {processor_id}: Физический процессор {physical_id}, Ядро {core_id}, Название: {model_name}\n")

        f.write(f"Время выполнения: {elapsed_time:.4f} секунд\n")
