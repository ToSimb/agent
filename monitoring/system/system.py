import time
import psutil


class SystemMonitor:
    def __init__(self):
        self.params = {
            "chassis.uptime": None,
            "chassis.core.count": None,
            "chassis.logic.count": None,
            "chassis.load.avg": None,
            "chassis.irq": None,
            "chassis.memory.total": None,
            "chassis.memory.used": None,
            "chassis.memory.available": None,
            "chassis.swap.total": None,
            "chassis.swap.used": None,
            "chassis.swap.available": None
        }

    def update(self):
        uptime = psutil.boot_time()
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        load_avg = psutil.cpu_percent(interval=0.1)
        core_count = psutil.cpu_count(logical=False)
        logic_count = psutil.cpu_count(logical=True)
        cpu_stats = psutil.cpu_stats()

        # через ASUNCIO
        # uptime = await asyncio.to_thread(psutil.boot_time)
        # vm = await asyncio.to_thread(psutil.virtual_memory)
        # swap = await asyncio.to_thread(psutil.swap_memory)
        # load_avg = await asyncio.to_thread(psutil.cpu_percent, interval=0.1)
        # core_count = await asyncio.to_thread(psutil.cpu_count, logical=False)
        # logic_count = await asyncio.to_thread(psutil.cpu_count, logical=True)
        # cpu_stats = await asyncio.to_thread(psutil.cpu_stats)

        result = {
            "chassis.uptime": int(time.time() - uptime),
            "chassis.core.count": core_count,
            "chassis.logic.count": logic_count,
            "chassis.load.avg": load_avg,
            "chassis.irq": cpu_stats.interrupts,
            "chassis.memory.total": vm.total,
            "chassis.memory.used": vm.used,
            "chassis.memory.available": vm.free,
            "chassis.swap.total": swap.total,
            "chassis.swap.used": swap.used,
            "chassis.swap.available": swap.free
        }
        self.params.update(result)

    def get_all(self):
        return self.params

    def get_metrics(self, metric_id: str):
        return self.params.get(metric_id, None)