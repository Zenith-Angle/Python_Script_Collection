from osgeo import gdal
import numpy as np


# 读取栅格数据
def read_raster(raster_path):
    dataset = gdal.Open(raster_path)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    return array


# 写入栅格数据
def write_raster(array, reference_path, output_path):
    dataset = gdal.Open(reference_path)
    driver = dataset.GetDriver()
    out_dataset = driver.Create(output_path, dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_Float32)
    out_dataset.SetGeoTransform(dataset.GetGeoTransform())
    out_dataset.SetProjection(dataset.GetProjection())
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(array)
    out_band.FlushCache()
    out_band.SetNoDataValue(-9999)
    out_dataset = None


# 评分函数，根据提供的阈值和权重来计算得分
def score_index(value, thresholds, weights):
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return weights[i]
    return weights[-1]


# 根据图示的评价标准来计算土地评价指数
def evaluate_land(soil_texture, organic_matter, slope, alkalinity, ph, drainage):
    # 设置阈值
    texture_thresholds = [1, 2, 3, 4]  # 从沙质土到粘土
    organic_thresholds = [20, 15, 10, 5, 0]  # 从很低到很高
    slope_thresholds = [25, 15, 6, 2, 0]  # 从陡峭到平坦
    alkalinity_thresholds = [20, 15, 10, 5, 0]  # 从极高到极低
    ph_thresholds = [9, 8.5, 8, 7.5, 6.5]  # 从极酸到极碱
    drainage_thresholds = [7, 6, 5, 4, 3]  # 从极差到极好

    # 设置权重
    weights = [1, 0.8, 0.6, 0.4, 0.2]

    # 计算得分
    texture_scores = np.vectorize(score_index)(soil_texture, texture_thresholds, weights)
    organic_scores = np.vectorize(score_index)(organic_matter, organic_thresholds, weights)
    slope_scores = np.vectorize(score_index)(slope, slope_thresholds, weights)
    alkalinity_scores = np.vectorize(score_index)(alkalinity, alkalinity_thresholds, weights)
    ph_scores = np.vectorize(score_index)(ph, ph_thresholds, weights)
    drainage_scores = np.vectorize(score_index)(drainage, drainage_thresholds, weights)

    # 计算加权平均
    land_evaluation_index = texture_scores + organic_scores + slope_scores + alkalinity_scores + ph_scores + drainage_scores
    land_evaluation_index /= len(weights)  # 这里是简单平均，如果您有不同的权重请进行调整

    return land_evaluation_index


# 文件路径
# ...

# 读取数据
# ...

# 计算土地评价指数
land_evaluation_index = evaluate_land(soil_texture, organic_matter, slope, alkalinity, ph, drainage)

# 输出土地评价指数栅格文件
# ...
