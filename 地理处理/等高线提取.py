import os
from osgeo import gdal, ogr
from tqdm import tqdm

# 输入DEM文件和输出文件夹路径
dem_file_path = 'D:\\开发竞赛\\数据\\高程数据\\DEM\\DEM.tif'
output_folder = 'D:\\开发竞赛\\数据\\高程数据\\DEM\\Contours'

# 确保输出文件夹存在
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 打开DEM文件
dem_dataset = gdal.Open(dem_file_path)
if dem_dataset is None:
    raise RuntimeError("无法打开文件：{}".format(dem_file_path))

band = dem_dataset.GetRasterBand(1)  # DEM数据通常存储在第一个波段

# 计算波段的统计信息以确保最大值可用
band.ComputeStatistics(False)
max_elevation = band.GetMaximum()

# 确保我们成功获取了最大高程值
if max_elevation is None:
    raise RuntimeError("无法获取波段的最大高程值。")

# 准备输出Shapefile的驱动
driver = ogr.GetDriverByName('ESRI Shapefile')
if driver is None:
    raise RuntimeError("无法加载ESRI Shapefile驱动。")


# 定义创建高程字段的函数
def create_elev_field(layer):
    field_defn = ogr.FieldDefn('ELEV', ogr.OFTInteger)
    if layer.CreateField(field_defn) != 0:
        raise RuntimeError("创建高程字段失败。")
    return layer.FindFieldIndex('ELEV', 1)


# 回调函数，用于更新tqdm进度条
def gdal_progress_callback(complete, message, user_data):
    user_data.update(1)  # 更新进度条
    return 1  # 1表示进度条继续，0将中止操作


# 海拔小于2000米的等高线
output_path_less_2000 = os.path.join(output_folder, 'Contours_Less_2000m.shp')
dataSource_less_2000 = driver.CreateDataSource(output_path_less_2000)
layer_less_2000 = dataSource_less_2000.CreateLayer(output_path_less_2000, geom_type=ogr.wkbLineString)
elev_field_index = create_elev_field(layer_less_2000)

# 生成等高线
gdal.ContourGenerate(band, 0, 0, [2000], 0, 0, layer_less_2000, elev_field_index, 0)
dataSource_less_2000 = None  # 关闭文件

# 海拔2000米以上的等高线，每500米一段
for base_elev in range(2000, int(max_elevation) + 500, 500):
    output_path_above_2000 = os.path.join(output_folder, f'Contours_{base_elev}m.shp')
    dataSource_above_2000 = driver.CreateDataSource(output_path_above_2000)
    layer_above_2000 = dataSource_above_2000.CreateLayer(output_path_above_2000, geom_type=ogr.wkbLineString)
    elev_field_index = create_elev_field(layer_above_2000)

    total_steps = (int(max_elevation) - 2000) // 500 + 1  # 计算总步数
    with tqdm(total=total_steps, desc='提取等高线') as pbar:
        # 使用回调函数更新进度条
        gdal.ContourGenerate(band, 0, 0, [base_elev], 0, 0, layer_above_2000, elev_field_index, 0,
                             callback=gdal_progress_callback, callback_data=pbar)
        dataSource_above_2000 = None  # 关闭文件

print("等高线提取完成。")
