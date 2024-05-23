import requests
import time
import datetime
import json
import os

# 指定输出文件夹路径
output_folder = "path_to_your_folder"  # 请将"path_to_your_folder"替换为你的文件夹路径


def fetch_traffic_data():
    url = "https://restapi.amap.com/v3/traffic/status/circle"
    params = {
        "location": "101.777430,36.618946",
        "level": "2",
        "radius": "5000",
        "output": "json",
        "extensions": "all",
        "key": "bb3a9c2dda05ce08846a2c24357bd0bf"
    }
    response = requests.get(url, params=params)
    return response.json()


def save_data(data):
    # 创建时间戳
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"traffic_data_{timestamp}.json"
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 拼接完整的文件路径
    file_path = os.path.join(output_folder, filename)
    with open(file_path, 'w') as f:
        json.dump(data, f)
    print(f"Data saved at {file_path}")


def main():
    while True:
        data = fetch_traffic_data()
        save_data(data)
        print("Waiting for the next fetch...")
        time.sleep(600)  # 等待10分钟


if __name__ == "__main__":
    main()
