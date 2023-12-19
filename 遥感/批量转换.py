import os
from osgeo import gdal


def convert_to_tiff(input_folder_path, output_folder_path):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # 遍历文件夹内的所有文件
    for filename in os.listdir(input_folder_path):
        # 构建输入文件的完整路径
        input_file_path = os.path.join(input_folder_path, filename)
        # 构建输出文件的完整路径
        output_file_path = os.path.join(output_folder_path, os.path.splitext(filename)[0] + '.tiff')

        # 尝试打开文件
        dataset = gdal.Open(input_file_path)
        if dataset is not None:
            # 将文件转换为 TIFF
            gdal.Translate(output_file_path, dataset)
            print(f"转换文件：{input_file_path} 到 {output_file_path}")
        else:
            print(f"无法打开文件：{input_file_path}，或文件不是支持的格式")


# 使用示例
input_folder_path = 'D:\\yaoganguochengshuju\\EX5'  # 替换为你的输入文件夹路径
output_folder_path = 'D:\\yaoganguochengshuju\\EX5\\TIFF'  # 替换为你的输出文件夹路径
convert_to_tiff(input_folder_path, output_folder_path)
