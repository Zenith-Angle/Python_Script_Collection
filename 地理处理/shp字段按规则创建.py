import geopandas as gpd
import numpy as np


def add_level_field(input_shp, output_shp):
    # 读取Shapefile
    gdf = gpd.read_file(input_shp)

    # 确保fclass字段存在
    if 'fclass' not in gdf.columns:
        raise ValueError("fclass字段不存在于Shapefile中")

    # 添加level字段，初始化为0
    gdf['level'] = 0

    # 定义条件和对应的值
    conditions = [
        (gdf['fclass'].str.contains('trunk')) | (gdf['fclass'].str.contains('motorway')),
        (gdf['fclass'].str.contains('primary')),
        (gdf['fclass'].str.contains('secondary')),
        (gdf['fclass'].str.contains('tertiary'))
    ]
    values = [4, 3, 2, 1]

    # 使用numpy.select设置level值
    gdf['level'] = np.select(conditions, values, default=0)

    # 保存修改后的Shapefile
    gdf.to_file(output_shp, driver='ESRI Shapefile')

# 使用示例
input_shp = r"D:\开发竞赛\数据\路线数据\road.shp"
output_shp = r"D:\开发竞赛\数据\路线数据\路线\roads.shp"
add_level_field(input_shp, output_shp)
