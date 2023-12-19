import rasterio
import numpy as np
from tqdm import tqdm

# 打开两个遥感影像文件
with rasterio.open(r"D:\yaoganguochengshuju\EX4\fc.tif") as src1, \
        rasterio.open(r"D:\yaoganguochengshuju\EX4\TS.tif") as src2:
    # 确保两个影像的尺寸相同
    assert src1.shape == src2.shape

    # 一次性读取整个图层
    data1 = src1.read(1)
    data2 = src2.read(1)

    # 创建一个用于存储结果的列表
    results = []

    # 使用tqdm创建进度条
    with tqdm(total=src1.width * src1.height, desc="Processing", unit="pixel") as pbar:
        # 使用Numpy数组操作来处理像素值
        for row in range(src1.height):
            for col in range(src1.width):
                results.append(f'{data1[row, col]}, {data2[row, col]}\n')
                pbar.update(1)

# 将结果一次性写入文件
with open(r"D:\yaoganguochengshuju\EX4\fc-TS.txt", 'w') as outfile:
    outfile.writelines(results)

# 处理完成后打印提示
print("处理完成，结果已保存至fc-TS.txt")
