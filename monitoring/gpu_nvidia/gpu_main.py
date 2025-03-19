import time
from gpu_nvidia import GPUsMonitor

def measure_time(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

gpus, time_init = measure_time(GPUsMonitor)

get1, time_get1 = measure_time(gpus.get_gpus_all,"GPU-00a97fdd-bdb8-ae1d-07c2-86dacb0e1b54")
print(get1)

_, time_update = measure_time(gpus.update)

get2, time_get2 = measure_time(gpus.get_gpus_all,"GPU-00a97fdd-bdb8-ae1d-07c2-86dacb0e1b54")
print(get2)

get_item, time_item = measure_time(gpus.get_gpu,"GPU-00a97fdd-bdb8-ae1d-07c2-86dacb0e1b54", "gpu.index")
print(get_item)
get3, time_get3 = measure_time(gpus.get_gpus_all,"GPU-00a97fdd-bdb8-ae1d-07c2-86dacb0e1b54")
print(get3)

print("-"*25)
print(time_init)
print(time_get1)
print(time_update)
print(time_get2)
print(time_item)
print(time_get3)