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
plt.rcParams['savefig.dpi'] = 800


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

    # 组合热图
    data['hour'] = data.index.hour
    conditions = ['expedite', 'congested', 'blocked', 'unknown']

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    for ax, condition in zip(axes.flatten(), conditions):
        pivot_table = data.pivot_table(values=condition, index='hour', columns=pd.Grouper(freq='D'), aggfunc='mean')
        sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap='coolwarm', linewidths=.5, ax=ax,
                    cbar_kws={'label': '百分比 (%)'})
        ax.set_title(f'{condition}百分比热图')
        ax.set_xlabel('小时')
        ax.set_ylabel('日期')
    plt.tight_layout()
    plt.show()

    # 箱形图
    melted_data = data.melt(id_vars=['hour'], value_vars=conditions, var_name='Condition', value_name='Percentage')
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='hour', y='Percentage', hue='Condition', data=melted_data)
    plt.title('每小时不同条件的百分比分布')
    plt.xlabel('小时')
    plt.ylabel('百分比 (%)')
    plt.legend(title='交通状况')
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
