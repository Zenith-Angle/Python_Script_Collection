import pandas as pd
import requests
import time
import random
import json
from datetime import datetime
import os
from tqdm import tqdm  # Import tqdm for progress bar


def load_coordinates(excel_path):
    # Load the Excel file
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
    # Get current datetime to use in filename
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{now}_{index}.json"
    filepath = os.path.join(folder_path, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    excel_path = "C:\\Users\\25830\\OneDrive - oganneson\\开发竞赛\\数据\\路线数据\\道路状况\\corners_and_centroids.xlsx"
    output_folder = "C:\\Users\\25830\\OneDrive - oganneson\\开发竞赛\\数据\\路线数据\\道路状况\\请求结果"
    api_key = "bb3a9c2dda05ce08846a2c24357bd0bf"

    df = load_coordinates(excel_path)

    # Use tqdm to display a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing API requests"):
        rectangle = f"{row['TopLeftX']},{row['TopLeftY']};{row['BottomRightX']},{row['BottomRightY']}"
        # Random delay to avoid being banned
        time.sleep(10 + random.uniform(0, 5))
        response_data = make_request(rectangle, api_key)
        save_json(response_data, row['Index'], output_folder)
        print(f"Request {row['Index']} completed and saved.")


if __name__ == "__main__":
    main()
