import geopandas as gpd
from shapely.geometry import box
import json
import os
from datetime import datetime


def process_and_output_json(lon1, lat1, lon2, lat2, output_folder):
    """
    处理给定的两个坐标点，筛选出符合条件的网格，并输出到JSON文件
    """
    # 固定的shp文件路径
    shp_path = r"C:\Users\25830\OneDrive - oganneson\开发竞赛\数据\路线数据\区域网格5km_小于0.5.shp"

    # 读取shp文件
    gdf = gpd.read_file(shp_path)

    # 创建矩形框
    minx, miny = min(lon1, lon2), min(lat1, lat2)
    maxx, maxy = max(lon1, lon2), max(lat1, lat2)
    bounding_box = box(minx, miny, maxx, maxy)

    # 筛选出与矩形相交的网格
    selected_gdf = gdf[gdf.intersects(bounding_box)]

    # 找出`exped_c`最小的前16个网格
    top16_gdf = selected_gdf.nsmallest(16, 'exped_c')

    # 提取网格的坐标和exped_c值
    features = []
    for index, row in top16_gdf.iterrows():
        geometry = row.geometry
        # 获取所有不重复的顶点坐标
        coordinates = list(geometry.exterior.coords)
        unique_coordinates = [coordinates[i] for i in
                              range(len(coordinates) - 1)]  # 移除重复的最后一个点
        features.append({
            "coordinates": unique_coordinates,
            "exped_c": row['exped_c']
        })

    # 输出到指定的json文件
    output_file = datetime.now().strftime("%Y%m%d%H%M%S") + "_output.json"
    output_path = os.path.join(output_folder, output_file)
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=4)

    print(f"输出文件已保存到：{output_path}")


# 示例调用
lon1, lat1 = 104.705695, 35.563318
lon2, lat2 = 98.439735, 39.727449
output_folder = r"C:\Users\25830\OneDrive - oganneson\开发竞赛\数据\路线数据\网格筛选结果"
process_and_output_json(lon1, lat1, lon2, lat2, output_folder)
