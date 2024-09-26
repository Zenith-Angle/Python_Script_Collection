import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score
import rasterio
from rasterio.plot import reshape_as_image
from skimage.transform import resize

# 设置matplotlib支持中文显示
plt.rcParams['font.family'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 读取影像数据并重采样为相同形状
def read_tiff(file_path):
    with rasterio.open(file_path) as src:
        array = src.read(1)  # 读取第一个波段的数据
        return array


# 重采样函数，将数组重采样为指定形状
def resample_array(array, new_shape):
    resized_array = resize(array, new_shape, mode='constant')
    return resized_array


# 定义影像文件路径
vari_path = r'E:\juan_wan\处理\dsm\VARI.tif'
slope_path = r'E:\juan_wan\处理\dsm\坡度.tif'
erosion_path = r'E:\juan_wan\处理\dsm\erosion.tif'

# 读取影像数据并重采样为相同形状
vari_data = read_tiff(vari_path)
slope_data = read_tiff(slope_path)
erosion_data = read_tiff(erosion_path)

# 确保数据形状一致
min_shape = (min(vari_data.shape[0], slope_data.shape[0], erosion_data.shape[0]),
             min(vari_data.shape[1], slope_data.shape[1], erosion_data.shape[1]))

vari_data = resample_array(vari_data, min_shape)
slope_data = resample_array(slope_data, min_shape)
erosion_data = resample_array(erosion_data, min_shape)

# 将影像数据转换为DataFrame
df = pd.DataFrame({
    'VARI': vari_data.flatten(),
    'Slope': slope_data.flatten(),
    'Erosion': erosion_data.flatten()
})

# 移除包含NaN值的行
df = df.dropna()

# 构建自变量和因变量
X = df[['VARI', 'Slope']]
y = df['Erosion']

# 使用多项式回归拟合
degree = 2  # 多项式的次数，可以根据实际情况调整
model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
model.fit(X, y)

# 预测
y_pred = model.predict(X)

# 计算R平方
r2 = r2_score(y, y_pred)
print(f"R-squared: {r2}")

# 绘制散点图和回归线
plt.figure(figsize=(10, 6))
plt.scatter(y, y_pred, color='blue', alpha=0.6)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
plt.title('多元回归预测结果', fontsize=16)
plt.xlabel('实际值', fontsize=14)
plt.ylabel('预测值', fontsize=14)
plt.text(y.min() + (y.max() - y.min()) * 0.1, y.max() - (y.max() - y.min()) * 0.1,
         f'R^2 = {r2:.2f}', fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.show()
