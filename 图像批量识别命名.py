import cv2
import numpy as np
import os
from sklearn.metrics import pairwise_distances_argmin
from PIL import Image
import numpy as np
import os
from sklearn.metrics import pairwise_distances_argmin

# 预定义的颜色和它们对应的 HEX 代码
COLORS = {
    '红色': '#FF0000',
    '绿色': '#008000',
    '蓝色': '#0000FF',
    '黄色': '#FFFF00',
    '青色': '#00FFFF',
    '洋红': '#FF00FF',
    '白色': '#FFFFFF',
    '黑色': '#000000',
    '灰色': '#808080',
    '藏青色': '#000080',
    '橄榄色': '#808000',
    '酸橙色': '#00FF00',
    '紫色': '#800080',
    '蓝绿色': '#008080',
    '水色': '#00FFFF',
    '褐红色': '#800000',
    '紫红色': '#FF00FF',
    '银色': '#C0C0C0',
    '皇家蓝': '#4169E1',
    '橙色': '#FFA500',
    '粉红色': '#FFC0CB',
    '棕色': '#A52A2A',
    '金色': '#FFD700',
    '紫罗兰': '#EE82EE',
    '靛蓝色': '#4B0082',
    '米色': '#F5F5DC',
    '天蓝色': '#87CEFA',
    '橙红色': '#FF4500',
    '深红色': '#8B0000',
    '浅灰色': '#D3D3D3',
    '深灰色': '#A9A9A9',
    '翠绿色': '#7FFF00',
    '巧克力色': '#D2691E',
    '珊瑚色': '#FF7F50'
}

COLORS_RGB = {name: [int(hex_code[i:i + 2], 16) for i in (1, 3, 5)] for name, hex_code in COLORS.items()}

# 将 HEX 颜色代码转换为 RGB
COLORS_RGB = {name: [int(hex_code[i:i + 2], 16) for i in (1, 3, 5)] for name, hex_code in COLORS.items()}


def get_main_color(image):
    mean_color = cv2.mean(image)[:3]
    return mean_color


def find_nearest_color_name(rgb_color):
    color_names = list(COLORS_RGB.keys())
    color_values = np.array(list(COLORS_RGB.values()))
    idx = pairwise_distances_argmin([rgb_color], color_values)
    return color_names[idx[0]]


def process_images(folder_path):
    # 首先删除文件名中的#字符
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            new_filename = filename.replace('#', '')  # 删除文件名中的#字符
            new_file_path = os.path.join(folder_path, new_filename)
            os.rename(file_path, new_file_path)  # 重命名文件

    # 然后根据颜色和尺寸重命名图像
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                image = Image.open(file_path)
            except Exception as e:
                print(f"无法读取图像：{file_path}，错误：{e}")
                continue  # 跳过无法读取的图像

            main_color = get_main_color(image)
            color_name = find_nearest_color_name(main_color)
            width, height = image.size
            new_filename = f"{color_name}_{width}x{height}.png"
            new_file_path = os.path.join(folder_path, new_filename)

            # 检查新文件名是否已经存在，如果存在，则添加一个唯一的后缀
            suffix = 1
            while os.path.exists(new_file_path):
                new_filename = f"{color_name}_{width}x{height}_{suffix}.png"
                new_file_path = os.path.join(folder_path, new_filename)
                suffix += 1

            os.rename(file_path, new_file_path)  # 重命名文件


def get_main_color(image):
    # 将 Pillow 图像对象转换为 NumPy 数组
    numpy_image = np.array(image)
    # 计算图像的平均颜色
    mean_color = np.mean(numpy_image, axis=(0, 1))[:3]
    return mean_color


# 调用函数，传入你的文件夹路径
process_images("D:\\前端学习\\html\\色图")
