import time
from eth_port import EthPortMonitor

eth_ports = EthPortMonitor()
print(eth_ports.get_eth_ports_of_update())
eth_ports.update_eth_ports_of_update(["lo", 'enp2s0'])
print(eth_ports.get_eth_ports_of_update())
time_1 = time.time()
eth_ports.update()
print(time.time() - time_1)
print("----------------")

eth_ports.get_all()

print("------"*4)

print(eth_ports.get_item("lo", "port.in.bytes"))