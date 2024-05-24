import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

# 设置matplotlib支持中文显示，并设置高分辨率输出
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.dpi'] = 1600


def load_data(folder_path):
    data = {'time': [], 'expedite': [], 'congested': [], 'blocked': [], 'unknown': []}
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
    return pd.DataFrame(data)


def categorize_time(hour):
    if 6 <= hour < 9:
        return '早高峰'
    elif 17 <= hour < 19:
        return '晚高峰'
    elif 9 <= hour < 12:
        return '上午非高峰'
    elif 12 <= hour < 17:
        return '下午非高峰'
    else:
        return '夜间非高峰'


def plot_advanced(data):
    data.set_index('time', inplace=True)

    # 时间序列分解
    result = seasonal_decompose(data['expedite'], model='additive', period=24)  # 假设每24小时为周期
    fig, axes = plt.subplots(4, 1, figsize=(10, 8))
    result.observed.plot(ax=axes[0], title='观测值')
    result.trend.plot(ax=axes[1], title='趋势')
    result.seasonal.plot(ax=axes[2], title='季节性')
    result.resid.plot(ax=axes[3], title='残差')
    fig.suptitle('时间序列分解')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # 线图
    plt.figure(figsize=(12, 8))
    plt.plot(data.index, data['expedite'], label='畅通')
    plt.plot(data.index, data['congested'], label='拥堵')
    plt.plot(data.index, data['blocked'], label='阻塞')
    plt.plot(data.index, data['unknown'], label='未知')
    plt.xlabel('时间')
    plt.ylabel('百分比 (%)')
    plt.title('24小时内交通状态变化')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 堆叠面积图
    colors = [(0.2, 0.4, 1, 0.6), (1, 0.9, 0.2, 0.6), (1, 0.2, 0.2, 0.6), (1, 1, 1, 0.6)]
    plt.figure(figsize=(12, 8))
    plt.stackplot(data.index, data['expedite'], data['congested'], data['blocked'], data['unknown'],
                  labels=['畅通', '拥堵', '阻塞', '未知'], colors=colors)
    plt.xlabel('时间')
    plt.ylabel('百分比 (%)')
    plt.title('24小时内交通状态变化（堆叠面积图）')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 箱形图
    data['hour'] = data.index.hour
    data['period'] = data['hour'].apply(categorize_time)
    melted_data = data.melt(id_vars=['period'], value_vars=['expedite', 'congested', 'blocked', 'unknown'],
                            var_name='Condition', value_name='Percentage')
    plt.figure(figsize=(12, 8))
    box_plot = sns.boxplot(x='period', y='Percentage', hue='Condition', data=melted_data)

    # 修改图例为中文
    handles, labels = box_plot.get_legend_handles_labels()
    new_labels = ['畅通', '拥堵', '阻塞', '未知']
    plt.legend(handles, new_labels, title='交通状况')

    plt.title('不同时间段的交通状态百分比分布')
    plt.xlabel('时间段')
    plt.ylabel('百分比 (%)')
    plt.show()

    # 滑动窗口平均图
    rolling_data = data['expedite'].rolling(window=24, center=True).mean()  # 24小时滑动平均
    plt.figure(figsize=(12, 6))
    plt.plot(data['expedite'], label='原始数据')
    plt.plot(rolling_data, label='滑动平均', color='red')
    plt.title('畅通百分比滑动平均')
    plt.xlabel('时间')
    plt.ylabel('畅通百分比 (%)')
    plt.legend()
    plt.show()


# 使用实际的文件夹路径
data = load_data(r"C:\Users\25830\Downloads\Compressed\lzw\results")
plot_advanced(data)
