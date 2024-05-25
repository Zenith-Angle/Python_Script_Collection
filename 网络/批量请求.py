import pandas as pd
import requests
import time
import random
import json
from datetime import datetime
import os
from tqdm import tqdm  # 导入 tqdm 来显示进度条


def load_coordinates(excel_path):
    # 从 Excel 文件中加载数据
    df = pd.read_excel(excel_path)
    return df


def make_request(rectangle, api_key):
    url = "https://restapi.amap.com/v3/traffic/status/rectangle"
    params = {
        "extensions": "all",
        "key": api_key,
        "rectangle": rectangle,
        "output": "json",
        "level": 6
    }
    response = requests.get(url, params=params)
    return response.json()


def save_json(data, index, folder_path):
    # 获取当前日期时间作为文件名
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{now}_{index}.json"
    filepath = os.path.join(folder_path, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    excel_path = r"D:\开发竞赛\数据\路线数据\西宁\西宁网格1.5km_vertices.xlsx"
    output_folder = r"D:\开发竞赛\数据\路线数据\道路状况\请求结果_1.5km"
    api_keys = ["bb3a9c2dda05ce08846a2c24357bd0bf", "eb1c2fe24b0043e604d6086b80d4ae23", "61d3b28494eb37472e64606fdef59c51"]  # 在这里添加所有 API keys

    df = load_coordinates(excel_path)

    # 使用 tqdm 显示进度条
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing API requests"):
        rectangle = f"{row['TopLeftX']},{row['TopLeftY']};{row['BottomRightX']},{row['BottomRightY']}"
        # 通过索引和 keys 列表的长度取余来交替使用 keys
        api_key = api_keys[index % len(api_keys)]
        # 随机延迟以避免被封禁
        time.sleep(2 + random.uniform(0, 1))
        response_data = make_request(rectangle, api_key)
        save_json(response_data, row['Index'], output_folder)
        print(f"Request {row['Index']} completed and saved.")


if __name__ == "__main__":
    main()
