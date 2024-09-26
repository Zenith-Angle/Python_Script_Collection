import requests
import time
import datetime
import json
import os

# 指定输出文件夹路径
output_folder = r"C:\Users\25830\Downloads\Compressed\lzw\results_old"  # 请将"path_to_your_folder"替换为你的文件夹路径


def fetch_traffic_data():
    url = "https://restapi.amap.com/v3/traffic/status/rectangle"
    params = {
        "extensions": "all",
        "key": "eb1c2fe24b0043e604d6086b80d4ae23",
        "rectangle": "101.730569,36.655544;101.764569,36.621544",
        "output": "json",
        "level": 6
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
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # 使用ensure_ascii参数来保证汉字的正确编码
    print(f"Data saved at {file_path}")


def main():
    while True:
        data = fetch_traffic_data()
        save_data(data)
        print("Waiting for the next fetch...")
        time.sleep(900)


if __name__ == "__main__":
    main()
