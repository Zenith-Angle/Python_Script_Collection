import os
from osgeo import gdal, ogr


def extract_by_mask(folder_path, shp_file_path):
    # 加载 Shapefile
    shp = ogr.Open(shp_file_path)
    if shp is None:
        print(f"无法打开 Shapefile: {shp_file_path}")
        return

    # 获取 Shapefile 的图层
    layer = shp.GetLayer()

    # 遍历文件夹内的所有 TIFF 文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.tiff') or filename.endswith('.tif'):
            # 构建输入文件的完整路径
            input_file_path = os.path.join(folder_path, filename)
            # 构建输出文件的完整路径（添加 'extracted' 后缀）
            base_name, ext = os.path.splitext(filename)
            output_file_path = os.path.join(folder_path, base_name + '_extracted' + ext)

            # 使用 Shapefile 作为掩膜提取 TIFF 文件
            ds = gdal.Warp(output_file_path, input_file_path, format='GTiff', cutlineDSName=shp_file_path,
                           cutlineLayer=layer.GetName(), cropToCutline=True, dstNodata=0)
            if ds is not None:
                ds = None  # 关闭数据集
                print(f"按掩膜提取完成：{output_file_path}")
            else:
                print(f"无法按掩膜提取文件：{input_file_path}")


# 使用示例
folder_path = r"D:\yaoganguochengshuju\EX5\2000Index"  # 替换为你的文件夹路径
shp_file_path = r"D:\yaoganguochengshuju\EX5\2000Index\2000.shp"  # 替换为你的 Shapefile 路径
extract_by_mask(folder_path, shp_file_path)
