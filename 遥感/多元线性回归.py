import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# 加载数据
data = pd.read_excel(r"D:\yaoganguochengshuju\EX5\analysis\HI-I.xlsx")

# 选择自变量和因变量
X = data.iloc[:, 1:]  # 自变量 (第2, 3, 4, 5列)
y = data.iloc[:, 0]  # 因变量 (第1列)

# 将数据分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# 创建并训练线性回归模型
model = LinearRegression()
model.fit(X_train, y_train)

# 预测和评估模型
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# 获取系数和截距
coefficients = model.coef_
intercept = model.intercept_

# 输出系数和截距
print("系数:", coefficients)
print("截距:", intercept)
print("均方误差:", mse)
print("R^2 分数:", r2)

# 构造拟合方程
equation = "y = "
for i, coef in enumerate(coefficients):
    equation += f"{coef:.2f} * x{i + 1} "
    if i < len(coefficients) - 1:
        equation += "+ "
equation += f"+ {intercept:.2f}"

# 输出拟合方程
print("拟合方程:", equation)

plt.figure(dpi=300)  # 设置DPI
# 绘制残差图
plt.scatter(y_test, y_test - y_pred, color='blue', s=0.01)  # 将点的大小设置为0.01
plt.title('残差图')
plt.xlabel('实际值')
plt.ylabel('残差')
plt.axhline(y=0, color='r', linestyle='--')
plt.show()
