# 将一个shp文件里面的所有的要素都合并为一个要素
# import os
# import geopandas as gpd
# import pandas as pd
# from shapely.ops import unary_union
#
# # 定义输入文件夹路径和输出文件路径
# input_folder = r"D:\开发竞赛\数据\高程数据\DEM\Contours"
# output_file = r'D:\开发竞赛\数据\高程数据\DEM\Contours\merged_contourLine.shp'
#
# # 初始化一个空的列表，用于存储所有shp文件的GeoDataFrame
# gdf_list = []
#
# # 遍历输入文件夹中的所有shp文件
# for file in os.listdir(input_folder):
#     if file.endswith('.shp'):
#         file_path = os.path.join(input_folder, file)
#         gdf = gpd.read_file(file_path)
#
#         # 检查shp文件是否包含数据
#         if gdf.empty:
#             print(f"{file} 为空，跳过")
#             continue
#
#         # 如果没有CRS，设置默认的CRS
#         if gdf.crs is None:
#             gdf.set_crs(epsg=4326, inplace=True)
#
#         # 获取当前shp文件的ELEV字段值
#         elev_value = gdf['ELEV'].iloc[0]
#
#         # 合并当前shp文件的所有几何图形为一个几何图形
#         merged_geometry = unary_union(gdf.geometry)
#
#         # 创建一个新的GeoDataFrame，包含合并后的几何图形和ELEV字段
#         merged_gdf = gpd.GeoDataFrame([[elev_value, merged_geometry]],
#                                       columns=['ELEV', 'geometry'], crs=gdf.crs)
#
#         gdf_list.append(merged_gdf)
#
# # 合并所有GeoDataFrame
# if gdf_list:
#     final_gdf = pd.concat(gdf_list, ignore_index=True)
#
#     # 确保投影为WGS84
#     final_gdf = final_gdf.to_crs(epsg=4326)
#
#     # 保存合并后的shp文件
#     final_gdf.to_file(output_file)
#     print(f'合并后的shp文件已保存至 {output_file}')
# else:
#     print("文件夹中没有找到任何有效的shp文件")

# 只进行单纯的合并
import os
import geopandas as gpd
from shapely.geometry import shape
from shapely.ops import unary_union
import pandas as pd

# 定义输入文件夹路径和输出文件路径
input_folder = r"D:\开发竞赛\数据\高程数据\DEM\Contours"
output_file = r'D:\开发竞赛\数据\高程数据\DEM\Contours\merged_contourLine_multipart.shp'

# 初始化一个空的列表，用于存储所有shp文件的GeoDataFrame
gdf_list = []

# 遍历输入文件夹中的所有shp文件
for file in os.listdir(input_folder):
    if file.endswith('.shp'):
        file_path = os.path.join(input_folder, file)
        gdf = gpd.read_file(file_path)

        # 如果没有CRS，设置默认的CRS
        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)

        # 转换multipart为singlepart
        gdf_singleparts = gdf.explode(index_parts=False)

        gdf_list.append(gdf_singleparts)

# 合并所有GeoDataFrame
if gdf_list:
    merged_gdf = pd.concat(gdf_list, ignore_index=True)

    # 确保投影为WGS84
    merged_gdf = merged_gdf.to_crs(epsg=4326)

    # 保存合并后的shp文件
    merged_gdf.to_file(output_file)
    print(f'合并后的shp文件已保存至 {output_file}')
else:
    print("文件夹中没有找到任何shp文件")
