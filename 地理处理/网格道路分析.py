# traffic_analysis.py
#
# 本脚本用于分析交通数据，计算网格内的道路容纳力和点的数量。
# - 道路容纳力是根据道路类型（从tertiary到motorway）的重要性赋予不同的权重。
# - 点的数量是统计在每个网格内的点的总数。
# 输入包括三个Shapefile：网格、道路和点。
# 输出是修改后的网格Shapefile，其中添加了两个新字段：
#   - 'trfc_cap': 网格内所有道路的总容纳力，长度乘以容纳力系数后除以10。
#   - 'pts_num': 网格内点的数量。
# 输出文件将保存在输入网格文件的同一目录下，并在文件名后加上'_staTrafficAndPoints'。

import geopandas as gpd
import os


def calculate_traffic_capacity_and_points(grid_path, roads_path, points_path):
    # 加载数据
    grid = gpd.read_file(grid_path)
    roads = gpd.read_file(roads_path)
    points = gpd.read_file(points_path)

    # 为道路赋值容纳力
    capacity_values = {
        'tertiary': 1, 'tertiary_link': 1,
        'secondary': 2, 'secondary_link': 2,
        'primary': 3, 'primary_link': 3,
        'trunk': 4, 'trunk_link': 4,
        'motorway': 4, 'motorway_link': 4
    }
    roads['capacity'] = roads['fclass'].map(capacity_values)

    # 计算每个网格的道路容纳力
    def sum_road_capacity(geom):
        intersected_roads = roads[roads.geometry.intersects(geom)]
        # 使用道路长度乘以容纳力系数，再除以10
        total_capacity = (intersected_roads['length'] * intersected_roads['capacity']).sum() / 100
        return round(total_capacity, 6)  # 保留6位小数

    grid['trfc_cap'] = grid.geometry.apply(sum_road_capacity)

    # 计算每个网格内的点的数量
    def count_points(geom):
        intersected_points = points[points.geometry.intersects(geom)]
        return len(intersected_points)

    grid['pts_num'] = grid.geometry.apply(count_points)

    # 输出文件，使用输入网格文件的目录
    output_path = os.path.join(os.path.dirname(grid_path),
                               os.path.basename(grid_path).replace('.shp', '_staTrafficAndPoints.shp'))
    grid.to_file(output_path)


# 调用函数
calculate_traffic_capacity_and_points(
    r"D:\开发竞赛\数据\路线数据\西宁\西宁网格1km_1_traffic.shp",
    r"D:\开发竞赛\数据\路线数据\西宁\西宁road投影转地理.shp",
    r"D:\开发竞赛\数据\路线数据\西宁\西宁_wb.shp"
)
