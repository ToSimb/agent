import wmi

def get_cpu_temperature():
    try:
        w = wmi.WMI(namespace="root\WMI")
        temperature_info = w.MSAcpi_ThermalZoneTemperature()
        for sensor in temperature_info:
            # Значение температуры передается в десятых долях Кельвина, переводим в Цельсии
            temp_celsius = (sensor.CurrentTemperature / 10.0) - 273.15
            return round(temp_celsius, 2)
        return None
    except Exception as e:
        return f"Ошибка: {e}"

cpu_temp = get_cpu_temperature()
print(f"Температура процессора: {cpu_temp} °C")
