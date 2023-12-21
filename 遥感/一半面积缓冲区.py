import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np


def calculate_external_buffer_area(feature, target_area):
    """
    计算给定要素的外部缓冲区，使其面积达到目标面积。
    """
    original_area = feature.area
    buffer_distance = 0
    increment = 10  # 初始增量
    tolerance = 0.01  # 容差

    while True:
        buffered_feature = feature.buffer(buffer_distance)
        external_buffer_area = buffered_feature.area - original_area

        if np.isclose(external_buffer_area, target_area, rtol=tolerance):
            return buffered_feature.difference(feature)

        if external_buffer_area < target_area:
            buffer_distance += increment
        else:
            increment /= 2
            buffer_distance -= increment


# 读取shp文件
gdf = gpd.read_file(r"D:\yaoganguochengshuju\EX5\Edge\2020.shp")

# 计算每个要素的外部缓冲区
buffered_geometries = gdf['geometry'].apply(lambda x: calculate_external_buffer_area(x, x.area * 0.5))

# 将外部缓冲区保存到新的GeoDataFrame
buffered_gdf = gpd.GeoDataFrame(geometry=buffered_geometries)

# 保存为新的shp文件
buffered_gdf.to_file(r"D:\yaoganguochengshuju\EX5\Edge\2015_r1.shp")
