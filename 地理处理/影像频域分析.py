import numpy as np
import rasterio
from scipy.fftpack import fft2, fftshift
import matplotlib.pyplot as plt
import matplotlib

# 设置matplotlib支持中文显示
matplotlib.rcParams['font.family'] = 'SimHei'  # 设置字体为黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号


# 读取影像
def read_image(file_path):
    with rasterio.open(file_path) as src:
        image = src.read(1)
        transform = src.transform
        crs = src.crs
    return image, transform, crs


# 裁剪影像
def crop_images_to_same_size(image1, image2):
    min_height = min(image1.shape[0], image2.shape[0])
    min_width = min(image1.shape[1], image2.shape[1])
    cropped_image1 = image1[:min_height, :min_width]
    cropped_image2 = image2[:min_height, :min_width]
    return cropped_image1, cropped_image2


# 频域分析
def perform_frequency_analysis(image1, image2):
    fft_image1 = fftshift(fft2(image1))
    fft_image2 = fftshift(fft2(image2))
    magnitude_image1 = np.abs(fft_image1)
    magnitude_image2 = np.abs(fft_image2)
    valid_mask = ~np.isnan(magnitude_image1) & ~np.isnan(magnitude_image2)
    correlation = np.corrcoef(magnitude_image1[valid_mask].flatten(),
                              magnitude_image2[valid_mask].flatten())[0, 1]
    return magnitude_image1, magnitude_image2, correlation


# 主函数
def main(image1_path, image2_path):
    image1, transform1, crs1 = read_image(image1_path)
    image2, transform2, crs2 = read_image(image2_path)

    # 确保两个影像具有相同的尺寸
    image1, image2 = crop_images_to_same_size(image1, image2)

    # 频域分析
    magnitude_image1, magnitude_image2, freq_corr = perform_frequency_analysis(image1,
                                                                               image2)

    # 输出相关性结果
    print(f'频域相关性: {freq_corr:.4f}')

    # 频域分析图优化
    plt.figure(figsize=(8, 6))
    plt.plot(np.arange(len(magnitude_image1.flatten())),
             np.log1p(magnitude_image1.flatten()),
             marker='o', linestyle='-', color='r', markersize=1, linewidth=0.5,
             label='频域分析结果')
    plt.title('频域分析结果')
    plt.xlabel('像素序号')
    plt.ylabel('对数幅度')
    plt.grid(True)
    plt.legend()
    plt.show()

    # 计算幅度差异，避免负值
    magnitude_diff = np.abs(magnitude_image1) - np.abs(magnitude_image2)
    magnitude_diff[magnitude_diff < 0] = 0

    # 可视化频域相关性热图，调整颜色映射和图例尺度
    plt.figure(figsize=(8, 6))
    plt.imshow(np.log1p(magnitude_diff), cmap='hot')  # 使用'hot'颜色映射
    plt.colorbar(label='对数幅度差异', ticks=[0, 5, 10, 15, 20, 25])
    plt.clim(0, 25)  # 设置颜色范围，使对比更明显
    plt.title('频域相关性')
    plt.xlabel('列索引')
    plt.ylabel('行索引')
    plt.show()


# 执行主函数
if __name__ == "__main__":
    main(r"E:\juan_wan\处理\dsm\erosion.tif", r"E:\juan_wan\处理\dsm\坡度.tif")
