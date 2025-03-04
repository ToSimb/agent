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
    try:
        for disk in disks:
            current_disk_data = {}
            data[disk[0]] = {}
            result = run_smartctl_command(['smartctl', '-A', disk[1], disk[2], disk[0]])
            for line in result.splitlines():
                if "Temperature_Celsius" in line:
                    current_disk_data["Temperature"] = int(line.split()[-1])
                    continue
                elif "Temperature:" in line:
                    current_disk_data["Temperature"] = int(line.split()[-2])
                    continue
                elif "Power_On_Hours" in line:
                    current_disk_data["Power_On_Hours"] = int(line.split()[-1])
                    continue
                elif "Power On Hours:" in line:
                    current_disk_data["Power_On_Hours"] = int(line.split()[-1])
                    continue
                elif "Raw_Read_Error_Rate" in line or "Read_Error_Rate" in line:
                    current_disk_data["Read_Error_Rate"] = int(line.split()[-1])
                    continue
                elif "Seek_Error_Rate" in line:
                    current_disk_data["Seek_Error_Rate"] = int(line.split()[-1])
                    continue
                elif "Reallocated_Sector_Ct" in line:
                    current_disk_data["Reallocated_Sector_Ct"] = int(line.split()[-1])
                    continue
                elif "Percent_Lifetime_Used" in line:
                    current_disk_data["Percent_Lifetime_Used"] = int(line.split()[-1])
                    continue
                elif "SSD_Life_Left" in line:
                    current_disk_data["NAND"] = int(line.split()[-1])
                    continue
                elif "Количество использованных резервных блоков??????" in line:
                    current_disk_data["Количество использованных резервных блоков"] = int(line.split()[-1])
                    continue
            data[disk[0]] = current_disk_data
    except Exception as e:
        print(f"Ошибка обработки вывода smartctl -A: {e}")
    return data