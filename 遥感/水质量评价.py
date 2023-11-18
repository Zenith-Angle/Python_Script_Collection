import os
import numpy as np
import rasterio


# 定义计算各项指标TLI值的函数
def calculate_tli_chla(chl_a):
    return 10 * (2.5 + 1.086 * np.log(chl_a))


def calculate_tli_tn(tn):
    return 10 * (5.453 + 1.694 * np.log(tn))


def calculate_tli_tp(tp):
    return 10 * (9.436 + 1.624 * np.log(tp))


def calculate_tli_codmn(cod_mn):
    return 10 * (0.109 + 2.661 * np.log(cod_mn))


# 权重
weights = {
    'chl_a': 0.32606,
    'tn': 0.21924,
    'tp': 0.23007,
    'cod_mn': 0.22462
}

# 输入文件夹路径
input_folder = r"D:\yaoganguochengshuju\EX1\calres"
# 输出文件夹路径
output_folder = r"D:\yaoganguochengshuju\EX1\calres\assessment"

# 创建输出目录
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 文件路径配置
input_files = {
    "2005water": "ETM+",
    "2010water": "ETM+",
    "2016water": "OLI",
    "2020AWEI_nsh_water": "OLI"
}

# 波段对应配置
bands_etm = {"b3": 2, "b4": 3, "b5": 4, "b6": 5, "b7": 6}
bands_oli = {"b3": 3, "b4": 4, "b5": 5, "b6": 6, "b7": 7}

# 处理每个文件
for file_name, sensor_type in input_files.items():
    # 构建输入文件路径
    data_file = os.path.join(input_folder, file_name)

    # 读取数据并计算指标
    with rasterio.open(data_file) as src:
        # 根据传感器类型选择波段
        band_nums = bands_oli if sensor_type == "OLI" else bands_etm
        bands = src.read([band_nums[b] for b in ['b3', 'b4', 'b5', 'b6', 'b7'] if b in band_nums])

        # 分配波段数据
        b3, b4, b5, b6, b7 = [bands[band_nums[b] - 1] if b in band_nums else None for b in
                              ['b3', 'b4', 'b5', 'b6', 'b7']]

        # 计算TLI值
        tli_chla = calculate_tli_chla(b5, b6)
        tli_tn = calculate_tli_tn(b4, b6)
        tli_tp = calculate_tli_tp(b4, b6, b7)
        tli_codmn = calculate_tli_codmn(b3, b5, b7)

        # 保存计算结果到ENVI格式
        profile.update(driver='ENVI')

        output_files = {
            "tli_chla": tli_chla,
            "tli_tn": tli_tn,
            "tli_tp": tli_tp,
            "tli_codmn": tli_codmn
        }

        for output_name, output_data in output_files.items():
            # 设置输出文件路径
            output_file_path = os.path.join(output_folder, f"{file_name}_{output_name}")
            with rasterio.open(output_file_path, 'w', **profile) as dst:
                dst.write(output_data, 1)

        # 计算综合TLI值
        tli_total = (weights['chl_a'] * tli_chla +
                     weights['tn'] * tli_tn +
                     weights['tp'] * tli_tp +
                     weights['cod_mn'] * tli_codmn)

        # 保存综合TLI值到ENVI格式
        output_file_path = os.path.join(output_folder, f"{file_name}_tli_total")
        with rasterio.open(output_file_path, 'w', **profile) as dst:
            dst.write(tli_total, 1)

    print(f"TLI计算并保存完成：{file_name}")
