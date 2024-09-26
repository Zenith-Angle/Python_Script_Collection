import os
from googletrans import Translator

# 定义文件夹路径
folder_path = r"E:\myfans视频" # 请将此路径替换为你的文件夹路径

# 创建翻译器对象
translator = Translator()


# 定义一个函数来清理文件名
def sanitize_filename(filename):
    # 删除或替换文件名中无效的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename


# 收集现有的文件名以避免重名
existing_filenames = set(os.listdir(folder_path))

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    # 跳过目录
    if os.path.isdir(file_path):
        continue
    # 将文件名分成名称和扩展名
    name, ext = os.path.splitext(filename)
    # 翻译名称部分
    try:
        translation = translator.translate(name, src='ja', dest='zh-cn')
        new_name = sanitize_filename(translation.text)
        new_filename = new_name + ext
        # 处理可能的重名情况
        original_new_filename = new_filename
        counter = 1
        while new_filename in existing_filenames:
            new_filename = f"{new_name}_{counter}{ext}"
            counter += 1
        # 更新现有文件名集合
        existing_filenames.add(new_filename)
        # 获取新的完整路径
        new_file_path = os.path.join(folder_path, new_filename)
        # 重命名文件
        os.rename(file_path, new_file_path)
        print(f'已将 "{filename}" 重命名为 "{new_filename}"')
    except Exception as e:
        print(f'翻译 "{filename}" 时出错: {e}')
