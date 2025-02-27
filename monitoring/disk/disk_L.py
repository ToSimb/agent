import subprocess
from disk_WL import get_disk_data


def get_disk_usage():
    """Получает информацию о файловых системах (разделах) с помощью df -B1"""
    try:
        result = subprocess.run(["df", "-B1"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")

        partitions = {}
        for line in lines[1:]:  # Пропускаем заголовок
            data = line.split()
            if len(data) < 6 or not data[0].startswith("/dev/"):
                continue

            try:
                partition_info = {
                    "mount_point": data[5],
                    "total_size": int(data[1]),
                    "used": int(data[2]),
                    "available": int(data[3])
                }
                partitions[data[0]] = partition_info
            except (ValueError, IndexError) as e:
                print(f"Ошибка при обработке строки df: {line} — {e}")

        return partitions

    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения df: {e}")
        return {}


def get_disk_speed():
    """Получает скорость чтения и записи дисков с помощью iostat -dx"""
    try:
        result = subprocess.run(['iostat', '-dx'], capture_output=True, text=True, check=True)
        output = result.stdout.strip().split("\n")

        if len(output) < 4:
            print("Ошибка: неожиданный формат вывода iostat")
            return {}

        # Убираем заголовки, оставляя только строки с данными
        output = output[3:]

        disks_data = {}
        for line in output:
            parts = line.split()
            if len(parts) <= 8:
                continue  # Пропускаем строки, где недостаточно данных

            try:
                disk_name = f"/dev/{parts[0]}"
                read_speed = float(parts[2])  # В КБ/с
                write_speed = float(parts[8])  # В КБ/с

                disks_data[disk_name] = {
                    "read_speed_KBps": read_speed,
                    "write_speed_KBps": write_speed
                }
            except (ValueError, IndexError) as e:
                print(f"Ошибка при обработке строки iostat: {line} — {e}")

        return disks_data

    except FileNotFoundError:
        print("Ошибка: команда iostat не найдена. Установите пакет sysstat.")
        return {}
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения iostat: {e}")
        return {}

def all_disk():
    try:
        # Получаем данные о дисках
        disk_data = get_disk_data()
        disk_speed = get_disk_speed()

        # Объединяем данные о скорости с дисками
        for key in disk_speed:
            if key in disk_data:
                disk_data[key].update(disk_speed[key])

        # Получаем данные о разделах и объединяем с дисками
        parts_data = get_disk_usage()
        for part in parts_data.keys():
            parent_disk = part[:-1]  # Например, /dev/sda1 → /dev/sda
            if parent_disk in disk_data:
                disk_data[parent_disk][part] = parts_data[part]

        return disk_data

    except Exception as e:
        print(f"Критическая ошибка в программе: {e}")
        return {}
