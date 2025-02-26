import locale
import subprocess


def run_smartctl_command(command):
    """Запускает smartctl и возвращает вывод или None при ошибке"""
    try:
        encoding = locale.getpreferredencoding()
        return subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding)
    except subprocess.CalledProcessError as e:
        print(f"SMART недоступен для команды: {' '.join(command)}:\n{e}")
        return None


def get_disk_list():
    """Получение списка дисков"""
    try:
        result = run_smartctl_command(['smartctl', '--scan']).strip().split("\n")
        disks = [[line.split()[0], line.split()[1], line.split()[2]] for line in result if line.strip()]
        print(disks)
        return disks
    except Exception as e:
        print(f"Ошибка получения списка дисков: {e}")
        return []

def get_disk_data():
    disks = get_disk_list()
    if not disks:
        print("Диски не найдены.")
        return

    data = {}

    for disk in disks:
        current_disk_data = {}
        result = run_smartctl_command(['smartctl', '-A', disk[1], disk[2], disk[0]])
        for line in result.splitlines():
            if "Temperature_Celsius" in line:
                current_disk_data["temperature"] = int(line.split()[-1])
            elif "Power_On_Hours" in line:
                current_disk_data["power_on_hours"] = int(line.split()[-1])
            elif "Raw_Read_Error_Rate" in line or "Read_Error_Rate" in line:
                current_disk_data["read_error_rate"] = int(line.split()[-1])
            elif "Seek_Error_Rate" in line:
                current_disk_data["seek_error_rate"] = int(line.split()[-1])
            elif "Reallocated_Sector_Ct" in line:
                current_disk_data["reallocated_sectors"] = int(line.split()[-1])

        data[disk[0]] = current_disk_data
    print(data)

get_disk_data()