import pandas as pd
import os


def save_grouped_data(excel_path, m_column_index, e_column_index, output_folder, sheet_name):
    # 确保输出文件夹存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 读取Excel文件，指定工作表名称
    df = pd.read_excel(excel_path, sheet_name='点重分类', header=0)

    # 打印列名和列数来验证文件内容
    print("列数:", len(df.columns))
    print("列名:", df.columns.tolist())

    # 使用列索引获取列名
    m_column_name = df.columns[m_column_index]
    e_column_name = df.columns[e_column_index]

    # 按第M列的内容分组
    grouped = df.groupby(m_column_name)

    # 遍历每个分组
    for name, group in grouped:
        # 获取第E列的内容，并使用换行符连接
        content = '\n'.join(group[e_column_name].astype(str))

        # 构建输出文件路径
        output_path = os.path.join(output_folder, f"{name}.txt")

        # 保存为TXT文件，文件名为分组名
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)


# 示例用法
save_grouped_data(r"C:\Users\25830\Downloads\点重分类.xlsx", 12, 4, r"C:\Users\25830\Downloads\景点数据分析",
                  "点重分类")
