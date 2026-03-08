import os
import shutil
import sys
from collections import defaultdict


def move_files_to_individual_folders(path):
    """
    将指定路径中的文件移动到以文件名（不含后缀）命名的文件夹中
    同名文件（不同后缀）会放在同一个文件夹中

    Args:
        path: 要处理的目录路径
    """
    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"错误：路径 '{path}' 不存在！")
        return

    # 确保路径是目录
    if not os.path.isdir(path):
        print(f"错误：'{path}' 不是目录！")
        return

    # 获取目录中的所有文件和文件夹
    items = os.listdir(path)

    # 只处理文件，跳过目录
    files = [item for item in items if os.path.isfile(os.path.join(path, item))]

    if not files:
        print(f"在 '{path}' 中没有找到文件。")
        return

    print(f"找到 {len(files)} 个文件。开始处理...")

    # 使用字典按文件名（不含后缀）分组
    file_groups = defaultdict(list)

    for filename in files:
        # 获取文件名（不含扩展名）
        name_without_ext = os.path.splitext(filename)[0]
        file_groups[name_without_ext].append(filename)

    moved_count = 0
    skipped_count = 0

    for base_name, file_list in file_groups.items():
        folder_path = os.path.join(path, base_name)

        try:
            # 如果目标文件夹不存在，创建它
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"创建文件夹: '{base_name}'")

            # 移动该组中的所有文件
            for filename in file_list:
                file_path = os.path.join(path, filename)

                # 检查目标文件是否已存在
                destination_path = os.path.join(folder_path, filename)
                if os.path.exists(destination_path):
                    print(f"警告：文件 '{filename}' 在文件夹 '{base_name}' 中已存在，跳过")
                    skipped_count += 1
                    continue

                # 移动文件到目标文件夹
                shutil.move(file_path, destination_path)

                print(f"已移动：'{filename}' -> '{base_name}/{filename}'")
                moved_count += 1

        except Exception as e:
            print(f"处理文件组 '{base_name}' 时出错：{e}")
            skipped_count += len(file_list)

    print(f"\n处理完成！")
    print(f"成功移动：{moved_count} 个文件")
    print(f"跳过：{skipped_count} 个文件")
    print(f"创建/使用了 {len(file_groups)} 个文件夹")


def main():
    # 如果提供了命令行参数，使用第一个参数作为路径
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # 如果没有提供参数，询问用户输入
        path = input("请输入要处理的目录路径：")

    # 处理路径中的空格和引号
    path = path.strip('"\'')

    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    print(f"处理目录：{path}")

    # 显示将要执行的操作
    print("\n操作说明：")
    print("1. 将根据文件名（不含后缀）创建文件夹")
    print("2. 同名文件（不同后缀）将被移动到同一个文件夹中")
    print("3. 已存在的文件夹将被直接使用")
    print("4. 如果目标文件夹中已有同名文件，将跳过该文件")

    # 确认操作
    confirm = input("\n是否继续？(y/n): ").lower()
    if confirm not in ['y', 'yes', '是', '确认']:
        print("操作已取消。")
        return

    # 执行操作
    move_files_to_individual_folders(path)


if __name__ == "__main__":
    main()