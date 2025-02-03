import psutil

# Поменять на try

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


print(f"1. Общее количество оперативной памяти в системе: {get_virtual_memory_total()}")
print(f"2. Количество занятой оперативной памяти в системе: {get_virtual_memory_used()}")
print(f"3. Количество свободной оперативной памяти в системе: {get_virtual_memory_free()}")
print(f"4. Общее количество swap-памяти в системе: {get_swap_memory_total()}")
print(f"5. Количество занятой swap-памяти в системе: {get_swap_memory_used()}")
print(f"6. количество свободной swap-памяти в системе: {get_swap_memory_free()}")