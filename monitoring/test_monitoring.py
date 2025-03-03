import json
import platform
import threading
import time

from ram.ram_WL import all_ram
from system.system_WL import all_system

if platform.system() == "Linux":
    from cpu.cpu_L import all_cpu
    from disk.disk_L import all_disk
    data = {"monitoring": {}}
elif platform.system() == "Windows":
    from cpu.cpu_W import all_cpu
    from disk.disk_W import all_disk
    from gpu_nvidia.gpuNvidia_W import all_gpu
    data = {"monitoring": {"gpu": all_gpu()}}

class Monitor:
    def __init__(self):
        self.intervals = {
            'cpu': 2,     # Интервал опроса для CPU в секундах
            'ram': 5,     # Интервал опроса для RAM в секундах
            'system': 10  # Интервал опроса для системы в секундах
        }
        self.running = True

    def get_cpu_usage(self):
        """Метод для получения данных о CPU"""
        while self.running:
            # Вызов функции для получения данных о CPU
            cpu_data = self.get_cpu_data()
            print(f"CPU Data: {cpu_data}")
            time.sleep(self.intervals['cpu'])

    def get_ram_usage(self):
        """Метод для получения данных о RAM"""
        while self.running:
            ram_data = all_ram()
            print(f"RAM Data: {ram_data}")
            time.sleep(self.intervals['ram'])

    def get_system_load(self):
        """Метод для получения данных о системе"""
        while self.running:
            system_data = all_system()
            print(f"System Data: {system_data}")
            time.sleep(self.intervals['system'])

    def start_monitoring(self):
        """Запускает мониторинг в отдельных потоках"""
        threading.Thread(target=self.get_cpu_usage).start()
        threading.Thread(target=self.get_ram_usage).start()
        threading.Thread(target=self.get_system_load).start()

    def stop_monitoring(self):
        """Останавливает мониторинг"""
        self.running = False

    def set_interval(self, parameter, interval):
        """Устанавливает новый интервал опроса для заданного параметра"""
        if parameter in self.intervals:
            self.intervals[parameter] = interval
            print(f"Interval for {parameter} set to {interval} seconds.")

    def get_cpu_data(self):
        """Здесь должна быть ваша логика получения данных о CPU"""
        return {"usage": "dummy_cpu_data"}  # Замените на реальную логику

def main():
    monitor = Monitor()
    monitor.start_monitoring()

    # Пример изменения интервала
    time.sleep(15)  # Ждем 15 секунд
    monitor.set_interval('cpu', 5)  # Изменяем интервал опроса для CPU

    # Остановка мониторинга через некоторое время
    time.sleep(30)  # Ждем еще 30 секунд
    monitor.stop_monitoring()

if __name__ == "__main__":
    main()