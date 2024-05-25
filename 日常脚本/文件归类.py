import os
import shutil

# 定义文件类型和目标文件夹的映射
file_types = {
    'Compressed': ['zip', 'rar', 'r0*', 'r1*', 'arj', 'gz', 'sit', 'sitx', 'sea', 'ace', 'bz2', '7z'],
    'Document': ['doc', 'pdf', 'ppt', 'pps', 'docx', 'pptx','xlsx', 'xls', 'txt', 'rtf', 'md', 'csv'],
    'Music': ['mp3', 'wav', 'wma', 'mpa', 'ram', 'ra', 'aac', 'aif', 'm4a', 'tsa'],
    'Application': ['exe', 'msi'],
    'Video': ['avi', 'mpg', 'mpe', 'mpeg', 'asf', 'wmv', 'mov', 'qt', 'rm', 'mp4', 'flv', 'm4v', 'webm', 'ogv', 'ogg',
              'mkv', 'ts', 'tsv']
}


def organize_files(source_folder):
    for category, extensions in file_types.items():
        # 创建目标文件夹
        target_folder = os.path.join(source_folder, category)
        os.makedirs(target_folder, exist_ok=True)

        # 移动文件
        for ext in extensions:
            # 处理通配符 *
            if '*' in ext:
                files = [f for f in os.listdir(source_folder) if f.startswith(ext.replace('*', ''))]
            else:
                files = [f for f in os.listdir(source_folder) if f.endswith(ext)]

            for file in files:
                source_file = os.path.join(source_folder, file)
                target_file = os.path.join(target_folder, file)
                if os.path.isfile(source_file):
                    shutil.move(source_file, target_file)
                    print(f"Moved: {source_file} -> {target_file}")


# 设置源文件夹路径
source_folder = r"C:\Users\25830\Downloads"

# 调用整理函数
organize_files(source_folder)
