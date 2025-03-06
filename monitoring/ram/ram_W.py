import win32com.client
import time

def get_memory_info():
    """Получаем информацию о модулях памяти через WMI"""
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    conn = wmi.ConnectServer(".", "root\\CIMV2")

    query = "SELECT * FROM Win32_PhysicalMemory"
    return conn.ExecQuery(query)


def get_temperature_info():
    """Получаем информацию о температурных датчиках через WMI"""
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    conn = wmi.ConnectServer(".", "root\\CIMV2")

    temperature_query = "SELECT * FROM Win32_TemperatureProbe"
    return conn.ExecQuery(temperature_query)


def all_ram():
    start_time = time.time()
    # Получаем данные о памяти и температурных датчиках
    ram_data = get_memory_info()
    temperature_data = get_temperature_info()

    # Создаем словарь температур для быстрого доступа по DeviceID
    temperature_dict = {
        sensor.DeviceID: sensor.CurrentTemperature / 10.0
        for sensor in temperature_data
    }

    ram_list = []

    for ram in ram_data:
        # Получаем температуру для планки, если она доступна
        temperature = temperature_dict.get(ram.DeviceLocator, "None")

        # Формируем данные для каждой планки
        ram_list.append({
            "Slot": ram.DeviceLocator,
            "Memory": int(ram.Capacity) if ram.Capacity.isdigit() else -1,
            "Manufacturer": ram.Manufacturer,
            "Model": ram.PartNumber.strip(),
            "Maximum Frequency": ram.Speed,
            "Voltage": ram.ConfiguredVoltage,
            "Min Voltage": ram.MinVoltage,
            "Max Voltage": ram.MaxVoltage ,
            "Temperature": int(temperature) if temperature.isdigit() else -1,
        })
    print("Время сбора параметров RAM:", time.time() - start_time)
    return ram_list


if __name__ == "__main__":
    # Выводим все данные о планках памяти
    for ram_info in all_ram():
        print(ram_info)
