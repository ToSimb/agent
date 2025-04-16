import json
import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, getCmd, nextCmd
)
from monitoring.base import BaseObject, SubObject


class Switch(BaseObject):
    def __init__(self, ip: str, file_path: str = "switches.json"):
        super().__init__()
        self.ip = ip
        self.system_id = None
        self.model = None
        self.snmp_port = 161
        self.oids_map = {}
        self.community = "public"
        self.interfaces = {}
        self.interfaces_info = {}
        self.item_index = {}
        self.index_interface = {}
        self.connection_value = None
        self.connection_id = -1

        config = self.__load_config(file_path)
        if not config:
            print(f"Не удалось загрузить конфигурацию коммутатора {ip} из {file_path}")
            return

        current_switch = next((dt for dt in config.get("switches", []) if dt.get("ip") == ip), None)
        if not current_switch:
            print(f"Коммутатор с IP {ip} не найден в конфигурации.")
            return

        self.model = current_switch.get("model", "")
        self.snmp_port = current_switch.get("snmp_port", 161)
        self.oids_map = current_switch.get("OIDs", {})
        self.community = current_switch.get("community", "public")
        self.system_id = current_switch.get("scheme_number", "")
        print(f"Порядковый номер коммутатора в системе: {self.system_id}")

    @staticmethod
    def __load_config(file_path: str):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки конфигурации: {e}")
        return None

    async def init_async(self):
        """ Асинхронная инициализация """
        if len(self.oids_map) != 6:
            print(f"Неверное количество OID для {self.ip}")
            return

        if not await self.__check_switch_status():
            print(f"SNMP недоступен на {self.ip}")
            return

        self.connection_value = True
        self.index_interface = await self.__get_switch_interfaces()

        if not self.index_interface:
            print(f"Интерфейсы не найдены для {self.ip}")
            return

        for index in self.index_interface.values():
            self.interfaces[index] = Interface()
            self.interfaces_info[index] = f"switch:{self.system_id}:{index}"
        self.interfaces_info['connection'] = "switch:connection"

    async def __check_switch_status(self) -> bool:
        """ Проверка SNMP (sysUpTime) """
        engine = SnmpEngine()
        errorIndication, errorStatus, _, _ = await getCmd(
            engine,
            CommunityData(self.community, mpModel=1),
            UdpTransportTarget((self.ip, self.snmp_port), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'))
        )
        return not (errorIndication or errorStatus)

    async def __get_switch_interfaces(self) -> dict:
        """ Получение интерфейсов (ifDescr) """
        interfaces = {}
        engine = SnmpEngine()
        async for (errorIndication, errorStatus, _, varBinds) in nextCmd(
            engine,
            CommunityData(self.community, mpModel=1),
            UdpTransportTarget((self.ip, self.snmp_port), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.2')),
            lexicographicMode=False
        ):
            if errorIndication or errorStatus:
                print(f"Ошибка получения интерфейсов {self.ip}: {errorIndication or errorStatus.prettyPrint()}")
                break
            for oid, value in varBinds:
                index = str(oid).split('.')[-1]
                name = str(value)

                if self.model in ['Mellanox SX6700', 'Mellanox MSX6012F-2BFS']:
                    if 'IB' in name:
                        name = name.split('/')[-1]
                        interfaces[index] = name
                elif self.model == "D-Link DGS-1210-28X/ME":
                    if 'D-Link' in name:
                        interfaces[index] = name.split()[-1]
                else:
                    print(f"Модель {self.model} не поддерживается.")
        return interfaces

    def get_objects_description(self):
        return self.interfaces_info

    def create_index(self, switch_dict):
        for index, value in switch_dict.items():
            if value is not None:
                if index == 'connection':
                    self.connection_id = value
                else:
                    for key, iface in self.interfaces_info.items():
                        if iface == index:
                            self.item_index[str(value)] = self.interfaces_info.get(key)
                            break

    async def update(self):
        """ Асинхронное обновление данных интерфейсов """
        result = {}
        engine = SnmpEngine()

        for oid_base, metric_name in self.oids_map.items():
            oid = ObjectIdentity(oid_base)

            async for (errorIndication, errorStatus, _, varBinds) in nextCmd(
                engine,
                CommunityData(self.community, mpModel=1),
                UdpTransportTarget((self.ip, self.snmp_port), timeout=2, retries=1),
                ContextData(),
                ObjectType(oid),
                lexicographicMode=False
            ):
                if errorIndication or errorStatus:
                    print(f"Ошибка получения {oid_base} от {self.ip}: {errorIndication or errorStatus.prettyPrint()}")
                    break

                for oid_var, value in varBinds:
                    index = str(oid_var).split('.')[-1]
                    iface_index = self.index_interface.get(index)
                    if iface_index:
                        result.setdefault(iface_index, {})[metric_name] = int(value)

        if result:
            self.connection_value = True
            for iface, data in result.items():
                self.interfaces[iface].update(data)
        else:
            self.connection_value = False

    def get_all(self):
        return [{iface: self.interfaces[iface].get_params_all()} for iface in self.interfaces]

    def get_item_and_metric(self, item_id: str, metric_id: str):
        try:
            if item_id == str(self.connection_id) and metric_id == "connection":
                return self.connection_value
            iface = self.item_index.get(item_id)
            if iface:
                return self.interfaces[iface].get_metric(metric_id)
        except Exception as e:
            print(f"Ошибка получения {item_id}:{metric_id} - {e}")
        return None


class Interface(SubObject):
    def __init__(self):
        super().__init__()
        self.params = {
            "if.in.bytes": None,
            "if.in.packets": None,
            "if.out.errors": None,
            "if.out.bytes": None,
            "if.out.packets": None,
            "if.in.errors": None
        }

    def update(self, params_new: dict):
        self.params.update(params_new)

    def get_params_all(self):
        return self.params

    def get_metric(self, metric_id: str):
        try:
            result = self.params.get(metric_id)
            if result is not None:
                self.params[metric_id] = None
                return self.validate_integer(result)
        except Exception as e:
            print(f"Ошибка метрики {metric_id}: {e}")
        return None
