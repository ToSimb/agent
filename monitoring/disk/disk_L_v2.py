import subprocess


def list_physical_disks():
    try:
        # Выполняем команду lsblk с добавлением столбца TRAN
        result = subprocess.run(['lsblk', '-o', 'NAME,TYPE,TRAN'], capture_output=True, text=True)

        # Разбиваем вывод на строки
        lines = result.stdout.strip().split('\n')

        # Фильтруем только физические диски и собираем информацию о них
        disks = []
        for line in lines[1:]:  # Пропускаем заголовок
            parts = line.split()
            if 'disk' in parts and parts[0].startswith('sd'):
                disks.append((parts[0], parts[2]))  # Добавляем имя диска и тип подключения

        return disks
    except Exception as e:
        return str(e)


def get_disk_info(disk):
    try:
        # Выполняем команду smartctl
        result = subprocess.run(['smartctl', '-a', disk], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

# Пример использования
physical_disks = list_physical_disks()
print("Физические жесткие диски и их тип подключения:")
for disk, transport in physical_disks:
    print(f"Диск: {disk}, Тип подключения: {transport}")
