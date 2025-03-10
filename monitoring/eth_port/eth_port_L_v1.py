import psutil
import time
import platform
import subprocess

def measure_time(func, *args, **kwargs):
    """Функция для измерения времени выполнения другой функции."""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start



# Максимальная пропускная способность интерфейса (в байтах в секунду)
# Замените это значение на фактическую пропускную способность вашего интерфейса
MAX_BANDWIDTH = 12.5 * 1024 * 1024  # Пример для 100 Мбит/с (12.5 МБ/с)


## ! для получения MAX_BANDWIDTH
## wmic nic where "NetEnabled=true" get Name, Speed
def get_max_bandwidth(interface_name):
    try:
        if platform.system() == "Windows":
            # Для Windows
            output = subprocess.check_output(
                f"wmic nic where \"NetEnabled=true and Name='{interface_name}'\" get Speed",
                shell=True
            )
            speed = int(output.decode().splitlines()[1].strip())
            return speed / 8  # Переводим в байты в секунду
        elif platform.system() == "Linux":
            # Для Linux
            output = subprocess.check_output(
                f"ethtool {interface_name}",
                shell=True
            ).decode()
            for line in output.splitlines():
                if "Speed:" in line:
                    speed = line.split()[1]
                    speed_value = int(speed[:-3])  # Убираем 'Mb/s'
                    return speed_value * 1024 * 1024 / 8  # Переводим в байты в секунду
    except Exception as e:
        print(f"Не удалось получить скорость для интерфейса {interface_name}: {e}")
        return None

# Функция для расчета скорости трафика и загрузки
def calculate_speed_and_load(previous_stats, current_stats, interval):
    recv_speed = (current_stats.bytes_recv - previous_stats.bytes_recv) / interval
    sent_speed = (current_stats.bytes_sent - previous_stats.bytes_sent) / interval
    load_recv = (recv_speed / MAX_BANDWIDTH) * 100  # Загрузка входящим трафиком в процентах
    load_sent = (sent_speed / MAX_BANDWIDTH) * 100  # Загрузка исходящим трафиком в процентах
    return recv_speed, sent_speed, load_recv, load_sent

# Получаем начальную статистику
previous_stats = psutil.net_io_counters(pernic=True)

# Ждем 1 секунду для расчета скорости
time.sleep(0.1)

# Получаем текущую статистику
current_stats, time_stats = measure_time(psutil.net_io_counters,pernic=True)

# Выводим статистику и скорость
for interface_name in current_stats.keys():
    if interface_name in previous_stats:
        recv_speed, sent_speed, load_recv, load_sent = calculate_speed_and_load(previous_stats[interface_name], current_stats[interface_name], 0.1)
        print(f"Интерфейс: {interface_name}")
        # print(f"Получено байт: {current_stats[interface_name].bytes_recv}")
        # print(f"Получено пакетов: {current_stats[interface_name].packets_recv}")
        # print(f"Скорость входящего трафика: {recv_speed:.2f} байт/с")
        # print(f"Загрузка входящим трафиком: {load_recv:.2f}%")
        # print(f"Отправлено байт: {current_stats[interface_name].bytes_sent}")
        # print(f"Отправлено пакетов: {current_stats[interface_name].packets_sent}")
        # print(f"Скорость исходящего трафика: {sent_speed:.2f} байт/с")
        # print(f"Загрузка исходящим трафиком: {load_sent:.2f}%")
        # print(f"Ошибки при приеме: {current_stats[interface_name].errin}")
        # print(f"Ошибки при отправке: {current_stats[interface_name].errout}")
        print("-" * 50)
print(f"Время получения информации за раз: {time_stats}")
