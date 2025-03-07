import subprocess
from disk_WL import get_disk_data


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

        disk_list = [{"name": key, **value} for key, value in disk_data.items()]
        return disk_list

    except Exception as e:
        print(f"Критическая ошибка при получении данных о дисках: {e}")
        return {}

if __name__ == "__main__":
    print(all_disk())