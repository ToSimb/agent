import psutil
from monitoring.base import BaseObject, SubObject

from logger.logger_monitoring import logger_monitoring

class LvolsMonitor(BaseObject):
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            lvols (dict): Словарь, где ключ - место монтирование,
                            а значением - объект класса Lvol.
                            Пример: {'/': <__main__.Lvol object at 0x7e1c0d7bdac0>,
                                     '/boot/efi': <__main__.Lvol object at 0x7e1c0d7a8f10>}
            lvols_info (dict): Словарь, где ключ - индекс с нуля по порядку,
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'/': 'lvol:0', '/boot/efi': 'lvol:1'}
            item_index: Словарь, где ключ - это будущий item_id из схемы,
                        а значением - объект класса Lvol.
                        (по факту мы делаем новые ссылки на объекты)
                        Пример: {'52': <__main__.Lvol object at 0x7e1c0d7bdac0>,
                                '53': <__main__.Lvol object at 0x7e1c0d7a8f10>}
        """
        super().__init__()
        self.lvols = {}
        self.lvols_info = {}
        self.item_index = {}
        partitions = psutil.disk_partitions()
        filtered_partitions = self.__filter_partitions(partitions)
        index_lvol = 0
        for p in filtered_partitions:
            self.lvols[p.mountpoint] = Lvol(p.mountpoint)
            self.lvols_info[p.mountpoint] = f"lvol:{index_lvol}"
            index_lvol += 1


    @staticmethod
    def __filter_partitions(partitions):
        ignore_words = ['loop', 'snap', 'var/snap', 'docker', 'mnt', 'media', 'nfs']
        filtered = [
            p for p in partitions
            if not any(word in p.mountpoint for word in ignore_words)
        ]
        return filtered

    def get_objects_description(self):
        return self.lvols_info

    def create_index(self, lvol_dict):
        """
        Пример lvol_dict:
            {
                "lvol:/": 72,
                "lvol:/boot/efi": 73,
            }
        """
        for index in lvol_dict:
            if lvol_dict[index] is not None:
                for key, value in self.lvols_info.items():
                    if value == index:
                        self.item_index[str(lvol_dict[index])] = self.lvols.get(key, None)
                        break
                else:
                    logger_monitoring.debug(f'Для индекса {index} нет значения')
        logger_monitoring.info("Индексы для LVOLs обновлены")

    def update(self):
        for lvol in self.lvols.values():
            lvol.update()

    def get_all(self):
        return_list = []
        for index_lvol in self.lvols.keys():
            result = self.lvols[index_lvol].get_params_all()
            return_list.append({index_lvol :result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            logger_monitoring.error(f"Ошибка при вызове item_id  - {item_id}: {metric_id} - {e}")
            return None


class Lvol(SubObject):
    def __init__(self, mountpoint: str):
        super().__init__()
        self.mountpoint = mountpoint
        self.params = {
            "lvol.part.mountpoint": mountpoint,
            "lvol.part.total": None,
            "lvol.part.available": None,
            "lvol.part.used": None
        }

    def update(self):
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
                if result is not None:
                    if metric_id in ["lvol.part.mountpoint"]:
                        result = self.validate_string(result)
                    else:
                        self.params[metric_id] = None
                        result = self.validate_integer(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None