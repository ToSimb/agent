import time

from system import SystemMonitor

a = SystemMonitor()
a.update()
dd = a.get_all()
print(a.get_metrics("111"))