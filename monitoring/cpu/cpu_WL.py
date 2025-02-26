import psutil

def get_cpu_physical_core_count():
    """Возвращает количество физических ядер"""
    try:
        return psutil.cpu_count(logical=False)
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество физических ядер\": \n{e}")
        return -1


def get_cpu_logical_core_count():
    """Возвращает количество логических ядер"""
    try:
        return psutil.cpu_count(logical=True)
    except Exception as e:
        print(f"Ошибка сбора параметра \"Количество логических ядер\": \n{e}")
        return -1
