import subprocess
import re


def get_network_stats():
    cmd = "wmic path Win32_PerfRawData_Tcpip_NetworkInterface get Name, BytesReceivedPersec, BytesSentPersec,PacketsReceivedErrors,PacketsOutboundErrors, CurrentBandwidth /format:table"
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8",
                            errors="ignore")  # Фикс кодировки

    lines = result.stdout.strip().split("\n")
    if not lines or len(lines) < 2:
        print("Ошибка: WMIC не вернул данные.")
        return []

    headers = re.split(r'\s{2,}', lines[0].strip())  # Заголовки столбцов
    stats = []
    print(lines[0])
    for line in lines[2:]:
        print(line)
        values = re.split(r'\s{2,}', line.strip())
        if len(values) == len(headers):
            stats.append(dict(zip(headers, values)))

    return stats


def print_stats(stats):
    if not stats:
        print("Нет доступных сетевых интерфейсов.")
        return

    for stat in stats:
        ReceivLoad = -1
        SendLoad = -1
        if float(stat.get('CurrentBandwidth', 0)) != 0:
            if stat.get('BytesReceivedPersec', -1) != -1:
                ReceivLoad = 100.0 * float(stat.get('BytesReceivedPersec', -1)) / float(stat.get('CurrentBandwidth', 0))
            if stat.get('BytesSentPersec', -1) != -1:
                SendLoad = 100.0 * float(stat.get('BytesSentPersec', -1)) / float(stat.get('CurrentBandwidth', 0))


        print(f"Интерфейс: {stat['Name']}")
        print(f"  Получено пакетов: пока не собрано")
        print(f"  Отправлено пакетов: пока не собрано")
        print(f"  Получено байт: пока не собрано")
        print(f"  Отправлено байт: пока не собрано")
        print(f"  Входящая скорость: {float(stat.get('BytesReceivedPersec', -1))} байт/сек")
        print(f"  Исходящая скорость: {float(stat.get('BytesSentPersec', -1))} байт/сек")
        print(f"  Загрузка исходящим трафиком: {SendLoad} %")
        print(f"  Загрузка входящим трафиком: {ReceivLoad} %")
        print(f"  Ошибки при приеме: {float(stat.get('PacketsReceivedErrors', -1))}")
        print(f"  Ошибки при отправке: {float(stat.get('PacketsOutboundErrors', -1))}")
        print("-" * 40)


if __name__ == "__main__":
    stats = get_network_stats()
    print_stats(stats)
