import subprocess
import time
import locale

def measure_time(func, *args, **kwargs):
    """Функция для измерения времени выполнения другой функции."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

def list_physical_disks():
    try:
        result = subprocess.run(['lsblk', '-o', 'NAME,TYPE,SIZE'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        disks = [line.split() for line in lines if 'disk' in line and line.startswith('sd')]
        print(disks)
        return disks
    except Exception as e:
        return str(e)

def get_disk_model(disk):
    try:
        with open(f'/sys/block/{disk}/device/model', 'r') as f:
            return f.read().strip()
    except Exception as e:
        return str(e)


def get_disk_speed(disk_pull):
    try:
        speeds = {}
        result = subprocess.run(
            ["iostat", "-d", "-k", "1", "2"],  # Второй замер нужен
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line:
                aa = line.split()
                if aa[0] in disk_pull:
                    print(aa)
                    speeds[aa[0]] = [aa[2], aa[3]]
        return speeds
    except Exception as e:
        print(f"Ошибка получения скорости чтения и записи дисков: {e}")
    return speeds


def run_smartctl_command(command):
    try:
        encoding = locale.getpreferredencoding()
        return subprocess.check_output(command, stderr=subprocess.DEVNULL).decode(encoding)
    except Exception as e:
        print(f"Ошибка команды smartctl: {e}")
        return ""

def parse_smart_info(disk):
    command = ['smartctl', '-A', disk]
    disk_info = run_smartctl_command(command)

    temperature = -1
    power_on_hours = -1
    read_error_rate = -1
    seek_error_rate = -1
    reallocated_sectors = -1
    output_lines = []
    print("______")
    for line in disk_info.splitlines():
        # print(line)
        if 'Airflow_Temperature_Cel' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                temperature = int(parts[9])
        # добавил на всякий случай
        elif 'Temperature_Celsius' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                temperature = int(parts[9])
        # добавил на всякий случай
        elif 'Temperature:' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                temperature = int(parts[-2])  # Используем -2 для получения значения
        elif "Power_On_Hours" in line or "Power On Hours:" in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                power_on_hours = int(parts[9])
        elif 'ECC_Error_Rate' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                read_error_rate = int(parts[9])
        # добавил на всякий случай
        elif "Raw_Read_Error_Rate" in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                read_error_rate = int(parts[9])
        elif 'CRC_Error_Count' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                seek_error_rate = int(parts[9])
        # добавил на всякий случай
        elif 'Seek_Error_Rate' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                seek_error_rate = int(parts[9])
        elif 'Reallocated_Sector_Ct' in line:
            output_lines.append(line)
            parts = line.split()
            if len(parts) > 9:
                reallocated_sectors = int(parts[9])

    return {
        'temperature': temperature,
        'power_on_hours': power_on_hours,
        'read_error_rate': read_error_rate,
        'seek_error_rate': seek_error_rate,
        'reallocated_sectors': reallocated_sectors,
        'output_lines': output_lines
    }

physical_disks, time_physical_disks = measure_time(list_physical_disks)
with open("disk_info.txt", "w") as file:
    file.write(f"Время получения информации о наличии дисков: {time_physical_disks:.4f} секунд \n")
    file.write("Физические жесткие диски: \n")
    file.write('-' * 25 + '\n')


    disk_pull = []
    for disk_info in physical_disks:
        disk_pull.append(disk_info[0])

    disk_speed = get_disk_speed(disk_pull)
    print(disk_speed)
    for disk_info in physical_disks:
        disk_name = disk_info[0]
        disk_size = disk_info[2]
        disk_model = get_disk_model(disk_name)

        disk_params, time_disk_params = measure_time(parse_smart_info,f"/dev/{disk_name}")
        file.write(f"Физический диск: {disk_name}, Размер: {disk_size}, Модель: {disk_model} \n")
        file.write(f"   Температура: {disk_params['temperature']} °C \n")
        file.write(f"   Общее время работы: {disk_params['power_on_hours']} часов \n")
        file.write(f"   Частота ошибок чтения: {disk_params['read_error_rate']} \n")
        file.write(f"   Частота ошибок позиционирования: {disk_params['seek_error_rate']} \n")
        file.write(f"   Количество переназначенных секторов: {disk_params['reallocated_sectors']} \n")
        if disk_name in disk_speed:
            file.write(f"   Скорость чтения с диска: {disk_speed[disk_name][0]} Кбайт/с \n")
            file.write(f"   Скорость записи на диск: {disk_speed[disk_name][1]} Кбайт/с \n")
        else:
            file.write(f"   Скорость чтения с диска: -1 Кбайт/с \n")
            file.write(f"   Скорость записи на диск: -1 Кбайт/с \n")
        file.write(f"   Время потраченное на парсинг диска: {time_disk_params} \n")
        file.write("- -" * 10 + '\n')
        for i in disk_params['output_lines']:
            file.write(f" {i} \n")
        file.write("-"*50 + "\n")
print("Информация сохранена на disk_info122.txt")