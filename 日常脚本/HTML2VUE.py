import os
from bs4 import BeautifulSoup


def html_to_vue(html_path, output_dir):
    # 读取 HTML 文件内容
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 创建 Vue 文件内容
    vue_content = f"<template>\n  <div>\n{soup.prettify()}\n  </div>\n</template>\n\n"
    vue_content += "<script>\nexport default {\n  name: '" + \
                   os.path.splitext(os.path.basename(html_path))[
                       0] + "'\n}\n</script>\n\n"
    vue_content += "<style scoped>\n</style>\n"

    # 写入 Vue 文件
    vue_file_path = os.path.join(output_dir,
                                 os.path.splitext(os.path.basename(html_path))[
                                     0] + '.vue')
    with open(vue_file_path, 'w', encoding='utf-8') as vue_file:
        vue_file.write(vue_content)

    print(f"Converted {html_path} to {vue_file_path}")


def convert_directory_html_to_vue(directory_path):
    # 确保输出目录存在
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # 遍历目录中的 HTML 文件
    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            html_path = os.path.join(directory_path, filename)
            html_to_vue(html_path, directory_path)


# 使用示例：将 'path_to_html_files' 目录中的 HTML 文件转换为 Vue 组件
convert_directory_html_to_vue(r"C:\Users\25830\Downloads\landmarks_details")
