import os
import re


# 该脚本遍历指定文件夹及其所有子文件夹的文件，确保文件名开头和结尾的序号相同。
# 文件格式为：序号 + 文件名 + 序号 + 后缀。序号为两位数字。

def rename_files_in_folder(folder_path):
    # 定义匹配文件名前后两位数字的正则表达式
    pattern = r'^(?P<front>\d{2})?(?P<name>.*?)(?P<back>\d{2})?$'

    # 遍历文件夹及所有子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # 分离文件名和扩展名
            name, ext = os.path.splitext(file_name)

            # 使用正则表达式匹配文件名前后的序号
            match = re.match(pattern, name)
            if match:
                front_digits = match.group('front')  # 文件名开头的两位数字（可能不存在）
                middle_name = match.group('name')  # 文件名中间的部分
                back_digits = match.group('back')  # 文件名结尾的两位数字（可能不存在）

                # 情况 1: 如果只有后面的序号，没有前面的序号
                if back_digits and not front_digits:
                    new_name = f"{back_digits}{middle_name}{back_digits}{ext}"

                # 情况 2: 如果只有前面的序号，没有后面的序号
                elif front_digits and not back_digits:
                    new_name = f"{front_digits}{middle_name}{front_digits}{ext}"

                # 情况 3: 如果前后都有序号，但前后序号不一致
                elif front_digits and back_digits and front_digits != back_digits:
                    new_name = f"{front_digits}{middle_name}{front_digits}{ext}"

                # 情况 4: 前后都有序号且一致，保持原样
                elif front_digits and back_digits and front_digits == back_digits:
                    new_name = f"{front_digits}{middle_name}{back_digits}{ext}"

                # 情况 5: 如果文件名前后都没有序号，不做修改
                else:
                    continue

                # 生成完整的旧文件路径和新文件路径
                old_file_path = os.path.join(root, file_name)
                new_file_path = os.path.join(root, new_name)

                # 重命名文件（如果名称变化了才执行）
                if old_file_path != new_file_path:
                    os.rename(old_file_path, new_file_path)
                    print(f"文件重命名: {file_name} -> {new_name}")


# 指定文件夹路径
folder_path = r"E:\高数\第15讲"

# 调用函数进行重命名操作
rename_files_in_folder(folder_path)
