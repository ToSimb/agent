import subprocess

def get_cpu_metrics():
    try:
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
                        "LogicalProcessor": cpu_info["Name"],
                        "Usage": float(cpu_info["PercentProcessorTime"])
                    })
    except Exception as e:
        print(f"Ошибка обработки вывода команды wmic: {e}")
        return -1
    return {"LogicalProcessors": cpu_data, **overall_metrics}


if __name__ == "__main__":
    print(get_cpu_metrics())
