import psutil
from concurrent.futures import ThreadPoolExecutor


def get_system_info_parallel():
    """Параллельно собирает информацию о системе с минимальными накладными расходами, отдельно обрабатывая swap память"""
    with ThreadPoolExecutor() as executor:
        future_uptime = executor.submit(lambda: psutil.time.time() - psutil.boot_time())
        future_vm = executor.submit(psutil.virtual_memory)
        future_cpu_load = executor.submit(psutil.cpu_percent, 0)
        future_cpu_stats = executor.submit(psutil.cpu_stats)
        future_physical_cores = executor.submit(psutil.cpu_count, logical=False)
        future_logical_cores = executor.submit(psutil.cpu_count, logical=True)

    # Запускаем swap_memory в отдельном потоке, чтобы он не задерживал остальные операции
    with ThreadPoolExecutor(max_workers=1) as swap_executor:
        future_swap = swap_executor.submit(psutil.swap_memory)

    uptime_seconds = int(future_uptime.result())
    vm = future_vm.result()
    swap = future_swap.result()
    cpu_load = future_cpu_load.result()
    cpu_stats = future_cpu_stats.result()
    physical_cores = future_physical_cores.result()
    logical_cores = future_logical_cores.result()

    return {
        "uptime_seconds": uptime_seconds,
        "virtual_memory_total": vm.total,
        "virtual_memory_used": vm.used,
        "virtual_memory_free": vm.free,
        "swap_memory_total": swap.total,
        "swap_memory_used": swap.used,
        "swap_memory_free": swap.free,
        "cpu_load_percent": cpu_load,
        "physical_cores": physical_cores,
        "logical_cores": logical_cores,
        "interrupts": cpu_stats.interrupts
    }
