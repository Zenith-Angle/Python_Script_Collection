import geopandas as gpd
import pandas as pd


def shp_to_csv(shp_path, csv_path):
    # 读取shp文件
    gdf = gpd.read_file(shp_path)

    # 准备数据列表
    data = []

    # 遍历每个网格
    for index, row in gdf.iterrows():
        geometry = row.geometry
        # 获取网格的四个顶点坐标，移除重复点
        coordinates = list(geometry.exterior.coords)[:-1]
        # 确保只有四个顶点的情况下进行处理
        if len(coordinates) == 4:
            data.append({
                "id": index,
                "exped_c": row['exped_c'],
                "x1": round(coordinates[0][0], 6), "y1": round(coordinates[0][1], 6),
                "x2": round(coordinates[1][0], 6), "y2": round(coordinates[1][1], 6),
                "x3": round(coordinates[2][0], 6), "y3": round(coordinates[2][1], 6),
                "x4": round(coordinates[3][0], 6), "y4": round(coordinates[3][1], 6),
            })

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 保存为CSV
    df.to_csv(csv_path, index=False)
    print(f"文件已保存至：{csv_path}")


# 示例使用
shp_path = r"C:\Users\25830\OneDrive - oganneson\开发竞赛\数据\路线数据\区域网格5km_小于0.5.shp"
csv_path = r"C:\Users\25830\OneDrive - oganneson\开发竞赛\数据\路线数据\网格筛选结果\网格信息.csv"
shp_to_csv(shp_path, csv_path)
