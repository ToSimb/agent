import ctypes
import ctypes.wintypes as wintypes
import json

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3

IOCTL_SCSI_MINIPORT = 0x0004D008
IOCTL_SCSI_MINIPORT_SMART = 0x0004D028
SMART_GET_VERSION = 0x00074080
SMART_RCV_DRIVE_DATA = 0x0007c088

class GETVERSIONINPARAMS(ctypes.Structure):
    _fields_ = [
        ("bVersion", wintypes.BYTE),
        ("bRevision", wintypes.BYTE),
        ("bReserved", wintypes.BYTE),
        ("bIDEDeviceMap", wintypes.BYTE),
        ("fCapabilities", wintypes.DWORD),
        ("dwReserved", wintypes.DWORD * 4)
    ]

def get_smart_data_windows(physical_drive_index):
    device_path = f"\\\\.\\PhysicalDrive{physical_drive_index}"
    handle = ctypes.windll.kernel32.CreateFileW(
        device_path,
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None
    )

    if handle == -1 or handle == 0:
        return {"device": device_path, "error": "Cannot open device (no permission or does not exist)"}

    try:
        # Получаем SMART версию
        version_params = GETVERSIONINPARAMS()
        bytes_returned = wintypes.DWORD()

        res = ctypes.windll.kernel32.DeviceIoControl(
            handle,
            SMART_GET_VERSION,
            None,
            0,
            ctypes.byref(version_params),
            ctypes.sizeof(version_params),
            ctypes.byref(bytes_returned),
            None
        )

        if not res:
            return {"device": device_path, "error": "SMART not supported"}

        return {
            "device": device_path,
            "smart_available": True,
            "version": version_params.bVersion,
            "revision": version_params.bRevision,
            "device_map": version_params.bIDEDeviceMap,
            "capabilities": version_params.fCapabilities
        }

    finally:
        ctypes.windll.kernel32.CloseHandle(handle)

# Пример: Получить данные с первых 4 дисков
data = [get_smart_data_windows(i) for i in range(4)]
print(json.dumps(data, indent=2))
