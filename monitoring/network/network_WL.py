import json
import ipaddress
from pysnmp.hlapi import (SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd)


def snmp_get(ip, community, oid):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), 1, 2),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"Ошибка SNMP на {ip}: {errorIndication}")
            return None
        elif errorStatus:
            print(f"Ошибка SNMP на {ip}: {errorStatus.prettyPrint()}")
            return None
        else:
            for varBind in varBinds:
                return str(varBind[1])
    except Exception as e:
        print(f"Исключение при SNMP-запросе {ip}: {e}")
        return None


def discover_switches(network, community):
    found_switches = []
    print(f"Сканирование сети {network}...")
    for ip in ipaddress.IPv4Network(network, strict=False):
        sys_desc = snmp_get(str(ip), community, "1.3.6.1.2.1.1.1.0")
        if sys_desc:
            print(f"Обнаружен коммутатор: {ip}")
            found_switches.append(str(ip))
    return found_switches


def collect_data(ip, community):
    oids = {
        "received_bytes": "1.3.6.1.2.1.2.2.1.10",
        "received_packets": "1.3.6.1.2.1.2.2.1.11",
        "incoming_speed": "1.3.6.1.2.1.31.1.1.1.6",
        "incoming_load": "1.3.6.1.2.1.31.1.1.1.7",
        "sent_bytes": "1.3.6.1.2.1.2.2.1.16",
        "sent_packets": "1.3.6.1.2.1.2.2.1.17",
        "outgoing_speed": "1.3.6.1.2.1.31.1.1.1.10",
        "outgoing_load": "1.3.6.1.2.1.31.1.1.1.11",
        "receive_errors": "1.3.6.1.2.1.2.2.1.14",
        "send_errors": "1.3.6.1.2.1.2.2.1.20"
    }

    data = {}
    print(f"Сбор данных с {ip}...")
    for key, oid in oids.items():
        value = snmp_get(ip, community, oid)
        data[key] = value if value is not None else "N/A"

    return data


if __name__ == "__main__":
    network = "192.168.12.0/24"  # Укажите вашу подсеть
    community = "public"  # SNMP community

    switches = discover_switches(network, community)
    all_data = {}

    if not switches:
        print("Не найдено ни одного коммутатора! Проверьте SNMP-доступ.")
    else:
        for switch_ip in switches:
            all_data[switch_ip] = collect_data(switch_ip, community)

        with open("switch_data.json", "w") as f:
            json.dump(all_data, f, indent=4)

        print("Данные сохранены в switch_data.json")
