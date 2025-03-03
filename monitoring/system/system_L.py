import os
from .system_WL import (get_uptime, get_virtual_memory_total, get_virtual_memory_used,
                        get_virtual_memory_free, get_swap_memory_total, get_swap_memory_used,get_swap_memory_free)


def get_system_load():
    """Возвращает среднюю загрузку системы"""
    try:
        load1, load5, load15 = os.getloadavg()
        return load1
    except Exception as e:
        print(f"Ошибка сбора параметра 'Средняя загрузка системы': \n{e}")
        return -1

def all_system():
    data = {
        "system_load": get_system_load(),
        "uptime": get_uptime(),
        "total_ram": get_virtual_memory_total(),
        "used_ram": get_virtual_memory_used(),
        "free_ram": get_virtual_memory_free(),
        "total_swap": get_swap_memory_total(),
        "used_swap": get_swap_memory_used(),
        "free_swap": get_swap_memory_free()
    }
    return data


if __name__ == "__main__":
    print(all_system())