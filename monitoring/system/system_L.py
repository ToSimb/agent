from .system_WL import get_system_info_parallel
import time


def all_system():
    """Собирает всю информацию о системе"""
    start_time = time.time()
    data = get_system_info_parallel()
    print("Время сбора параметров SYSTEM:", time.time() - start_time)
    return data


if __name__ == "__main__":
    print(all_system())
