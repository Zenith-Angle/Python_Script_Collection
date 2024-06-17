import jieba
import json
import os
import re  # 引入正则表达式库


def clean_text(text):
    # 仅保留中文字符、英文字母和数字
    pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9]+')
    return ''.join(pattern.findall(text))


def process_text_file(input_txt):
    """
    处理单个文本文件，进行分词和词频统计，只保留出现次数不少于5次的词。
    :param input_txt: str, 输入的文本文件路径
    :return: list, 包含每个词及其词频的字典列表
    """
    with open(input_txt, 'r', encoding='utf-8') as file:
        text = file.read()

    cleaned_text = clean_text(text)
    words = jieba.cut(cleaned_text, cut_all=False)
    word_count = {}
    for word in words:
        if word.strip():  # 过滤空白字符
            word_count[word] = word_count.get(word, 0) + 1

    # 只保留出现次数不少于5次的词
    filtered_word_count = {word: count for word, count in word_count.items() if
                           count >= 5}
    return [{'name': word, 'value': count} for word, count in filtered_word_count.items()]


def generate_wordcloud_data(directory):
    """
    处理指定文件夹下所有txt文件，输出到相同文件夹的对应json文件。
    :param directory: str, 文件夹路径
    """
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            input_txt = os.path.join(directory, filename)
            result = process_text_file(input_txt)
            base_name = os.path.splitext(filename)[0]
            output_json = os.path.join(directory, f"{base_name}wb.json")
            with open(output_json, 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)
            print(f"Data has been written to {output_json}")


# 示例调用，替换 'path/to/your_directory' 为您的文件夹路径
generate_wordcloud_data(r"D:\开发竞赛\数据\景点数据\景点数据分析\景点wb数据")
