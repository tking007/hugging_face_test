import pywifi
from pywifi import const

# 创建一个无线对象
wifi = pywifi.PyWiFi()

# 获取第一个无线网卡
iface = wifi.interfaces()[0]

# 打印网卡的名称，确认我们获取的是正确的网卡
print(iface.name())

# 尝试将网卡设置为监听模式
iface.disconnect()  # 如果有连接，先断开
mode = iface.mode()  # 获取当前模式
try:
    iface.mode(const.IFACE_MONITOR)  # 尝试设置为监听模式
    print("无线网卡支持监听模式")
except Exception as e:
    print("无线网卡不支持监听模式")
finally:
    iface.mode(mode)  # 恢复原来的模式