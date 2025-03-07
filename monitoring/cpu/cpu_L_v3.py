import subprocess
import time

# Начало замера времени
start_time = time.time()

# Выполняем команду mpstat без ожидания
try:
    result = subprocess.run(['mpstat', '-P', 'ALL', '0'], capture_output=True, text=True, check=True)
    output = result.stdout
except subprocess.CalledProcessError as e:
    print(f"Ошибка при выполнении команды mpstat: {e}")
    output = ""
import time

# Начало замера времени
start_time = time.time()

# Обработка вывода
lines = output.splitlines()

with open('cpu_mpstat.txt', 'w') as file:  # Открываем файл для записи
    file.write("Информация о загрузке процессоров:\n")
    file.write("--------------------------------------------------\n")
    for line in lines[3:]:  # Пропускаем первые три строки заголовка
        columns = line.split()
        if len(columns) > 0:
            file.write(f"Процессор: {columns[1]}\n")
            file.write(f"  %user: {columns[2]} (время, проведенное в пользовательском режиме)\n")
            file.write(f"  %nice: {columns[3]} (время, проведенное в режиме 'nice')\n")
            file.write(f"  %system: {columns[4]} (время, проведенное в системном режиме)\n")
            file.write(f"  %idle: {columns[11]} (время простоя процессора)\n")
            file.write(f"  %iowait: {columns[5]} (время ожидания ввода-вывода)\n")
            file.write(f"  %irq: {columns[6]} (время, проведенное на обработку прерываний)\n")
            file.write(f"  %softirq: {columns[7]} (время, проведенное на обработку программных прерываний)\n")
            file.write(f"  %steal: {columns[8]} (время, отведенное для виртуальных машин)\n")
            file.write("--------------------------------------------------\n")

# Конец замера времени
end_time = time.time()

# Вывод времени выполнения
execution_time = end_time - start_time
with open('cpu_mpstat.txt', 'a') as file:  # Открываем файл для добавления
    file.write(f"\nВремя выполнения: {execution_time:.6f} секунд\n")
