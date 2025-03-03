import psutil


def get_virtual_memory_total():
    """Возвращает общее количество оперативной памяти в системе"""
    try:
        return psutil.virtual_memory().total
    except Exception as e:
        print(f"Ошибка сбора параметра \"Общее количество оперативной памяти в системе\": \n{e}")
        return -1


def get_virtual_memory_used():
    """Возвращает количество занятой оперативной памяти в системе"""
    try:
        return psutil.virtual_memory().used
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество занятой оперативной памяти в системе\": \n{e}")
        return -1


def get_virtual_memory_free():
    """Возвращает количество свободной оперативной памяти в системе"""
    try:
        return psutil.virtual_memory().free
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество свобоной оперативной памяти в системе\": \n{e}")
        return -1


def get_swap_memory_total():
    """Возвращает общее количество swap-памяти в системе"""
    try:
        return psutil.swap_memory().total
    except Exception as e:
        print(f"Ошибка сбора параметра \"Общее количество swap-памяти в системе\": \n{e}")
        return -1


def get_swap_memory_used():
    """Возвращает количество занятой swap-памяти в системе"""
    try:
        return psutil.swap_memory().used
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество занятой swap-памяти в системе\": \n{e}")
        return -1


def get_swap_memory_free():
    """Возвращает количество свободной swap-памяти в системе"""
    try:
        return psutil.swap_memory().free
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество свободной swap-памяти в системе\": \n{e}")
        return -1


def all_ram():
    data = {
        "total_ram": get_virtual_memory_total(),
        "used_ram": get_virtual_memory_used(),
        "free_ram": get_virtual_memory_free(),
        "total_swap": get_swap_memory_total(),
        "used_swap": get_swap_memory_used(),
        "free_swap": get_swap_memory_free(),
    }
    return data

if __name__ == "__main__":
    print(all_ram())