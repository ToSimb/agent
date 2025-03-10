import psutil
import time


INTERVAL = 0.5

def get_load(current_speed, max_bandwidth):
    if max_bandwidth == -1 or current_speed == -1: return -1
    return (current_speed / max_bandwidth) * 100.0

def calculate_speed_and_load(previous_stats, current_stats, interval, max_bandwidth):
    recv_speed = (current_stats.bytes_recv - previous_stats.bytes_recv) / interval
    sent_speed = (current_stats.bytes_sent - previous_stats.bytes_sent) / interval
    load_recv = get_load(recv_speed, max_bandwidth)
    load_sent = get_load(sent_speed, max_bandwidth)
    return recv_speed, sent_speed, load_recv, load_sent

previous_stats = psutil.net_io_counters(pernic=True)
time.sleep(INTERVAL)
current_stats = psutil.net_io_counters(pernic=True)

bandwidth_stats = psutil.net_if_stats()

# Выводим статистику
for interface_name in current_stats.keys():
    if interface_name in previous_stats:

        max_bandwidth = bandwidth_stats.get(interface_name, None)
        max_bandwidth_speed = max_bandwidth.speed * 125000.0 if max_bandwidth.speed != 0.0 else -1
        print(max_bandwidth_speed)
        recv_speed, sent_speed, load_recv, load_sent = calculate_speed_and_load(previous_stats[interface_name], current_stats[interface_name], INTERVAL, max_bandwidth_speed)
        print(f"Интерфейс: {interface_name}")
        print(f"    Максимальная пропускная способность(не надо собирать): {max_bandwidth_speed} байт/с")
        print(f"    Скорость входящего трафика: {recv_speed} байт/с")
        print(f"    Загрузка входящим трафиком: {load_recv}%")
        print(f"    Скорость исходящего трафика: {sent_speed} байт/с")
        print(f"    Загрузка исходящим трафиком: {load_sent}%")
        print(f"    Получено байт: {current_stats[interface_name].bytes_recv}")
        print(f"    Отправлено байт: {current_stats[interface_name].bytes_sent}")
        print(f"    Получено пакетов: {current_stats[interface_name].packets_recv}")
        print(f"    Отправлено пакетов: {current_stats[interface_name].packets_sent}")
        print(f"    Ошибки при приеме: {current_stats[interface_name].errin}")
        print(f"    Ошибки при отправке: {current_stats[interface_name].errout}")
        print("-" * 50)