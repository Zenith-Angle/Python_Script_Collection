import os
import subprocess
from PIL import Image


def convert_avif_to_jpg_and_merge_to_pdf(folder_path, output_pdf_path):
    # 搜索文件夹中所有的AVIF文件
    avif_files = [f for f in os.listdir(folder_path) if f.endswith('.avif')]

    converted_images = []

    for file in avif_files:
        file_path = os.path.join(folder_path, file)
        jpg_path = file_path.rsplit('.', 1)[0] + '.jpg'

        # 使用ffmpeg将AVIF转换为JPG
        subprocess.run(['ffmpeg', '-i', file_path, jpg_path])

        converted_images.append(jpg_path)

    # 将所有的JPG文件合并到一个PDF文件中
    if converted_images:
        image_list = [Image.open(img_path).convert('RGB') for img_path in converted_images[1:]]
        first_image = Image.open(converted_images[0])
        first_image.convert('RGB').save(output_pdf_path, save_all=True, append_images=image_list)


# 使用示例：将 'my_folder' 内的AVIF文件转换并合并到 'output.pdf'
convert_avif_to_jpg_and_merge_to_pdf(r"Z:\漫画\【搬运】[藤本树][幕間堂漢化][短篇]蓦然回首_-_哔哩哔哩", r'蓦然回首.pdf')
