import psutil

class LvolsMonitor:
    def __init__(self):
        self.lvols = {}
        partitions = psutil.disk_partitions()
        filtered_partitions = self.filter_partitions(partitions)
        for p in filtered_partitions:
            self.lvols[p.mountpoint] = Lvol(p.mountpoint)

    def filter_partitions(self, partitions):
        ignore_words = ['loop', 'snap', 'var/snap', 'docker', 'mnt', 'media']
        filtered = [
            p for p in partitions
            if not any(word in p.mountpoint for word in ignore_words)
        ]
        return filtered

    def update(self):
        for lvol in self.lvols.values():
            lvol.update_params()

    def get_all(self):
        for mountpoint in self.lvols.values():
            aaa = mountpoint.get_params_all()
            print(aaa)

    def get_params_all(self, mountpoint: str):
        try:
            return self.lvols.get(mountpoint).get_params_all()
        except:
            return None

    def get_item(self, mountpoint: str, metric_id:str):
        try:
            return self.lvols.get(mountpoint).get_metric(metric_id)
        except:
            print(f"ошибка - {mountpoint}: {metric_id}")
            return None

class Lvol:
    def __init__(self, mountpoint: str):
        self.mountpoint = mountpoint
        self.params = {
            "lvol.part.mountpoint": mountpoint,
            "lvol.part.total": None,
            "lvol.part.available": None,
            "lvol.part.used": None
        }

    def update_params(self):
        usage = psutil.disk_usage(self.mountpoint)
        total = usage.total if (type(usage.total) == int or type(usage.total) == float) else None
        available = usage.free if (type(usage.free) == int or type(usage.free) == float) else None
        used = usage.used if (type(usage.used) == int or type(usage.used) == float) else None
        result = {
            "lvol.part.total": total,
            "lvol.part.available": available,
            "lvol.part.used": used
        }
        self.params.update(result)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                self.params[metric_id] = None
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            print(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None


a = LvolsMonitor()
a.update()
