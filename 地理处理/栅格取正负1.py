from PIL import Image
import numpy as np

# 打开影像文件
input_file = r"E:\juan_wan\处理\dsm\VARI.tif"
output_file = r"E:\juan_wan\处理\dsm\VARI_reclass.tif"
nodata_value = -9999  # 设定一个NoData值

# 读取影像数据
img = Image.open(input_file)
img_data = np.array(img)

# 将影像数据限制在-1到+1之间，其余的设为NoData值
masked_data = np.where((img_data >= -1) & (img_data <= 1), img_data, nodata_value)

# 将处理后的数据转换回图像
masked_img = Image.fromarray(masked_data.astype(np.float32))

# 保存处理后的影像
masked_img.save(output_file)
