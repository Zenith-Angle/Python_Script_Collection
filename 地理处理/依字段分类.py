import geopandas as gpd
import pandas as pd
from pathlib import Path


# 加载数据
def load_shapefile(filepath):
    return gpd.read_file(filepath)


# 根据季节分类并保存
def process_and_save_shapefiles(df, date_column, filepath):
    # 从日期字段提取月份
    months = pd.to_datetime(df[date_column]).dt.month

    # 根据月份分配季节
    bins = [0, 2, 5, 8, 12]
    labels = ['寒', '春', '暑', '秋']
    seasons = pd.cut(months, bins=bins, labels=labels, right=False)

    # 确保所有文本字段都是UTF-8字符串
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.encode('utf-8').str.decode('utf-8')

    # 保存每个季节的数据到新的Shapefile
    base_path = Path(filepath).stem
    output_directory = Path(filepath).parent

    for season in labels:
        season_data = df[seasons == season].copy()
        if not season_data.empty:
            output_path = output_directory / f"{base_path}_{season}.shp"
            season_data.to_file(output_path)


# 主函数
def process_shapefile(filepath):
    df = load_shapefile(filepath)
    process_and_save_shapefiles(df, 'create_tim', filepath)


# 调用主函数处理shp文件
process_shapefile(r"D:\开发竞赛\数据\路线数据\裁剪后微博.shp")
