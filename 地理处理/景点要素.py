import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os

# 使用pandas读取坐标数据
data = pd.read_csv('D:\\开发竞赛\\数据\\景点数据\\坐标.txt',
                   delimiter='：',
                   encoding='utf-8',
                   header=None,
                   names=['name', 'coords'],
                   engine='python')
data[['latitude', 'longitude']] = data['coords'].str.split(', ', expand=True)
data.drop(columns='coords', inplace=True)
data['latitude'] = data['latitude'].astype(float)
data['longitude'] = data['longitude'].astype(float)

# 创建GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))

# 设置坐标参考系统为WGS84 (epsg:4326)
gdf.set_crs(epsg=4326, inplace=True)

# 输出文件夹路径
output_folder = 'D:\\开发竞赛\\数据\\景点数据\\landmarks'

# 确保输出文件夹存在
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 输出文件名
output_filename = 'landmarks.shp'

# 保存GeoDataFrame为Shapefile格式
output_path = os.path.join(output_folder, output_filename)
gdf.to_file(output_path, encoding='utf-8')

print(f'Shapefile saved at {output_path}')
