import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib

# 设置matplotlib以支持中文
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统使用SimHei
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# 替换为你的文件路径
file_path = r"D:\yaoganguochengshuju\EX5\analysis\HI-NDVI.txt"

# 读取数据，使用逗号加空格作为分隔符
data = pd.read_csv(file_path, sep=", ", header=None, names=["layer1", "layer2"], engine='python')

# 将数据转换为数值类型，非数值的行将被转换为NaN
data['layer1'] = pd.to_numeric(data['layer1'], errors='coerce')
data['layer2'] = pd.to_numeric(data['layer2'], errors='coerce')

# 删除任何含有NaN的行
data.dropna(inplace=True)

# 计算斯皮尔曼秩相关系数
spearman_corr, spearman_pvalue = stats.spearmanr(data['layer1'], data['layer2'])
print(f"Spearman Rank Correlation Coefficient: {spearman_corr}, P-value: {spearman_pvalue}")

# 选择多项式的次数
degree = 4

# 多项式回归
coefficients = np.polyfit(data['layer1'], data['layer2'], degree)
polynomial = np.poly1d(coefficients)


# 生成拟合的多项式方程字符串
equation = "y = " + " + ".join(
    [f"{coeff:.2e}x^{i}" if i > 1 else (f"{coeff:.2e}x" if i == 1 else f"{coeff:.2e}") for i, coeff in
     enumerate(coefficients[::-1])])

x = np.linspace(min(data['layer1']), max(data['layer1']), 100)
y_poly = polynomial(x)

# 创建一个高分辨率的图表
plt.figure(dpi=300)  # 设置DPI

# 绘制散点图和拟合曲线
plt.scatter(data['layer1'], data['layer2'], s=0.01)  # 点的大小
plt.plot(x, y_poly, 'r')
plt.xlabel('热岛强度')
plt.ylabel('NDVI')
plt.title('热岛强度与NDVI散点图与4次多项式拟合\n斯皮尔曼相关系数: {:.2f}'.format(spearman_corr))

# 显示方程
plt.text(min(data['layer1']), max(data['layer2']), equation, fontsize=9, color='red')

plt.show()

# 输出方程
print("Fitted Polynomial Equation:", equation)