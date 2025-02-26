import json
from  pysnmp.hlapi import *


def snmp_get_bulk(oid, target, community='public', port=161):
    """Запрашивает SNMP-данные по OID для всех интерфейсов."""
    iterator = nextCmd(
        snmpSnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((target, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False  # Останавливаем на другом OID
    )

    results = {}
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(f"SNMP error: {errorIndication}")
            break
        elif errorStatus:
            print(f"SNMP error: {errorStatus.prettyPrint()}")
            break
        else:
            for varBind in varBinds:
                index = str(varBind[0]).split('.')[-1]  # Последняя цифра в OID — номер интерфейса
                results[index] = int(varBind[1]) if varBind[1].isNumeric() else None
    return results

# Функция сбора данных с устройства
def collect_snmp_data(target, community):
    """Собирает SNMP-метрики по всем интерфейсам устройства."""
    oids = {
        "out_traffic": "1.3.6.1.2.1.2.2.1.16",  # ifOutOctets
        "max_speed": "1.3.6.1.2.1.2.2.1.5",    # ifSpeed
        "in_errors": "1.3.6.1.2.1.2.2.1.14",   # ifInErrors
        "out_errors": "1.3.6.1.2.1.2.2.1.20"   # ifOutErrors
    }

    device_data = {}

    for key, oid in oids.items():
        device_data[key] = snmp_get_bulk(oid, target, community)

    return device_data

# Читаем конфигурацию из файла
def load_config(config_file="config.json"):
    """Загружает список устройств и SNMP-параметры из JSON-файла."""
    with open(config_file, "r") as file:
        return json.load(file)

# Основная функция
def main():
    config = load_config()
    all_data = {}

    for device in config["devices"]:
        ip = device["ip"]
        community = device["community"]
        print(f"Сбор данных с {ip}...")
        all_data[ip] = collect_snmp_data(ip, community)

    print(json.dumps(all_data, indent=4))

# Запуск
if __name__ == "__main__":
    main()
