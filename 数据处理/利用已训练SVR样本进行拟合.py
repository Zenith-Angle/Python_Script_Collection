import geopandas as gpd
import joblib
import os


def calculate_exped(shp_path, model_path):
    # 读取 Shapefile 文件
    gdf = gpd.read_file(shp_path)

    # 检查是否存在 trfc_cap 和 pts_num 字段
    if 'trfc_cap' not in gdf.columns or 'pts_num' not in gdf.columns:
        raise ValueError("Shapefile 文件中缺少 'trfc_cap' 或 'pts_num' 字段")

    # 提取特征
    X = gdf[['trfc_cap', 'pts_num']]

    # 加载已训练好的 SVR 模型
    svr_model = joblib.load(model_path)

    # 进行预测
    gdf['exped_c'] = svr_model.predict(X)

    # 生成输出文件路径
    base, ext = os.path.splitext(shp_path)
    output_shp_path = f"{base}_SVR{ext}"

    # 保存结果到新的 Shapefile 文件
    gdf.to_file(output_shp_path, driver='ESRI Shapefile')


# 定义路径
shp_path = r"D:\开发竞赛\数据\路线数据\区域网格5km_staTrafficAndPoints.shp"
model_path = r"D:\开发竞赛\数据\路线数据\模型建立\SVR\svr_model.pkl"

# 调用函数
calculate_exped(shp_path, model_path)
