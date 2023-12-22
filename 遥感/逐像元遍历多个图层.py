import rasterio
import numpy as np
from tqdm import tqdm


# 定义读取和处理tif文件的函数
def read_and_process_tif(file_path, min_threshold=-999, max_threshold=999):
    with rasterio.open(file_path) as src:
        data = src.read(1)
        # 使用numpy的掩码数组来快速剔除极值
        masked_data = np.ma.masked_outside(data, min_threshold, max_threshold)
        return masked_data.filled(np.nan)  # 将掩码部分替换为nan


# 要处理的文件列表
file_paths = [
    r"D:\yaoganguochengshuju\EX5\analysis\2000HI.tif",
    r"D:\yaoganguochengshuju\EX5\Index\Extract_2000NDVI.tif",
    r"D:\yaoganguochengshuju\EX5\Index\Extract_2000NDBI.tif",
    r"D:\yaoganguochengshuju\EX5\Index\Extract_2000NDISI.tif",
    r"D:\yaoganguochengshuju\EX5\Index\Extract_2000MNDWI.tif",
    # 添加其它四个文件的路径
    # ...
]

# 读取并处理每个文件
data_arrays = [read_and_process_tif(path) for path in file_paths]

# 检查数组尺寸是否一致
assert all(data.shape == data_arrays[0].shape for data in data_arrays)

# 创建一个用于存储结果的列表
results = []

# 使用tqdm创建进度条
with tqdm(total=data_arrays[0].size, desc="Processing", unit="pixel") as pbar:
    for row in range(data_arrays[0].shape[0]):
        for col in range(data_arrays[0].shape[1]):
            # 提取每个文件在相同位置的值
            values = [data[row, col] for data in data_arrays]
            # 检查是否所有值都不是nan
            if all(np.isfinite(v) for v in values):
                results.append(', '.join(map(str, values)) + '\n')
            pbar.update(1)

# 指定输出文件名
output_filename = r"D:\yaoganguochengshuju\EX5\analysis\Hi-I.txt"

# 将结果一次性写入文件
with open(output_filename, 'w') as outfile:
    outfile.writelines(results)

# 处理完成后打印提示
print(f"处理完成，结果已保存至{output_filename}")
