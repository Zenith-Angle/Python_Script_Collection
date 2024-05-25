import geopandas as gpd
import json
import os


def read_json_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def extract_info_from_json(data):
    if data['status'] == "1" and 'trafficinfo' in data and 'evaluation' in data['trafficinfo']:
        eval_info = data['trafficinfo']['evaluation']
        return {
            'exped': eval_info.get('expedite', ''),
            'cong': eval_info.get('congested', ''),
            'block': eval_info.get('blocked', ''),
            'unkn': eval_info.get('unknown', ''),
            'stat': eval_info.get('status', ''),
            'desc': eval_info.get('description', '')
        }
    else:
        return {
            'exped': None,
            'cong': None,
            'block': None,
            'unkn': None,
            'stat': None,
            'desc': None
        }


def update_shapefile_with_json(shapefile_path, json_folder):
    # 读取 Shapefile
    gdf = gpd.read_file(shapefile_path)

    # 初始化新字段
    for field in ['time', 'exped', 'cong', 'block', 'unkn', 'stat', 'desc']:
        if field not in gdf.columns:
            gdf[field] = None

    # 遍历 JSON 文件并更新 Shapefile
    for file_name in os.listdir(json_folder):
        if file_name.endswith('.json'):
            index = float(file_name.split('_')[1].split('.')[0])
            json_path = os.path.join(json_folder, file_name)
            json_data = read_json_data(json_path)
            info = extract_info_from_json(json_data)
            time = file_name.split('_')[0]

            # 更新对应 Index 的行
            row_mask = gdf['Index'] == index
            if row_mask.any():  # 确保至少有一行匹配
                for key, value in info.items():
                    if isinstance(value, list):
                        value = value[0] if value else None
                    gdf.loc[row_mask, key] = value
                gdf.loc[row_mask, 'time'] = time
            else:
                print(f"No matching index found for index {index}.")

    # 保存更新后的 Shapefile
    new_shapefile_path = os.path.splitext(shapefile_path)[0] + "_traffic.shp"
    gdf.to_file(new_shapefile_path, encoding='GBK')


# 调用函数
shapefile_path = r"D:\开发竞赛\数据\路线数据\西宁\西宁网格1km_1.shp"
json_folder = r"D:\开发竞赛\数据\路线数据\道路状况\请求结果_1km"
update_shapefile_with_json(shapefile_path, json_folder)
