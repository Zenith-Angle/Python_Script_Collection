#!/usr/bin/env python3
import os
import shutil


def organize_videos(folder_path):
    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)
    # 遍历所有文件
    for file in files:
        # 生成文件的完整路径
        file_path = os.path.join(folder_path, file)
        # 如果文件是视频文件，且当前路径是一个文件
        if os.path.isfile(file_path) and file.lower().endswith(
                ('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
            # 生成对应的目标文件夹路径
            target_folder = os.path.join(folder_path, os.path.splitext(file)[0])
            # 检查目标文件夹是否存在
            if not os.path.exists(target_folder):
                # 如果目标文件夹不存在则创建
                os.makedirs(target_folder)
            # 生成目标文件的新路径
            new_path = os.path.join(target_folder, file)
            # 移动视频文件到新路径
            shutil.move(file_path, new_path)
            print(f"已移动视频文件: {file} -> {new_path}")


if __name__ == "__main__":
    folder_path = input("请输入要整理的视频文件夹路径: ")
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        organize_videos(folder_path)
        print("视频整理完毕！")
    else:
        print("输入的路径无效或不是一个文件夹，请检查后重新输入。")
