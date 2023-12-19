import os
from osgeo import gdal


def convert_tiff_to_envi(folder_path):
    # 遍历文件夹内的所有 TIFF 文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".tiff") or filename.endswith(".tif"):
            # 构建输入文件的完整路径
            input_file_path = os.path.join(folder_path, filename)
            # 构建输出文件的完整路径（这里我添加了 '_envi' 后缀来区分文件）
            output_file_path = os.path.join(folder_path, os.path.splitext(filename)[0] + '_envi')

            # 打开 TIFF 文件
            dataset = gdal.Open(input_file_path)
            if dataset is not None:
                # 设置输出格式为 ENVI
                driver = gdal.GetDriverByName('ENVI')
                # 将 TIFF 文件转换为 ENVI
                driver.CreateCopy(output_file_path, dataset)
                print(f"转换文件：{input_file_path} 到 {output_file_path}")
            else:
                print(f"无法打开文件：{input_file_path}")


# 使用示例
folder_path =r"D:\yaoganguochengshuju\EX5\2010Index" # 替换为你的文件夹路径
convert_tiff_to_envi(folder_path)
