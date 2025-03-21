import time

from freon_a import FreonA

time_1 = time.time()
obj_fa = FreonA()

print(obj_fa.get_item_all("192.168.85.137"))

obj_fa.update()

print(obj_fa.get_item_all("192.168.85.137"))

print(obj_fa.get_item("192.168.85.137","unit.U"))

print(obj_fa.get_item("192.168.85.137","unit.U"))

obj_fa.update()

print(obj_fa.get_item("192.168.85.137","unit.U"))

print(time.time()-time_1)

