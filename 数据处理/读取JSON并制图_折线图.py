import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib

# 设置matplotlib支持中文显示
matplotlib.rcParams['font.family'] = 'SimHei'  # 设置字体为黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def read_and_plot_data(folder_path):
    data = {'time': [], 'expedite': [], 'congested': [], 'blocked': [], 'unknown': [], 'status': []}

    for filename in sorted(os.listdir(folder_path)):
        if filename.startswith('traffic_data') and filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                content = json.load(file)
                evaluation = content['trafficinfo']['evaluation']
                timestamp = filename[len('traffic_data_'):-5]
                time_format = '%Y-%m-%d_%H-%M-%S'
                date_time = datetime.strptime(timestamp, time_format)

                data['time'].append(date_time)
                data['expedite'].append(float(evaluation['expedite'].replace('%', '')))
                data['congested'].append(float(evaluation['congested'].replace('%', '')))
                data['blocked'].append(float(evaluation['blocked'].replace('%', '')))
                data['unknown'].append(float(evaluation['unknown'].replace('%', '')))
                data['status'].append(int(evaluation['status']))

    # 分别绘制图表
    plt.figure(figsize=(12, 6))
    plt.plot(data['time'], data['expedite'], label='畅通', marker='o')
    plt.xlabel('时间')
    plt.ylabel('百分比 (%)')
    plt.title('畅通情况随时间的变化')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(data['time'], data['congested'], label='拥堵', marker='o')
    plt.xlabel('时间')
    plt.ylabel('百分比 (%)')
    plt.title('拥堵情况随时间的变化')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(data['time'], data['blocked'], label='阻塞', marker='o')
    plt.xlabel('时间')
    plt.ylabel('百分比 (%)')
    plt.title('阻塞情况随时间的变化')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(data['time'], data['unknown'], label='未知', marker='o')
    plt.xlabel('时间')
    plt.ylabel('百分比 (%)')
    plt.title('未知情况随时间的变化')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(data['time'], data['status'], label='状态', marker='o')
    plt.xlabel('时间')
    plt.ylabel('状态值')
    plt.title('状态随时间的变化')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 使用实际的文件夹路径替换此处的'your_folder_path'
read_and_plot_data(r"C:\Users\25830\Downloads\lzw\results")
