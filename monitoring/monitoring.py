import platform 
import json

def main():
    if platform.system() == "Linux":
        from system.system_L import all_system
        from cpu.cpu_L import all_cpu
        from disk.disk_L import all_disk
        from ram.ram_L import all_ram
        data = {"monitoring": {}}
    elif platform.system() == "Windows":
        from system.system_W import all_system
        from ram.ram_W import all_ram
        from cpu.cpu_W import all_cpu
        from disk.disk_W import all_disk
        from gpu_nvidia.gpuNvidia_W import all_gpu
        data = {"monitoring": {"gpu": all_gpu()}}
    else:
        print("Операционная система не поддерживается программой")
        return -1

    data["monitoring"].update({
        "cpu": all_cpu(),
        "ram": all_ram(),
        "system": all_system(),
        "disks": all_disk()
    })
    return json.dumps(data, indent=4)

if __name__ == "__main__":
    print(main())