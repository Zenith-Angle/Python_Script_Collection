import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 替换为你的文件路径
file_path = r"D:\yaoganguochengshuju\EX5\analysis\HI-MNDWI.txt"

# 读取数据，使用逗号加空格作为分隔符
data = pd.read_csv(file_path, sep=", ", header=None, names=["layer1", "layer2"], engine='python')

# 将数据转换为数值类型，非数值的行将被转换为NaN
data['layer1'] = pd.to_numeric(data['layer1'], errors='coerce')
data['layer2'] = pd.to_numeric(data['layer2'], errors='coerce')

# 删除任何含有NaN的行
data.dropna(inplace=True)

# 计算皮尔逊相关系数
pearson_corr, pearson_pvalue = stats.pearsonr(data['layer1'], data['layer2'])
print(f"Pearson Correlation Coefficient: {pearson_corr}, P-value: {pearson_pvalue}")

# 计算斯皮尔曼秩相关系数
spearman_corr, spearman_pvalue = stats.spearmanr(data['layer1'], data['layer2'])
print(f"Spearman Rank Correlation Coefficient: {spearman_corr}, P-value: {spearman_pvalue}")

# 四次多项式回归
coefficients = np.polyfit(data['layer1'], data['layer2'], 4)
polynomial = np.poly1d(coefficients)
x = np.linspace(min(data['layer1']), max(data['layer1']), 100)
y_poly = polynomial(x)

# 绘制散点图和拟合曲线
plt.scatter(data['layer1'], data['layer2'], s=10)  # 点的大小
plt.plot(x, y_poly, 'r')
plt.xlabel('Layer 1')
plt.ylabel('Layer 2')
plt.title('Scatter Plot of Two Layers with 4th Degree Polynomial Regression')
plt.show()