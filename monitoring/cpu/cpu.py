import time
import psutil
import subprocess
import platform
import ctypes
from ctypes import wintypes, byref, POINTER, cast
from monitoring.base import BaseObject, SubObject

from logger.logger_mon_cpu import logger_monitoring

class CPUsMonitor(BaseObject):
    def __init__(self):
        """
        Инициализация экземпляра класса.

        Атрибуты:
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
        super().__init__()
        self.cores = {}
        self.cores_info = {}
        self.item_index = {}
        self.system = platform.system()
        if self.system == 'Linux':
            cores_infor = self.__get_linux_info()
            for core_line in cores_infor:
                self.cores[core_line['processor_id']] = Core()
                self.cores_info[core_line['processor_id']] = f"cpu:{core_line['physical_id']}:{core_line['logical_core_in_physical_id']}"
        elif self.system == 'Windows':
            cores_infor = self.__get_windows_info()
            for core_line in cores_infor:
                self.cores[core_line['processor_id']] = Core()
                self.cores_info[core_line['processor_id']] = f"cpu:{core_line['physical_id']}:{core_line['logical_core_in_physical_id']}"

    @staticmethod
    def __get_linux_info():
        """
        Получает информацию о процессорах из файла /proc/cpuinfo.

        Возвращает:
            list: Список словарей, каждый из которых содержит информацию о процессоре.
                  Пример формата выходных данных:
                  {'processor_id': '0', 'model_name': 'AMD Ryzen ..', 'physical_id': '0', 'logical_core_in_physical_id': '0'}
                  {'processor_id': '1', 'model_name': 'AMD Ryzen ..', 'physical_id': '0', 'logical_core_in_physical_id': '1'}
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

                    #для разделения по core внутри cpu
                    if current_processor['physical_id'] not in count_processor:
                        count_processor[current_processor['physical_id']] = 0
                    current_processor["logical_core_in_physical_id"] = str(count_processor[current_processor['physical_id']])
                    count_processor[current_processor['physical_id']] += 1

                elif line.startswith("model name"):
                    current_processor['model_name'] = line.split(":")[1].strip()
            if current_processor:
                processor_info.append(current_processor)
        return processor_info

    def __get_windows_info(self):
        """
        Получает информацию о процессорах.

        Возвращает:
            list: Список словарей, каждый из которых содержит информацию о процессоре.
                  Пример формата выходных данных:
                  {'processor_id': '0', 'model_name': 'AMD Ryzen ..', 'physical_id': '0', 'logical_core_in_physical_id': '0'}
                  {'processor_id': '1', 'model_name': 'AMD Ryzen ..', 'physical_id': '0', 'logical_core_in_physical_id': '1'}
                  ...
        """
        DWORD = wintypes.DWORD
        WORD = wintypes.WORD
        BYTE = wintypes.BYTE
        ULONG_PTR = wintypes.WPARAM
        RELATION_PROCESSOR_PACKAGE = 3

        class GROUP_AFFINITY(ctypes.Structure):
            _fields_ = [("Mask", ULONG_PTR),
                        ("Group", WORD),
                        ("Reserved", WORD * 3)]

        class PROCESSOR_RELATIONSHIP(ctypes.Structure):
            _fields_ = [("Flags", BYTE),
                        ("EfficiencyClass", BYTE),
                        ("Reserved", BYTE * 20),
                        ("GroupCount", WORD),
                        ("GroupMask", GROUP_AFFINITY * 1)]

        class SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX(ctypes.Structure):
            _fields_ = [("Relationship", wintypes.INT),
                        ("Size", DWORD),
                        ("Processor", PROCESSOR_RELATIONSHIP)]

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.GetLogicalProcessorInformationEx.argtypes = (
            wintypes.INT,
            ctypes.c_void_p,
            POINTER(DWORD)
        )
        kernel32.GetLogicalProcessorInformationEx.restype = wintypes.BOOL
        cpu_names = self.__get_windows_cpu_names()
        length = DWORD(0)
        res = kernel32.GetLogicalProcessorInformationEx(RELATION_PROCESSOR_PACKAGE, None, byref(length))
        buf = ctypes.create_string_buffer(length.value)
        res = kernel32.GetLogicalProcessorInformationEx(RELATION_PROCESSOR_PACKAGE, buf, byref(length))
        if not res:
            raise ctypes.WinError(ctypes.get_last_error())
        offset = 0
        cores_info = []
        socket_index = 0
        while offset < length.value:
            info = cast(ctypes.byref(buf, offset), POINTER(SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX)).contents
            if info.Relationship == RELATION_PROCESSOR_PACKAGE:
                group_count = info.Processor.GroupCount
                group_array_type = GROUP_AFFINITY * group_count
                group_array = cast(info.Processor.GroupMask, POINTER(group_array_type)).contents
                logical_core_in_physical_id = 0
                model_name = cpu_names[str(socket_index)] if socket_index < len(cpu_names) else None
                for group_affinity in group_array:
                    group_id = group_affinity.Group
                    mask = group_affinity.Mask
                    core = 0
                    while mask:
                        if mask & 1:
                            logical_cpu_id = core + (group_id * 64)
                            current_core = {'processor_id': str(logical_cpu_id),
                                            'model_name': model_name,
                                            'physical_id': str(socket_index),
                                            'logical_core_in_physical_id': str(logical_core_in_physical_id)}
                            cores_info.append(current_core)
                            logical_core_in_physical_id += 1
                        mask >>= 1
                        core += 1
            offset += info.Size
            socket_index += 1
        return cores_info

    @staticmethod
    def __get_windows_cpu_names():
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'DeviceID,Name'],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().splitlines()
            lines = [line.strip() for line in lines if line.strip()]
            cpu_names = {}
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split(None, 1)
                if len(parts) == 2:
                    cpu_names.update({parts[0].strip().replace('CPU', ''): parts[1].strip()})
            return cpu_names
        except Exception as e:
            logger_monitoring.error(f"Ошибка получения списка процессоров с помощью wmic: {e}")
            return []

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
        for index in cpu_dict:
            if cpu_dict[index] is not None:
                for key, value in self.cores_info.items():
                    if value == index:
                        self.item_index[str(cpu_dict[index])] = self.cores.get(key, None)
                        break
                else:
                    logger_monitoring.debug(f'Для индекса {index} нет значения')
        logger_monitoring.info("Индексы для CPU обновлены")

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
        elif self.system == 'Windows':
            cores_info = self.__get_core_wmic_windows()
            for i, core in self.cores.items():
                if i in cores_info.keys():
                    core.update(cores_info[i])

    @staticmethod
    def __get_core_mpstat_linux():
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
            result = subprocess.run(['mpstat', '-P', 'ALL', '1', '1'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if line:
                    columns = line.split()
                    if len(columns) > 10:
                        # ОСОБЕННОСТЬ !! В Debian может время быть в формате времени PM/AM
                        # по этому надо делать срезку такую: output[columns[2]] = columns[3:]
                        output[columns[1]] = columns[2:]
            return output
        except Exception as e:
            logger_monitoring.error(f"Ошибка при выполнении команды mpstat: {e}")
            return {}

    @staticmethod
    def __get_core_wmic_windows():
        """
        Получает информацию о загрузке процессоров с помощью команды wmic.

        Возвращает:
        # name: core.softirq.time, core.idle.time, core.irq.time, core.system.time, core.load, core.user.time
            dict: {
                  '0': ['1,68', '0,07', '0,27', '0,25', '0,00', '0,02'],
                  '1': ['1,63', '0,06', '0,37', '0,25', '0,00', '0,00'],
                  ...
              }
        """
        cmd = [
            'wmic', 'path', 'Win32_PerfFormattedData_PerfOS_Processor', 'get',
            'Name,PercentProcessorTime,PercentUserTime,PercentPrivilegedTime,'
            'PercentInterruptTime,PercentDPCTime,PercentIdleTime'
        ]
        output = subprocess.check_output(cmd, text=True, encoding='utf-8', errors='ignore')

        lines = output.splitlines()
        headers = lines[0].split()

        cpu_entries = [
            line.split() for line in lines[1:]
            if line and not line.startswith('_Total')
        ]

        result = {
            values[0]: [values[i] for i in range(1, 7)]
            for values in cpu_entries if len(values) == len(headers)
        }
        return result

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
            logger_monitoring.error(f"Ошибка при вызове item_id - {item_id}: {metric_id} - {e}")
            return None


class Core(SubObject):
    def __init__(self):
        super().__init__()
        self.system = platform.system()
        self.params = {
            'core.user.time': None,
            'core.system.time': None,
            'core.irq.time': None,
            'core.softirq.time': None,
            'core.idle.time': None,
            'core.iowait.time': None,
            'core.load': None
        }

    def update(self, update_line=None):
        params_new = {}
        if self.system == 'Linux':
            params_new = {
                'core.user.time': update_line[0],
                'core.system.time': update_line[2],
                'core.irq.time': update_line[4],
                'core.softirq.time': update_line[5],
                'core.idle.time': update_line[9],
                'core.iowait.time': update_line[3],
                'core.load': update_line[10]
            }
        elif self.system == 'Windows':
            params_new = {
                'core.user.time': update_line[5],
                'core.system.time': update_line[3],
                'core.irq.time': update_line[2],
                'core.softirq.time': update_line[0],
                'core.idle.time': update_line[1],
                'core.iowait.time': None,
                'core.load': update_line[4]
            }
        self.params.update(params_new)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            if metric_id in self.params:
                result = self.params[metric_id]
                if result is not None:
                    self.params[metric_id] = None
                    result = self.validate_double(result)
                return result
            else:
                raise KeyError(f"Ключ не найден в словаре.")
        except Exception as e:
            logger_monitoring.error(f"Ошибка в запросе метрики {metric_id} - {e}")
            return None