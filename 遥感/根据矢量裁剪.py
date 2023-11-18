from osgeo import gdal, ogr
import os


def repair_geometry(shapefile_path):
    """
    尝试修复矢量文件中的无效几何。

    :param shapefile_path: 矢量文件路径。
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shapefile_path, 1)  # 1 表示可编辑模式
    layer = dataSource.GetLayer()

    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom.IsValid():
            continue
        repaired = geom.Buffer(0)
        if repaired.IsValid():
            feature.SetGeometry(repaired)
            layer.SetFeature(feature)

    dataSource = None


def clip_raster_by_shapefile(raster_path, shapefile_path, output_path):
    """
    使用矢量文件裁剪栅格文件。

    :param raster_path: 栅格文件路径 (ENVI文件)。
    :param shapefile_path: 矢量文件路径。
    :param output_path: 裁剪后的栅格文件保存路径。
    """
    # 打开栅格文件
    raster = gdal.Open(raster_path)
    if raster is None:
        raise FileNotFoundError(f"未找到栅格文件: {raster_path}")

    # 打开矢量文件
    driver = ogr.GetDriverByName("ESRI Shapefile")
    shapefile = driver.Open(shapefile_path)
    if shapefile is None:
        raise FileNotFoundError(f"未找到矢量文件: {shapefile_path}")

    # 执行裁剪操作
    gdal.Warp(output_path, raster, format="ENVI", cutlineDSName=shapefile_path, cropToCutline=True, dstNodata=0)


def process_files(base_dir, years):
    """
    处理指定年份的ENVI文件和矢量文件。

    :param base_dir: 文件所在的基本目录。
    :param years: 要处理的年份列表。
    """
    for year in years:
        raster_file = os.path.join(base_dir, f"{year}flaash")
        shapefile = os.path.join(base_dir, f"{year}AWEI_nsh.shp")
        output_file = os.path.join(base_dir, "data", f"{year}water")

        try:
            repair_geometry(shapefile)
            clip_raster_by_shapefile(raster_file, shapefile, output_file)
            print(f"{year}年的文件处理成功。")
        except FileNotFoundError as e:
            print(f"处理{year}年的文件时出错: {e}")


# 要处理的目录和年份
base_directory = "D:/yaoganguochengshuju/EX1"
years_to_process = [2005, 2010, 2016, 2020]

# 处理文件
process_files(base_directory, years_to_process)
