import psutil
import time

# Максимальная пропускная способность интерфейса (в байтах в секунду)
# Замените это значение на фактическую пропускную способность вашего интерфейса
MAX_BANDWIDTH = 12.5 * 1024 * 1024  # Пример для 100 Мбит/с (12.5 МБ/с)

## ! для получения MAX_BANDWIDTH
## wmic nic where "NetEnabled=true" get Name, Speed

# Функция для получения статистики по сетевым интерфейсам
def get_network_stats():
    # Получаем статистику по всем интерфейсам
    net_io = psutil.net_io_counters(pernic=True)

    # Выводим статистику для каждого интерфейса
    for interface_name, stats in net_io.items():
        print(f"Интерфейс: {interface_name}")
        print(f"Получено байт: {stats.bytes_recv}")
        print(f"Получено пакетов: {stats.packets_recv}")
        print(f"Отправлено байт: {stats.bytes_sent}")
        print(f"Отправлено пакетов: {stats.packets_sent}")
        print(f"Ошибки при приеме: {stats.errin}")
        print(f"Ошибки при отправке: {stats.errout}")
        print("-" * 50)

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
time.sleep(1)

# Получаем текущую статистику
current_stats = psutil.net_io_counters(pernic=True)

# Выводим статистику и скорость
for interface_name in current_stats.keys():
    if interface_name in previous_stats:
        recv_speed, sent_speed, load_recv, load_sent = calculate_speed_and_load(previous_stats[interface_name], current_stats[interface_name], 1)
        print(f"Интерфейс: {interface_name}")
        print(f"Получено байт: {current_stats[interface_name].bytes_recv}")
        print(f"Получено пакетов: {current_stats[interface_name].packets_recv}")
        print(f"Скорость входящего трафика: {recv_speed:.2f} байт/с")
        print(f"Загрузка входящим трафиком: {load_recv:.2f}%")
        print(f"Отправлено байт: {current_stats[interface_name].bytes_sent}")
        print(f"Отправлено пакетов: {current_stats[interface_name].packets_sent}")
        print(f"Скорость исходящего трафика: {sent_speed:.2f} байт/с")
        print(f"Загрузка исходящим трафиком: {load_sent:.2f}%")
        print(f"Ошибки при приеме: {current_stats[interface_name].errin}")
        print(f"Ошибки при отправке: {current_stats[interface_name].errout}")
        print("-" * 50)
