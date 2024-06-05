import pandas as pd
from shapely.geometry import box, Polygon
import json
import os
from datetime import datetime


def process_and_output_json(lon1, lat1, lon2, lat2, output_folder):
    """
    处理给定的两个坐标点，筛选出符合条件的网格，并输出到JSON文件
    """
    # 固定的csv文件路径
    csv_path = r"C:\Users\25830\OneDrive - oganneson\开发竞赛\数据\路线数据\网格筛选结果\网格信息.csv"

    # 读取csv文件
    df = pd.read_csv(csv_path)

    # 创建矩形框，用于筛选
    minx, miny = min(lon1, lon2), min(lat1, lat2)
    maxx, maxy = max(lon1, lon2), max(lat1, lat2)
    bounding_box = box(minx, miny, maxx, maxy)

    # 准备数据列表
    features = []

    # 遍历DataFrame的每一行
    for index, row in df.iterrows():
        # 创建网格的Polygon
        polygon = Polygon([
            (row['x1'], row['y1']),
            (row['x2'], row['y2']),
            (row['x3'], row['y3']),
            (row['x4'], row['y4'])
        ])

        # 如果网格与矩形框相交
        if polygon.intersects(bounding_box):
            # 添加网格信息到列表
            features.append({
                "id": row['id'],
                "exped_c": row['exped_c'],
                "coordinates": [(row['x1'], row['y1']), (row['x2'], row['y2']),
                                (row['x3'], row['y3']), (row['x4'], row['y4'])]
            })

    # 筛选出exped_c最小的前16个网格
    features = sorted(features, key=lambda x: x['exped_c'])[:16]

    # 输出到指定的json文件
    output_file = datetime.now().strftime("%Y%m%d%H%M%S") + "_output.json"
    output_path = os.path.join(output_folder, output_file)
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=4)

    print(f"输出文件已保存到：{output_path}")


# 示例调用
lon1, lat1 = 104.705695, 35.563318
lon2, lat2 = 98.439735, 39.727449
output_folder = r"C:\Users\25830\OneDrive - oganneson\开发竞赛\数据\路线数据\网格筛选结果"
process_and_output_json(lon1, lat1, lon2, lat2, output_folder)
