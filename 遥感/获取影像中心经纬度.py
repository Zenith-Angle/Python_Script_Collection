from osgeo import gdal

filePath = r"D:\yaoganguochengshuju\EX4\fc.tif"  # tif文件路径
dataset = gdal.Open(filePath)  # 打开tif

adfGeoTransform = dataset.GetGeoTransform()  # 读取地理信息

# 左上角地理坐标
print(adfGeoTransform[0])
print(adfGeoTransform[3])

nXSize = dataset.RasterXSize  # 列数
nYSize = dataset.RasterYSize  # 行数

print(nXSize, nYSize)

arrSlope = []  # 用于存储每个像素的（X，Y）坐标
for i in range(nYSize):
    row = []
    for j in range(nXSize):
        px = adfGeoTransform[0] + i * adfGeoTransform[1] + j * adfGeoTransform[2]
        py = adfGeoTransform[3] + i * adfGeoTransform[4] + j * adfGeoTransform[5]
        col = [px, py]  # 每个像素的经纬度
        row.append(col)
        print(col)
    arrSlope.append(row)

