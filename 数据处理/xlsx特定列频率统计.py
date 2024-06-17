import pandas as pd
import json
import os


def process_excel_file(file_path):
    """
    读取Excel文件，跳过第一行，统计第二列数据的频率。

    :param file_path: str, 输入的Excel文件路径
    :return: list, 包含数据及其出现频率的字典列表
    """
    # 读取Excel文件，跳过第一行
    df = pd.read_excel(file_path, skiprows=1)

    # 统计第二列（index为1）的数据频率
    value_counts = df.iloc[:, 1].value_counts().to_dict()

    # 转换为列表的字典形式
    result = [{'name': str(key), 'value': int(value)} for key, value in
              value_counts.items()]
    return result


def generate_stats_json(directory):
    """
    处理指定文件夹下所有xlsx文件，输出到相同文件夹的对应json文件。

    :param directory: str, 文件夹路径
    """
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx'):
            input_path = os.path.join(directory, filename)
            result = process_excel_file(input_path)

            # 准备输出文件路径
            base_name = os.path.splitext(filename)[0]
            output_json = os.path.join(directory, f"{base_name}emotion.json")

            # 保存到JSON文件
            with open(output_json, 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)

            print(f"Data has been written to {output_json}")


# 示例调用，替换 'path/to/your_directory' 为您的文件夹路径
generate_stats_json(r"D:\开发竞赛\数据\景点数据\景点数据分析\景点情感")
