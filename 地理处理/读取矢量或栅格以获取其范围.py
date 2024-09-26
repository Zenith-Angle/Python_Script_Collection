import geopandas as gpd
import rasterio
from pyproj import Proj, transform
from datetime import datetime


def decimal_to_dms(decimal):
    """Convert decimal degrees to degrees, minutes, seconds."""
    d = int(decimal)
    m = int((decimal - d) * 60)
    s = ((decimal - d) * 60 - m) * 60
    return d, m, s


def convert_to_wgs84(x, y, source_crs):
    """Convert coordinates from source CRS to WGS84 (EPSG:4326)."""
    target_crs = Proj(init='epsg:4326')
    lon, lat = transform(source_crs, target_crs, x, y)
    return lon, lat


def print_decimal_degree_bounds(bounds, file_type):
    """Print bounds in decimal degree format."""
    print(
        f"{file_type}范围（十进制度）：xmin={bounds[0]}, ymin={bounds[1]}, xmax={bounds[2]}, ymax={bounds[3]}")


def print_dms_bounds(bounds, file_type):
    """Print bounds in degrees, minutes, seconds format."""
    min_lon_dms = decimal_to_dms(bounds[0])
    max_lon_dms = decimal_to_dms(bounds[2])
    min_lat_dms = decimal_to_dms(bounds[1])
    max_lat_dms = decimal_to_dms(bounds[3])

    print(f"{file_type}范围（度分秒）：")
    print(
        f"经度范围：{min_lon_dms[0]}°{min_lon_dms[1]}'{min_lon_dms[2]:.2f}\" 至 {max_lon_dms[0]}°{max_lon_dms[1]}'{max_lon_dms[2]:.2f}\"")
    print(
        f"纬度范围：{min_lat_dms[0]}°{min_lat_dms[1]}'{min_lat_dms[2]:.2f}\" 至 {max_lat_dms[0]}°{max_lat_dms[1]}'{max_lat_dms[2]:.2f}\"")


def print_shapefile_extent(file_path):
    # Read Shapefile
    gdf = gpd.read_file(file_path)
    bounds = gdf.total_bounds

    # Check if coordinates are in meters (assuming UTM or similar projection)
    if gdf.crs and gdf.crs.is_projected:
        source_crs = gdf.crs
        min_lon, min_lat = convert_to_wgs84(bounds[0], bounds[1], source_crs)
        max_lon, max_lat = convert_to_wgs84(bounds[2], bounds[3], source_crs)
        print_decimal_degree_bounds((min_lon, min_lat, max_lon, max_lat), "Shapefile")
        print_dms_bounds((min_lon, min_lat, max_lon, max_lat), "Shapefile")
    else:
        print_decimal_degree_bounds(bounds, "Shapefile")


# 从控制台输入文件路径
file_path = input("请输入要读取的 Shapefile 文件路径：\n")

# 打印 Shapefile 的范围信息
print_shapefile_extent(file_path)
