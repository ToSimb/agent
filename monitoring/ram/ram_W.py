import subprocess

def all_ram():
    result = subprocess.run(
        ["wmic", "memorychip", "get",
         "Capacity,DeviceLocator,Manufacturer,PartNumber,Speed,ConfiguredVoltage,MinVoltage,MaxVoltage", "/format:csv"],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split("\n")[1:]  # Пропускаем заголовок
    ram_list = []

    for line in lines:
        parts = line.split(",")
        if len(parts) >= 7:
            ram_list.append({
                "Slot": parts[3],
                "Memory": int(parts[1]) / 1024 ** 3,
                "manufacturer": parts[4],
                "Model": parts[7],
                "Maximum frequency": parts[8],
                "voltage": parts[2],
                "min voltage": parts[6],
                "max voltage": parts[5]
            })
    return ram_list

if __name__ == "__main__":
    print(all_ram())
