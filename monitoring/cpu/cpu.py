import time

import psutil
import subprocess
import platform

class CPUsMonitor:
    def __init__(self):
        self.cpus = {}
        self.cores_info = {}
        self.system = platform.system()
        if self.system == 'Linux':
            cpu_info, self.cores_info = self.__get_linux_info()
            for cpu in cpu_info.keys():
                self.cpus[cpu] = Cpu(cpu_info[cpu]["model_name"], cpu_info[cpu]["physicals_id"])

    def __get_linux_info(self):
        processor_info = {}
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith("processor"):
                    processor_id = line.split(":")[1].strip()
                    processor_info[processor_id] = {}
                elif line.startswith("physical id"):
                    physical_id = line.split(":")[1].strip()
                    processor_info[processor_id]['physical_id'] = physical_id
                elif line.startswith("model name"):
                    model_name = line.split(":")[1].strip()
                    processor_info[processor_id]['model_name'] = model_name
        cpu_info = {}
        cores_info = {}

        for cpu in cpu_info:
            cpu_info[cpu] = {}

        for processor_id, info in processor_info.items():
            # Типа тест на 2 процессора
            if int(processor_id) > 1:
                info["physical_id"] = 1
            if info['physical_id'] not in cpu_info:
                cpu_info[info['physical_id']] = {
                    "model_name": info['model_name'],
                    "physicals_id": []
                }
            cpu_info[info['physical_id']]['physicals_id'].append(processor_id)
            cores_info[processor_id] = info['physical_id']
        return cpu_info, cores_info

    def update(self):
        update_data = {}
        if self.system == 'Linux':
            cores_info = self.__get_core_mpstat_linux()
            load = psutil.cpu_percent(interval=0.5, percpu=True)
            for index_core in range(len(self.cores_info)):
                if self.cores_info[str(index_core)] not in update_data:
                    update_data[self.cores_info[str(index_core)]] = []
                data_line = cores_info[str(index_core)] + [str(load[index_core])]
                update_data[self.cores_info[str(index_core)]].append( {str(index_core): data_line})

            for cpu_key in self.cpus.keys():
                print("CPU", cpu_key)
                self.cpus[cpu_key].update(update_data[cpu_key])

    def __get_core_mpstat_linux(self):
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
            output = {}

    def get_all(self):
        for cpu in self.cpus.keys():
            print("CPU", cpu)
            self.cpus[cpu].get_all()

    def get_item2(self, cpu: str, core: str, metric_id: str):
        try:
            return self.cpus.get(cpu).get_item(core, metric_id)
        except:
            print(f"ошибка - {cpu}: {metric_id}")
            return None

class Cpu:
    def __init__(self, model_name, physicals_id):
        self.model_name = model_name
        self.cores = {}
        self.cores_ids = {}
        for index in range(len(physicals_id)):
            self.cores_ids[physicals_id[index]] = index
            self.cores[str(index)] = Core(physicals_id[index])

    def update(self, update_data):
        for index in update_data:
            idd = list(index.keys())[0]
            self.cores[str(self.cores_ids[idd])].update(index[idd])

    def get_all(self):
        for core in self.cores.keys():
            params = self.cores[core].get_params_all()
            print("Core", core, params)

    def get_item(self, core: str, metric_id: str):
        try:
            return self.cores.get(core).get_metric(metric_id)
        except:
            print(f"ошибка - {core}: {metric_id}")
            return None

class Core:
    def __init__(self, physicals_id):
        self.physicals_id = physicals_id
        self.system = platform.system()
        self.params = {
            'сore.user.time': None,
            'сore.system.time': None,
            'сore.irq.time': None,
            'сore.softirq.time': None,
            'сore.idle.time': None,
            'сore.iowait': None,
            'сore.load': None
        }

    def update(self, update_line):
        print(f"core {self.physicals_id}", update_line)
        if self.system == 'Linux':
            params_new = {
                'сore.user.time': update_line[0],
                'сore.system.time': update_line[2],
                'сore.irq.time': update_line[4],
                'сore.softirq.time': update_line[5],
                'сore.idle.time': update_line[9],
                'сore.iowait': update_line[3],
                'сore.load': update_line[10]
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


time_start = time.time()
aa = CPUsMonitor()
print("init", time.time()-time_start)
print("_"*30)
time_update = time.time()
aa.update()
print("update", time.time()-time_update)
print("_"*30)
time_get_all = time.time()
aa.get_all()
print("get_all", time.time()-time_get_all)
print("_"*30)
time_get_item = time.time()
print(aa.get_item2('0','1', 'сore.idle.time'))
