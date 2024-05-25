import geopandas as gpd
from shapely.geometry import Polygon
import os
import pandas as pd


def extract_corners(shp_path, output_folder):
    # 读取shapefile文件
    gdf = gpd.read_file(shp_path)

    # 检查确保几何类型是Polygon
    if not all(gdf.geometry.type == 'Polygon'):
        raise ValueError("所有的几何形状必须是多边形（Polygon）")

    # 按照从上到下、从左到右的顺序排序多边形
    gdf['top'] = gdf.geometry.bounds['maxy']
    gdf['left'] = gdf.geometry.bounds['minx']
    gdf_sorted = gdf.sort_values(by=['top', 'left'], ascending=[False, True])

    # 初始化存储顶点的列表
    corners = []

    # 准备DataFrame以写入Excel
    data_for_excel = pd.DataFrame(columns=['Index', 'TopLeftX', 'TopLeftY', 'BottomRightX', 'BottomRightY'])

    # 遍历排序后的多边形，提取顶点并添加序号
    index = 1
    for i, polygon in enumerate(gdf_sorted.geometry):
        if isinstance(polygon, Polygon):
            minx, miny, maxx, maxy = polygon.bounds
            # 左上角顶点，强制保留小数点后六位
            top_left = (round(minx, 6), round(maxy, 6))
            # 右下角顶点，强制保留小数点后六位
            bottom_right = (round(maxx, 6), round(miny, 6))
            corners.append((index, top_left, bottom_right))
            data_for_excel.loc[i] = [index, top_left[0], top_left[1], bottom_right[0], bottom_right[1]]
            index += 1

    # 添加序号到原始GeoDataFrame
    gdf_sorted['Index'] = data_for_excel['Index'].values

    # 构建更新后的shapefile文件路径，确保不覆盖原有文件
    base_name = os.path.splitext(os.path.basename(shp_path))[0]
    updated_shp_path = os.path.join(os.path.dirname(shp_path), base_name + "_1.shp")
    counter = 1
    while os.path.exists(updated_shp_path):
        counter += 1
        updated_shp_path = os.path.join(os.path.dirname(shp_path), f"{base_name}_{counter}.shp")

    # 保存更新后的shapefile
    gdf_sorted.to_file(updated_shp_path)

    # 构建输出Excel文件的完整路径，文件名为原文件名加上“_vertices”
    output_path = os.path.join(output_folder, f'{base_name}_vertices.xlsx')

    # 将顶点信息保存到Excel文件中
    with pd.ExcelWriter(output_path) as writer:
        data_for_excel.to_excel(writer, index=False)

    print(f"顶点信息已经保存到 '{output_path}'")
    print(f"更新后的shapefile保存在 '{updated_shp_path}'")


# 指定shapefile路径和输出文件夹路径
shp_path = r"D:\开发竞赛\数据\路线数据\西宁\西宁网格1km.shp"
output_folder = r"D:\开发竞赛\数据\路线数据\西宁"
extract_corners(shp_path, output_folder)
