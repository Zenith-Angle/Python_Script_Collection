import psutil

available_interfaces = psutil.net_io_counters(pernic=True).keys()
print("可用的网络接口：")
for interface in available_interfaces:
    print(interface)
