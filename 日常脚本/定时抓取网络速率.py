import psutil
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

# 初始化数据存储列表和上一次的数据
timestamps, sent_data, received_data = [], [], []
last_sent, last_received = 0, 0


def get_bandwidth(interface='以太网'):
    global last_sent, last_received
    net_io = psutil.net_io_counters(pernic=True)
    if interface in net_io:
        sent = net_io[interface].bytes_sent
        received = net_io[interface].bytes_recv
        sent_diff = sent - last_sent
        received_diff = received - last_received
        last_sent, last_received = sent, received
        return sent_diff, received_diff
    else:
        print(f'Interface {interface} not found')
        return None, None


# 设置图像保存的时间间隔（单位：分钟）
save_interval = 5

# 记录下一次保存图像的时间
next_save_time = datetime.now() + timedelta(minutes=save_interval)

while True:
    # 获取当前时间和带宽数据
    timestamp = datetime.now()
    sent_diff, received_diff = get_bandwidth()

    if sent_diff is not None:
        timestamps.append(timestamp)
        sent_data.append(sent_diff)
        received_data.append(received_diff)

    # 检查是否到了保存图像的时间
    if datetime.now() >= next_save_time:
        # 创建并保存图像
        fig, ax = plt.subplots(2, 1, figsize=(10, 5))
        ax[0].plot(timestamps, sent_data, label='Bytes Sent')
        ax[1].plot(timestamps, received_data, label='Bytes Received', color='red')

        ax[0].legend()
        ax[1].legend()
        ax[0].set_ylabel('Bytes')
        ax[1].set_xlabel('Time')
        ax[1].set_ylabel('Bytes')

        plt.tight_layout()

        # 保存图像
        filename = f"bandwidth_{next_save_time.strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        print(f"Saved plot as {filename}")

        # 更新下一次保存图像的时间
        next_save_time += timedelta(minutes=save_interval)

        # 清空数据（可选）
        timestamps.clear()
        sent_data.clear()
        received_data.clear()

        plt.close(fig)

    # 休眠1秒
    time.sleep(1)
