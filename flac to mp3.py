from pydub import AudioSegment
import os


def convert_flac_to_mp3(folder_path):
    # 遍历文件夹内的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为 FLAC 文件
        if filename.endswith('.flac'):
            flac_path = os.path.join(folder_path, filename)
            mp3_path = os.path.join(folder_path, filename[:-5] + '.mp3')

            # 加载 FLAC 文件
            audio = AudioSegment.from_file(flac_path, format="flac")

            # 将音频转换为 MP3 并保存
            audio.export(mp3_path, format="mp3")


# 指定您的文件夹路径
folder_path = r"C:\Users\25830\Downloads\convert.freelrc.com"
convert_flac_to_mp3(folder_path)
