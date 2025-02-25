import platform
import subprocess


# Нужны sata диски



def run_smartctl_command(command):
    """Запускает smartctl и возвращает вывод или None при ошибке"""
    try:
        return subprocess.check_output(command, stderr=subprocess.DEVNULL).decode('cp1251')
    except subprocess.CalledProcessError as e:
        print(f"SMART недоступен для команды: {' '.join(command)}:\n{e}")
        return None


def get_disk_list():
    """Получение списка дисков для Windows и Linux"""
    if platform.system() == "Linux":
        try:
            result = subprocess.check_output(["lsblk", "-d", "-n", "-o", "NAME"]).decode().strip().split("\n")
            return [f"/dev/{disk.strip()}" for disk in result if disk.strip()]
        except Exception as e:
            print(f"Ошибка получения списка дисков: {e}")
            return []
    elif platform.system() == "Windows":
        try:
            result = subprocess.check_output(["smartctl", "--scan"]).decode().strip().split("\n")
            print(result)
            disks = [[line.split()[0], ' '.join([line.split()[1], line.split()[2]])] for line in result if line.strip()]
            print(disks)
            return disks
        except Exception as e:
            print(f"Ошибка получения списка дисков: {e}")
            return []
    else:
        print(f"Ошибка получения списка дисков")
        return []


def get_disks_data():
    disks = get_disk_list()
    if not disks:
        print("Диски не найдены.")
        return

    data = {}

    for disk_name in disks:
        current_disk_data = {}
        result = run_smartctl_command(f'smartctl -A {disk_name[1]} {disk_name[0]}')
        for line in result.split('\n'):
            if 'Temperature' in line and "Celsius" in line:
                current_disk_data['Температура'] = int(line.split()[-2])
            elif 'Power On Hours' in line:
                current_disk_data['Общее время работы'] = int(''.join(line.split()[3:]))

        data[disk_name[0]] = current_disk_data
        print(result)
        print(data)


get_disks_data()