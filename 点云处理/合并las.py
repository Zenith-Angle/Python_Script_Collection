import os
import glob
import laspy
import numpy as np


def merge_las_files(input_folder, output_file):
    # 获取指定文件夹中的所有 LAS 文件
    las_files = glob.glob(os.path.join(input_folder, "*.las"))

    if not las_files:
        print("指定文件夹中没有找到 LAS 文件")
        return

    # 读取第一个 LAS 文件
    merged_las = laspy.read(las_files[0])

    # 创建一个用于存储合并后的点云数据的列表
    points = [merged_las.points]

    # 逐个读取并合并其余的 LAS 文件
    for las_file in las_files[1:]:
        las = laspy.read(las_file)
        points.append(las.points)

    # 使用 numpy.vstack 合并所有点云数据
    merged_points = np.vstack(points)

    # 更新 merged_las 的点云数据
    merged_las.points = merged_points

    # 将合并后的数据写入输出文件
    merged_las.write(output_file)
    print(f"合并后的 LAS 文件已保存为 {output_file}")


# 指定输入文件夹和输出文件名
input_folder = r"E:\juan_wan\jw激光雷达"  # 请替换为你的LAS文件所在的文件夹路径
output_file = "23JuanWan_LAS.las"

# 合并 LAS 文件
merge_las_files(input_folder, output_file)
