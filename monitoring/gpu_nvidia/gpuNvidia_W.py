import subprocess


def all_gpu():
    """Получает данные о всех видеокартах через nvidia-smi"""
    try:
        result = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=index,uuid,name,clocks.gr,clocks.mem,utilization.gpu,utilization.memory,memory.used,fan.speed,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )

        gpus_data = []
        for line in result.stdout.strip().split("\n"):
            values = line.split(", ")
            gpus_data.append({
                "Index": int(values[0]),
                "UUID": values[1],
                "Model": values[2],
                "Core Clock (MHz)": int(values[3]),
                "Memory Clock (MHz)": int(values[4]),
                "GPU Utilization (%)": int(values[5]),
                "Memory Utilization (%)": int(values[6]),
                "Memory Used (MB)": int(values[7]),
                "Fan Speed (%)": int(values[8]),
                "Temperature (C)": int(values[9])
            })

        return gpus_data

    except subprocess.CalledProcessError as e:
        print(json.dumps({"error": f"Ошибка при выполнении nvidia-smi: {e}"}, indent=4))
        return {}
    except Exception as e:
        print(json.dumps({"error": f"Неизвестная ошибка: {e}"}, indent=4))
        return {}