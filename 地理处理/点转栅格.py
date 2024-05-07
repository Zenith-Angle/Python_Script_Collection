import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
import numpy as np
from tqdm import tqdm


def points_to_raster(point_layer_path, range_layer_path, output_raster_path, grid_size=10):
    # 读取点数据和范围数据
    points = gpd.read_file(point_layer_path)
    range_boundary = gpd.read_file(range_layer_path)

    # 获取范围数据的边界
    minx, miny, maxx, maxy = range_boundary.total_bounds

    # 计算栅格的维度
    width = int((maxx - minx) / grid_size) + 1
    height = int((maxy - miny) / grid_size) + 1

    # 创建栅格转换
    transform = from_origin(minx, maxy, grid_size, grid_size)

    # 初始化栅格数组
    raster = np.zeros((height, width), dtype=np.float32)

    # 确保点数据的坐标系与范围数据相同
    if points.crs != range_boundary.crs:
        points = points.to_crs(range_boundary.crs)

    # 进行点到栅格的转换，并在此过程中添加进度条
    for index, point in tqdm(points.iterrows(), total=points.shape[0], desc="Converting points to raster"):
        if point.geometry.within(range_boundary.unary_union):
            row, col = ~transform * (point.geometry.x, point.geometry.y)
            row, col = int(row), int(col)
            raster[row, col] += point['level']  # 累加level值到栅格位置

    # 创建新的栅格文件
    with rasterio.open(
            output_raster_path, 'w', driver='GTiff',
            height=raster.shape[0], width=raster.shape[1],
            count=1, dtype=str(raster.dtype),
            crs=range_boundary.crs, transform=transform
    ) as dst:
        dst.write(raster, 1)

    return output_raster_path


# 示例用法
raster_path = points_to_raster(
    "D:\\开发竞赛\\数据\\景点数据\\landmarks\\点合并_level.shp",
    "D:\\开发竞赛\\数据\\省级数据\\研究区域\\range.shp",
    "D:\\开发竞赛\\数据\\景点数据\\landmarks\\点转栅格.tif",
    grid_size=10
)
print(f"栅格文件已创建：{raster_path}")
