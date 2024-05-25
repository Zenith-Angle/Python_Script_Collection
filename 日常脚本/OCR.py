import pytesseract
from PIL import Image
import cv2

# 确保将'TESSERACT_PATH'替换为您的Tesseract安装路径。
# 例如在Windows上可能是'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = 'TESSERACT_PATH'

# 使用PIL库读取图像
image = Image.open(r"C:\Users\25830\OneDrive - oganneson\桌面\运筹学.png")

# 使用Tesseract进行OCR处理
# psm模式6为假设图像为一个统一的文本块
# oem模式1为使用LSTM OCR引擎
custom_config = r'--oem 1 --psm 6'
text = pytesseract.image_to_string(image, config=custom_config)

# 输出识别的文本
print(text)
