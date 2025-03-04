from cpu_WL import (get_cpu_logical_core_count, get_cpu_physical_core_count, get_interrupt_count)
import subprocess
import time

def get_cpu_names():
    try:
        qwert1 = time.time()
        result = subprocess.run(
            ["wmic", "cpu", "get", "Name"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split("\n")
        cpu_names = [line.strip() for line in lines[1:] if line.strip()]
        qwert2 = time.time()
        print("получение имен")
        print(qwert2 - qwert1)
        return cpu_names
    except Exception as e:
        print(f"Ошибка при получении списка процессоров: {e}")
        return []


def get_cpu_metrics():
    try:
        qwert1 = time.time()
        cmd = "wmic path Win32_PerfFormattedData_PerfOS_Processor get Name,PercentProcessorTime,PercentInterruptTime,PercentDPCTime,PercentIdleTime,PercentUserTime,PercentPrivilegedTime /format:csv"
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            raise RuntimeError("Ошибка при выполнении команды WMIC")
    except Exception as e:
        print(f"Ошибка при выполнении команды WMIC: {e}")
        return -1

    try:
        lines = result.stdout.strip().split("\n")
        headers = lines[0].split(",")
        data_lines = lines[1:]

        cpu_data = []
        overall_metrics = {}

        for line in data_lines:
            values = line.split(",")
            if len(values) == len(headers):
                cpu_info = dict(zip(headers, values))
                if cpu_info["Name"] == "_Total":
                    overall_metrics.update({
                        "Hard_Time": float(cpu_info["PercentInterruptTime"]),
                        "Soft_Time": float(cpu_info["PercentDPCTime"]),
                        "Idle_Time": float(cpu_info["PercentIdleTime"]),
                        "User_Time": float(cpu_info["PercentUserTime"]),
                        "System_Time": float(cpu_info["PercentPrivilegedTime"])
                    })
                else:
                    cpu_data.append({
                        "id": cpu_info["Name"],
                        "Usage": float(cpu_info["PercentProcessorTime"])
                    })
    except Exception as e:
        print(f"Ошибка обработки вывода команды wmic: {e}")
        return -1
    qwert2 = time.time()
    print("получение параметров wmic")
    print(qwert2 - qwert1)
    return {"LogicalProcessors": cpu_data, **overall_metrics}


def get_cpu_time_io_wait():
    """Возвращает процент времени, которое центральный процессор простаивает в ожидании результатов операций ввода/вывода"""
    try:
        pass
    except Exception as e:
        print(f"Ошибка сбора параметра \"Процент времени простоя CPU в ожидании результатов операций ввода/вывода\": \n{e}")
        return -1


def all_cpu():
    data = {
        "cpu_names": get_cpu_names(),
        "physical_core": get_cpu_physical_core_count(),
        "logical_core": get_cpu_logical_core_count(),
        "interrupt_count": get_interrupt_count(),
        "cpu_io_wait_proc": get_cpu_time_io_wait(),
        **get_cpu_metrics()
    }
    return data


if __name__ == "__main__":
    print(all_cpu())