import time

from freon_b import FreonB
time_1 = time.time()

a1 = FreonB()
a1.update()
time_2 = time.time()
a1.get_all()
print("_____________")
print(a1.get_item_all("192.168.0.60"))
print(a1.get_item("192.168.0.60", "state"))
print(a1.get_item2("192.168.0.60", 0,"unit.P"))

print(time_2 - time_1)
print(time.time() - time_2)