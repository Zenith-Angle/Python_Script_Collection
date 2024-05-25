import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
import matplotlib

# 设置matplotlib支持中文显示
matplotlib.rcParams['font.family'] = 'SimHei'  # 设置字体为黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 读取Excel文件
file_path = r"D:\开发竞赛\数据\路线数据\模型建立\西宁_长度计量容纳力.xlsx"
data = pd.read_excel(file_path)

# 处理数据，去除'exped_c'中的缺失值
data = data.dropna(subset=['exped_c'])

# 定义特征和目标变量
X = data[['trfc_cap', 'pts_num']]
y = data['exped_c']

# 切分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建并训练SVR模型
svr_model = SVR(kernel='rbf', C=1.0, epsilon=0.1)
svr_model.fit(X_train, y_train)

# 进行预测
y_train_pred = svr_model.predict(X_train)
y_test_pred = svr_model.predict(X_test)

# 计算性能指标
r2_train = r2_score(y_train, y_train_pred)
r2_test = r2_score(y_test, y_test_pred)
mse_train = mean_squared_error(y_train, y_train_pred)
mse_test = mean_squared_error(y_test, y_test_pred)

# 输出结果
print(f"Train R^2: {r2_train:.4f}")
print(f"Test R^2: {r2_test:.4f}")
print(f"Train MSE: {mse_train:.4f}")
print(f"Test MSE: {mse_test:.4f}")

# 绘制真实值与预测值的对比图，并保存为文件

# 训练集的对比图
plt.figure(figsize=(12, 6), dpi=1600)
plt.scatter(y_train, y_train_pred, alpha=0.3)
plt.plot([min(y_train), max(y_train)], [min(y_train), max(y_train)], 'r--')
plt.xlabel("真实值")
plt.ylabel("预测值")
plt.title("训练集: 真实值 vs 预测值")
plt.legend(['预测值'], loc='upper left')
plt.savefig('train_comparison.png', bbox_inches='tight')
plt.show()

# 测试集的对比图
plt.figure(figsize=(12, 6), dpi=1600)
plt.scatter(y_test, y_test_pred, alpha=0.3)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')
plt.xlabel("真实值")
plt.ylabel("预测值")
plt.title("测试集: 真实值 vs 预测值")
plt.legend(['预测值'], loc='upper left')
plt.savefig('test_comparison.png', bbox_inches='tight')
plt.show()
