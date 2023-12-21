import rasterio
import numpy as np
from tqdm import tqdm

# 打开两个遥感影像文件
with rasterio.open(r"D:\yaoganguochengshuju\EX5\analysis\2000HI.tif") as src1, \
        rasterio.open(r"D:\yaoganguochengshuju\EX5\Index\Extract_2000NDVI.tif") as src2:

    # 确保两个影像的尺寸相同
    assert src1.shape == src2.shape

    # 一次性读取整个图层
    data1 = src1.read(1)
    data2 = src2.read(1)

    # 定义极值阈值
    min_threshold, max_threshold = -999, 999

    # 创建一个用于存储结果的列表
    results = []

    # 使用tqdm创建进度条
    with tqdm(total=src1.width * src1.height, desc="Processing", unit="pixel") as pbar:
        # 使用Numpy数组操作来处理像素值
        for row in range(src1.height):
            for col in range(src1.width):
                # 剔除极大值和极小值
                if min_threshold < data1[row, col] < max_threshold and \
                        min_threshold < data2[row, col] < max_threshold:
                    results.append(f'{data1[row, col]}, {data2[row, col]}\n')
                pbar.update(1)

# 指定输出文件名
output_filename = r"D:\yaoganguochengshuju\EX5\analysis\HI-NDVI.txt"

# 将结果一次性写入文件
with open(output_filename, 'w') as outfile:
    outfile.writelines(results)

# 处理完成后打印提示
print(f"处理完成，结果已保存至{output_filename}")
