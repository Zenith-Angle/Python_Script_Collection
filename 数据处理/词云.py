import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import re


# 定义一个函数来加载停用词
def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        stopwords = f.read().splitlines()
    return stopwords


# 定义一个函数来清理文本，移除无法识别的字符
def clean_text(text):
    # 保留中文字符、英文字母、数字和常见的标点符号
    pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9\s，。？！：；“”（）、《》…]+')
    return ''.join(pattern.findall(text))


# 定义一个函数来生成词云
def generate_wordcloud(text, stopwords, filename, output_dir):
    seg_list = jieba.cut(text, cut_all=False)  # 精确模式
    filtered_words = [word for word in seg_list if word not in stopwords]  # 过滤停用词
    seg_text = ' '.join(filtered_words)

    wc = WordCloud(font_path='simhei.ttf', background_color='white',
                   max_words=200, max_font_size=240, random_state=12,
                   width=1920, height=1080, margin=2, collocations=False)
    wc.generate(seg_text)

    # 保存词云图片
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(os.path.join(output_dir, f'{filename}.png'))  # 保存图片
    plt.close()  # 关闭图像，避免显示
    print(f'Generated wordcloud for {filename}.png')  # 打印生成信息


# 加载停用词
stopwords = load_stopwords(
    "C:\\Users\\25830\\OneDrive - oganneson\\桌面\\学习\\python学习\\python_learning\\词云\\stopword.txt")

# 设置目标文件夹和输出文件夹
input_dir = "C:\\Users\\25830\\Downloads\\景点数据分析"
output_dir = input_dir  # 可以设置为相同的目录或不同的目录

# 遍历目标文件夹中的所有txt文件
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_dir, filename)
        print(f'Processing {filename}...')  # 打印处理信息
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            cleaned_text = clean_text(text)  # 清理文本，注意变量名改变
            generate_wordcloud(cleaned_text, stopwords, filename[:-4], output_dir)
