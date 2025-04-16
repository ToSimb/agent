from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd,
    nextCmd
)


def get_iface_descr(ip, community="public", snmp_port=161):
    oid_if_descr = ObjectIdentity('1.3.6.1.2.1.2.2.1.2')
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, snmp_port), timeout=1, retries=2),
        ContextData(),
        ObjectType(oid_if_descr),
        lexicographicMode=False
    ):
        if errorIndication:
            print(f"SNMP ошибка на {ip} при получении описаний интерфейсов: {errorIndication}")
            break
        elif errorStatus:
            print(f"SNMP ошибка на {ip} при получении описаний интерфейсов: {errorStatus.prettyPrint()}")
            break
        else:
            for varBind in varBinds:
                oid, value = varBind
                if_oid_index = str(oid).split('.')[-1]
                print(f"{if_oid_index}: {value.prettyPrint()}")

get_iface_descr('10.70.0.250')