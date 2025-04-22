import subprocess
import re
import shutil

def find_field(fields, output):
    """
    Ищет первое совпадение одного из заданных полей в выводе команды.
    """
    for field in fields:
        match = re.search(rf"{field}:\s+(.*)", output)
        if match:
            return match.group(1).strip()
    return "Unknown"

# -------------------------------------------------------------------------------------------------------------


def _find(field_names: list[str], text: str):
    """
    Возвращает первое найденное значение строки
    «<Field name> : <value>» или None.
    """
    for name in field_names:
        m = re.search(rf"{name}\s*:\s*(.+)", text, re.I)
        if m:
            return m.group(1).strip()
    return None


def _smart_devices() -> list[dict]:
    """
    Собирает информацию о дисках при помощи smartctl.
    """
    if shutil.which("smartctl") is None:
        raise RuntimeError("smartctl не найден в PATH")

    result = subprocess.run(
        ["smartctl", "--scan"],
        capture_output=True,
        text=True,
        check=True,
    )

    devices: list[dict] = []
    for line in result.stdout.strip().splitlines():
        m = re.search(r"(/dev/\S+|\S+):?", line)
        if not m:
            continue

        dev = m.group(1)
        info = subprocess.run(
            ["smartctl", "-i", dev],
            capture_output=True,
            text=True,
            check=False,
        ).stdout

        devices.append(
            {
                "device": dev,
                "model": _find(
                    ["Model Number", "Device Model", "Product"], info
                )
                or "Unknown model",
                "serial": _find(["Serial Number"], info) or "Unknown SN",
                "smart": subprocess.run(
                    ["smartctl", "-A", dev],
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.strip(),
            }
        )
    return devices


def _wmic_disk_rates():
    if shutil.which("wmic") is None:
        return {}

    cmd = [
        "wmic",
        "path",
        "Win32_PerfFormattedData_PerfDisk_PhysicalDisk",
        "get",
        "Name,DiskReadBytesPersec,DiskWriteBytesPersec",
        "/format:csv",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    rates = {}

    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4 or parts[3].lower() == "name":
            continue  # пропускаем заголовок
        _, read_bps, write_bps, name = parts[:4]
        try:
            rates[name] = (int(read_bps), int(write_bps))
        except ValueError:
            rates[name] = (0, 0)
    return rates


def get_disks_report() -> str:
    disks = _smart_devices()
    rates = _wmic_disk_rates()

    lines: list[str] = ["smartctl"]
    for d in disks:
        lines.append(f"{d['device']} == {d['model']}, {d['serial']}")
        lines.append(d["smart"])
        lines.append("")

    if rates:
        lines.append(
            'wmic'
        )
        for name, (r, w) in rates.items():
            lines.append(f"{name} == {r} B/s read, {w} B/s write")
    else:
        lines.append("wmic: утилита недоступна или выполнена не в Windows")
    return "\n".join(lines).strip()


# -------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    with open("_disks.txt", "w", encoding="utf-8") as f:
        f.write(get_disks_report())
    print("Информация успешно сохранена в файл")