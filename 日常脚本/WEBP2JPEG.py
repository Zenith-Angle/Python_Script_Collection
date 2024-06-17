import os
from PIL import Image


def convert_webp_to_jpg(input_folder, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.webp'):
            webp_path = os.path.join(input_folder, filename)
            jpg_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.jpg")

            # 打开WEBP图片并转换为JPG格式
            with Image.open(webp_path) as img:
                # 转换为RGB模式，因为WEBP可能包含透明通道，而JPG不支持透明通道
                rgb_img = img.convert('RGB')
                rgb_img.save(jpg_path, 'JPEG')
                print(f"已将 {webp_path} 转换为 {jpg_path}")


if __name__ == "__main__":
    input_folder = r"D:\开发竞赛\数据\景点数据\景点图标"  # 替换为你的WEBP图片所在文件夹路径
    output_folder = r"D:\开发竞赛\数据\景点数据\景点图标" # 替换为你希望保存JPG图片的文件夹路径

    convert_webp_to_jpg(input_folder, output_folder)
