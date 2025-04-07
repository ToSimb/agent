import json
from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData
from pysnmp.hlapi import ObjectType, ObjectIdentity, nextCmd, getCmd
from base import BaseObject
from base import SubObject

class Switch(BaseObject):
    def __init__(self, ip: str, file_path: str = "switches.json"):
        super().__init__()
        self.ip = ip
        self.system_id = None
        self.model = None
        self.snmp_port = None
        self.oids_map = {}
        self.community = None
        self.interfaces = {}
        self.interfaces_info = {}
        self.item_index = {}

        config = self.__load_config(file_path)
        if not config:
            print(f"Не удалось загрузить конфигурацию коммутатора {ip} из {file_path}")
            return

        current_switch = next((dt for dt in config.get("switches", []) if dt.get("ip", "") == ip), None)
        if not current_switch:
            print(f"Коммутатор с IP {ip} не найден в конфигурации.")
            return

        self.model = current_switch.get("model", "")
        self.snmp_port = current_switch.get("snmp_port", 161)
        self.oids_map = current_switch.get("OIDs", {})
        self.community = current_switch.get("community", "public")
        self.system_id = config.get("switches", []).index(current_switch)
        print(f"Порядковый номер коммутатора в системе {self.system_id}")

        if len(self.oids_map) != 6:
            print(f"В файле конфигурации указано не верное количество параметров для {self.ip}.")

        if not self.__check_switch_status():
            return

        index_interface = self.__get_switch_interfaces()
        if not index_interface:
            print(f"Ошибка на коммутаторе: {self.ip}. Интерфейсы не найдены!")
            return

        for index in index_interface:
            self.interfaces[index] = Interface()
            self.interfaces_info[index] = f"switch:{self.system_id}:{index}"


    @staticmethod
    def __load_config(file_path: str):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл конфигурации коммутаторов не найден: {file_path}")
        except json.JSONDecodeError as e:
            print(f"Ошибка разбора JSON в файле коммутаторов {file_path}: {e}")
        return None

    def __check_switch_status(self):
        """"
        Проверяет работу SNMP на коммутаторе.
        Возвращает true или false.
        """
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),
            UdpTransportTarget((self.ip, self.snmp_port), timeout=2.0, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'))  # sysUpTime
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            print(f"Ошибка доступа коммутатора {self.ip}: {errorIndication}")
            return False
        elif errorStatus:
            print(f"Ошибка доступа коммутатора {self.ip}: {errorStatus.prettyPrint()}")
            return False
        else:
            return True

    def __get_switch_interfaces(self):
        """
        Получает количество сетевых интерфейсов и их идентификаторы (ifIndex) с коммутатора по SNMP.

        :return: список ifIndex
        """
        interfaces = []
        # SNMP OID для ifIndex: 1.3.6.1.2.1.2.2.1.1
        oid_if_index = ObjectIdentity('1.3.6.1.2.1.2.2.1.1')
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in nextCmd(SnmpEngine(),
                                  CommunityData(self.community, mpModel=1),
                                  UdpTransportTarget((self.ip, self.snmp_port), timeout=1, retries=2),
                                  ContextData(),
                                  ObjectType(oid_if_index),
                                  lexicographicMode=False):

            if errorIndication:
                print(f"SNMP ошибка на {self.ip} при получении списка интерфейсов: {errorIndication}")
                break
            elif errorStatus:
                print(f"SNMP ошибка на {self.ip}  при получении списка интерфейсов: {errorStatus.prettyPrint()}")
                break
            else:
                for varBind in varBinds:
                    oid, value = varBind
                    interfaces.append(str(value))
        return interfaces

    def get_objects_description(self):
        return self.interfaces_info

    def create_index(self, switch_dict):
        for index in switch_dict:
            if switch_dict[index] is not None:
                for key, value in self.interfaces_info.items():
                    if value == index:
                        self.item_index[str(switch_dict[index])] = self.interfaces_info.get(key, None)
                        break
            else:
                print(f'Для индекса {index} нет значения')
        print("Индексы для коммутаторов обновлены")

    def update(self):
        result = {}
        for oid_base, metric_name in self.oids_map.items():
            oid_obj = ObjectIdentity(oid_base)

            for (errorIndication,
                 errorStatus,
                 errorIndex,
                 varBinds) in nextCmd(SnmpEngine(),
                                      CommunityData(self.community, mpModel=1),
                                      UdpTransportTarget((self.ip, self.snmp_port), timeout=1, retries=2),
                                      ContextData(),
                                      ObjectType(oid_obj),
                                      lexicographicMode=False):

                if errorIndication:
                    print(f"SNMP ошибка на {self.ip}: {errorIndication} при выполнении update")
                    break
                elif errorStatus:
                    print(f"SNMP ошибка на {self.ip}: {errorStatus.prettyPrint()}при выполнении update")
                    break
                else:
                    for varBind in varBinds:
                        oid, value = varBind
                        if_index = str(oid).split('.')[-1]
                        if if_index not in result:
                            result[if_index] = {}
                        result[if_index][metric_name] = int(value)

        for interface_index, result_line in result:
            self.interfaces.get(interface_index).update(result_line)


    def get_all(self):
        return_list = []
        for interface_index in self.interfaces.keys():
            result = self.interfaces[interface_index].get_params_all()
            return_list.append({interface_index: result})
        return return_list

    def get_item_and_metric(self, item_id: str, metric_id:str):
        try:
            return self.item_index.get(item_id).get_metric(metric_id)
        except Exception as e:
            print(f"Ошибка - {item_id}: {metric_id} - {e}")
            return None

class Interface(SubObject):
    def __init__(self):
        super().__init__()
        self.params = {
            "if.in.bytes":    None,
            "if.in.packets":  None,
            "if.out.errors":  None,
            "if.out.bytes":   None,
            "if.out.packets": None,
            "if.in.errors":   None
        }

    def update(self, params_new: dict):
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