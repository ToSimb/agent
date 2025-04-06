import platform
import subprocess
import psutil
import re
import json

def find_field(fields, output):
    """
    Ищет первое совпадение одного из заданных полей в выводе команды.
    """
    for field in fields:
        match = re.search(rf"{field}:\s+(.*)", output)
        if match:
            return match.group(1).strip()
    return "Unknown"


def get_disks():
    """
    Получает список дисков с помощью smartctl, включая модель и серийный номер.
    """
    disks = []
    try:
        result = subprocess.run(["smartctl", "--scan"], capture_output=True, text=True)
        for line in result.stdout.strip().splitlines():
            match = re.search(r"(/dev/\S+|\S+:\s+)", line)
            if match:
                device = match.group(1).strip()
                try:
                    info_cmd = ["smartctl", "-i", device]
                    info = subprocess.run(info_cmd, capture_output=True, text=True)
                    output = info.stdout
                    model = find_field(["Model Number", "Model Family", "Device Model", "Product"], output)
                    serial = find_field(["Serial Number"], output)

                    disks.append({
                        "device": device,
                        "model": model,
                        "serial": serial
                    })
                except Exception as e:
                    disks.append({"device": device, "error": str(e)})
    except Exception as e:
        disks.append({"error": str(e)})
    return disks


def get_gpu():
    """
    Получает список GPU с помощью nvidia-smi, включая имя, серийный номер и UUID.
    """
    gpus = []
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,serial,gpu_uuid", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                parts = [part.strip() for part in line.split(",")]
                if len(parts) == 3:
                    name, serial, uuid = parts
                    gpus.append({
                        "name": name,
                        "serial": serial if serial != "[N/A]" else None,
                        "uuid": uuid
                    })
        else:
            print("error: nvidia-smi returned non-zero exit code")
    except FileNotFoundError:
        print("error: nvidia-smi not found")
    return gpus


def get_cpu():
    """
    Получает список процессоров:
    - на Windows: через wmic (имя и ID)
    - на Linux: через /proc/cpuinfo (только имя)
    """
    cpus = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'DeviceID,Name'],
                capture_output=True, text=True, check=True
            )
            lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
            for line in lines[1:]:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    cpus.append({
                        "id": parts[0].replace("CPU", "").strip(),
                        "name": parts[1].strip()
                    })
                else:
                    print("error: Could not parse wmic output")
        else:
            with open("/proc/cpuinfo", "r") as f:
                model_name = set()
                current_processor = {}
                for line in f:
                    if line.startswith("processor"):
                        if current_processor:
                            if current_processor != {}:
                                model_name.add(f"{current_processor['physical_id']}: {current_processor['model_name']}")
                            current_processor = {}
                    elif line.startswith("physical id"):
                        current_processor['physical_id'] = line.split(":")[1].strip()
                    elif line.startswith("model name"):
                        current_processor['model_name'] = line.split(":")[1].strip()
                for index in model_name:
                    print(index)
                    cpus.append(index)
    except Exception as e:
        print(f"error: {e}")
    return cpus


def get_network_interfaces():
    """
    Получает список сетевых интерфейсов и их IPv4-адресов.
    """
    interfaces = []
    try:
        for name, addrs in psutil.net_if_addrs().items():
            ipv4 = None
            for addr in addrs:
                if addr.family.name == "AF_INET":
                    ipv4 = addr.address
            interfaces.append({
                "name": name,
                "ipv4": ipv4 or None
            })
    except Exception as e:
        print(f"error: {e}")
    return interfaces


def collect_device_info():
    """
    Собирает информацию со всех типов устройств и возвращает единый словарь.
    """
    return {
        "disk": get_disks(),
        "gpu": get_gpu(),
        "cpu": get_cpu(),
        "interface": get_network_interfaces()
    }


if __name__ == "__main__":
    devices = collect_device_info()
    with open("_settings_file/_names.txt", "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=4, ensure_ascii=False)
    print("Информация успешно сохранена в файл settings_file")
