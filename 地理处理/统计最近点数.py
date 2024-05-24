import geopandas as gpd
from shapely.ops import nearest_points
import os


def load_shapefiles(points_path, lines_path):
    # 加载点和线的shapefile
    points_gdf = gpd.read_file(points_path)
    lines_gdf = gpd.read_file(lines_path)
    return points_gdf, lines_gdf


def find_nearest_lines(points_gdf, lines_gdf):
    # 计算每个点的最近线
    points_gdf['nearest_line'] = points_gdf.apply(
        lambda row: lines_gdf.geometry.iloc[lines_gdf.distance(row.geometry).idxmin()],
        axis=1
    )
    return points_gdf


def count_points_per_line(points_gdf):
    # 统计每条线的点数
    line_count = {}
    for line in points_gdf['nearest_line']:
        line_count[line] = line_count.get(line, 0) + 1
    return line_count


def set_levels(lines_gdf, line_count):
    # 添加和更新"level"字段，考虑"fclass"限制
    def apply_level_limits(line, fclass):
        count = line_count.get(line, 0)
        if fclass in ['motorway', 'motorway_link']:
            return min(count, 200)
        elif fclass in ['primary', 'primary_link']:
            return min(count, 100)
        return count

    lines_gdf['level'] = lines_gdf.apply(
        lambda row: apply_level_limits(row.geometry, row['fclass']),
        axis=1
    )
    return lines_gdf


def save_new_shapefile(lines_gdf, input_path):
    # 生成新的文件名并保存修改后的shapefile
    base = os.path.splitext(input_path)[0]
    new_path = base + "_wb.shp"
    lines_gdf.to_file(new_path)
    return new_path


# 使用示例
points_path = r"D:\开发竞赛\数据\路线数据\西宁\西宁_wb.shp"
lines_path = r"D:\开发竞赛\数据\路线数据\西宁\西宁road.shp"

points_gdf, lines_gdf = load_shapefiles(points_path, lines_path)
points_gdf = find_nearest_lines(points_gdf, lines_gdf)
line_count = count_points_per_line(points_gdf)
lines_gdf = set_levels(lines_gdf, line_count)
new_shapefile_path = save_new_shapefile(lines_gdf, lines_path)

print("新的shapefile已保存至:", new_shapefile_path)
