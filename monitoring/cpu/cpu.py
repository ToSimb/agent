import time
import psutil
import subprocess
import platform

class CPUsMonitor:
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
            cpus_name (dict): Словарь, где ключ - физический идентификатор процессора (сокета),
                            а значением - название модели процессора.
                            Пример: {'0': 'AMD Ryzen 5 3600X 6-Core Processor',
                                    '1': 'AMD Ryzen 5 3600X 6-Core Processor'}
            cores (dict): Словарь, где ключ - идентификатор процессора (логического потока),
                            а значением - объект класса Core, представляющий ядро процессора.
                            Пример: {'0': <__main__.Core object at 0x79853a7bdee0>,
                                     '1': <__main__.Core object at 0x79853a654d60>}
            cores_info (dict): Словарь, где ключ - идентификатор процессора (логического потока),
                               а значением - строка, представляющая информацию о его месте в системе.
                               Пример: {'0': 'cpu:0:0', '1': 'cpu:0:1', ...}
            item_index: Словарь, где ключ - это будущий item_id из схемы,
                        а значением - объект класса Core.
                        (по факту мы делаем новые ссылки на объекты)
                        Пример: {'12': <__main__.Core object at 0x79853a7bdee0>,
                                '13': <__main__.Core object at 0x79853a654d60>}
            system (str): Название операционной системы (например, 'Linux').
        """
        self.cpus_name = {}
        self.cores = {}
        self.cores_info = {}
        self.item_index = {}
        self.system = platform.system()
        if self.system == 'Linux':
            cores_infor = self.__get_linux_info()
            for core_line in cores_infor:
                if core_line["physical_id"] not in self.cpus_name:
                    self.cpus_name[core_line["physical_id"]] = core_line["model_name"]
                self.cores[core_line['processor_id']] = Core()
                self.cores_info[core_line['processor_id']] = f"cpu:{core_line['physical_id']}:{core_line['physical_core_id']}"

    def __get_linux_info(self):
        """
        Получает информацию о процессорах из файла /proc/cpuinfo.

        Возвращает:
            list: Список словарей, каждый из которых содержит информацию о процессоре.
                  Пример формата выходных данных:
                  {'processor_id': '0', 'model_name': 'AMD Ryzen ..', 'physical_id': '0', 'physical_core_id': '0'}
                  {'processor_id': '1', 'model_name': 'AMD Ryzen ..', 'physical_id': '0', 'physical_core_id': '1'}
                  ...
        """
        with open('/proc/cpuinfo', 'r') as f:
            processor_info = []
            current_processor = {}
            count_processor = {}
            for line in f:
                if line.startswith("processor"):
                    if current_processor:
                        processor_info.append(current_processor)
                        current_processor = {}
                    current_processor['processor_id'] = line.split(":")[1].strip()
                elif line.startswith("physical id"):
                    current_processor['physical_id'] = line.split(":")[1].strip()

                    # *!*!*!*!* ДЛЯ ТЕСТИРОВАНИЯ *!*!*!*!*
                    # if int(current_processor['processor_id']) > 1:
                    #     current_processor['physical_id'] = str(int(line.split(":")[1].strip())+1)
                    # else:
                    #     current_processor['physical_id'] = line.split(":")[1].strip()

                    #для разделения по core внутри cpu
                    if current_processor['physical_id'] not in count_processor:
                        count_processor[current_processor['physical_id']] = 0
                    current_processor["physical_core_id"] = str(count_processor[current_processor['physical_id']])
                    count_processor[current_processor['physical_id']] += 1

                elif line.startswith("model name"):
                    current_processor['model_name'] = line.split(":")[1].strip()
            if current_processor:
                processor_info.append(current_processor)
        return processor_info

    def get_objects_description(self):
        return self.cores_info

    def create_index(self, cpu_dict):
        """
        Пример cpu_dict:
            {
                "cpu:0:0": 12,
                "cpu:0:1": 13,
                "cpu:0:2": 14,
                "cpu:0:3": null
            }
        """
        print(cpu_dict)
        for index in cpu_dict:
            if cpu_dict[index] is not None:
                for key, value in self.cores_info.items():
                    if value == index:
                        self.item_index[str(cpu_dict[index])] = self.cores.get(key, None)
                        break
                else:
                    print(f'Для индекса {index} нет значения')
        print("Индексы для CPU обновлены")

    def update(self):
        """
        Обновляет информацию о загрузке процессоров.

        Описание data_line для Linux:
        proc_id ['%usr', '%nice', '%sys', '%iowait', '%irq', '%soft', '%steal', '%guest', '%gnice', '%idle', '%load']
        Пример вывода:
            0 ['5,20', '0,00', '0,46', '0,17', '0,00', '0,05', '0,00', '0,00', '0,00', '94,12', '2.0']
            1 ['5,28', '0,02', '0,39', '0,25', '0,00', '0,00', '0,00', '0,00', '0,00', '94,06', '3.9']
        """
        if self.system == 'Linux':
            cores_info = self.__get_core_mpstat_linux()
            load = psutil.cpu_percent(interval=0.5, percpu=True)
            for index_core in range(len(self.cores_info)):
                data_line = cores_info[str(index_core)] + [str(load[index_core])]
                self.cores[str(index_core)].update(data_line)
            print(time.time(), "Выполнено обновление CPU")

    def __get_core_mpstat_linux(self):
        """
        Получает информацию о загрузке процессоров с помощью команды mpstat.

        Обрабатывает:
            columns (list):
                Формат:
                    ['16:59:27', 'CPU', '%usr', '%nice', '%sys', '%iowait', '%irq', '%soft', '%steal', '%guest', '%gnice', '%idle']
                Пример формата выходных данных:
                {
                    ['16:59:27', 'all', '1,63', '0,05', '0,29', '0,25', '0,00', '0,01', '0,00', '0,00', '0,00', '97,77']
                    ['16:59:27', '0', '1,68', '0,07', '0,27', '0,25', '0,00', '0,02', '0,00', '0,00', '0,00', '97,71']
                }

        Возвращает:
            dict: {
                  'all': ['1,63', '0,05', '0,29', '0,25', '0,00', '0,01', '0,00', '0,00', '0,00', '97,77'],
                  '0': ['1,68', '0,07', '0,27', '0,25', '0,00', '0,02', '0,00', '0,00', '0,00', '97,71'],
                  '1': ['1,63', '0,06', '0,37', '0,25', '0,00', '0,00', '0,00', '0,00', '0,00', '97,69'],
              }
        """
        try:
            output = {}
            result = subprocess.run(['mpstat', '-P', 'ALL', '0'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if line:
                    columns = line.split()
                    if len(columns) > 10:
                        output[columns[1]] = columns[2:]
            return output
        except Exception as e:
            print(f"Ошибка при выполнении команды mpstat: {e}")
            return {}

    def get_all(self):
        return_list = []
        for index_cores in self.cores.keys():
            result = self.cores[index_cores].get_params_all()
            return_list.append({index_cores: result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            print(f"ошибка - {item_id}: {metric_id} - {e}")
            return None

    def get_item_origin(self, core: str, metric_id: str):
        try:
            return self.cores.get(core).get_metric(metric_id)
        except Exception as e:
            print(f"ошибка - {core}: {metric_id} - {e}")
            return None

class Core:
    def __init__(self):
        self.system = platform.system()
        self.params = {
            'core.user.time': None,
            'core.system.time': None,
            'core.irq.time': None,
            'core.softirq.time': None,
            'core.idle.time': None,
            'core.iowait': None,
            'core.load': None
        }

    def update(self, update_line):
        if self.system == 'Linux':
            params_new = {
                'core.user.time': update_line[0],
                'core.system.time': update_line[2],
                'core.irq.time': update_line[4],
                'core.softirq.time': update_line[5],
                'core.idle.time': update_line[9],
                'core.iowait': update_line[3],
                'core.load': update_line[10]
            }
            self.params.update(params_new)

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
