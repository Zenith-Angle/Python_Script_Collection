import os
from osgeo import gdal

# 指定包含DEM数据的文件夹路径
input_folder = 'D:\\开发竞赛\\数据\\高程数据\\DEM'
output_file = 'D:\\开发竞赛\\数据\\高程数据\\DEM\\DEM.tif'

# 搜索文件夹中所有符合命名规则的.img文件
dem_files = []
for filename in os.listdir(input_folder):
    if filename.startswith('srtm_') and filename.endswith('.img'):
        dem_files.append(os.path.join(input_folder, filename))

# 检查是否找到了DEM文件
if not dem_files:
    print('没有找到符合条件的DEM文件。')
else:
    # 使用GDAL的Python绑定直接合并DEM文件
    # 创建一个虚拟的VRT文件，将所有DEM图层作为输入
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
    vrt = gdal.BuildVRT(os.path.join(input_folder, 'temp.vrt'), dem_files, options=vrt_options)

    # 将VRT转换为GeoTIFF格式
    gdal.Translate(output_file, vrt, format='GTiff')

    # 清理：关闭VRT文件并删除虚拟文件（如果需要保留虚拟文件，则可以注释掉删除代码）
    vrt = None  # 关闭VRT文件
    os.remove(os.path.join(input_folder, 'temp.vrt'))  # 删除虚拟文件

    print(f'合并完成，输出文件为：{output_file}')
