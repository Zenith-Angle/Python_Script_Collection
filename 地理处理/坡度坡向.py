import numpy as np
import rasterio
import rasterio.mask
import fiona
from os.path import join


def calculate_slope_aspect(dem_data, transform):
    """计算坡度和坡向"""
    x, y = np.gradient(dem_data, transform[0], -transform[4])

    slope = np.sqrt(x ** 2 + y ** 2)
    slope = np.degrees(np.arctan(slope))

    aspect = np.degrees(np.arctan2(-x, y))
    aspect = np.where(aspect < 0, 90.0 - aspect, 360.0 - aspect + 90.0)

    return slope, aspect


def read_tiff(file_path):
    """读取TIFF文件，返回数据数组、地理变换矩阵、坐标参考系统和元数据"""
    with rasterio.open(file_path) as src:
        data = src.read(1).astype(np.float32)
        transform = src.transform
        crs = src.crs
        profile = src.profile
    return data, transform, crs, profile


def write_tiff(file_path, data, transform, crs):
    """将数据写入TIFF文件"""
    with rasterio.open(
            file_path, 'w',
            driver='GTiff',
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs=crs,
            transform=transform,
            nodata=np.nan
    ) as dst:
        dst.write(data, 1)


def main():
    dem_path = r"E:\juan_wan\jw22正射\3_dsm_ortho\1_dsm\jw22_dsm.tif"
    intersection_shapefile = r"E:\juan_wan\处理\dsm\交集.shp"
    output_folder = r"E:\juan_wan\处理\dsm"

    slope_output_path = join(output_folder, "slope.tif")
    aspect_output_path = join(output_folder, "aspect.tif")

    # 读取DEM数据
    dem_data, transform, crs, profile = read_tiff(dem_path)

    # 计算坡度和坡向
    slope, aspect = calculate_slope_aspect(dem_data, transform)

    # 读取交集范围形状
    with fiona.open(intersection_shapefile, 'r') as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]

    # 使用交集范围裁剪坡度图
    with rasterio.open(dem_path) as src:
        slope_image, slope_transform = rasterio.mask.mask(src, shapes, crop=True)
        slope_image = slope_image[0]

    # 使用交集范围裁剪坡向图
    with rasterio.open(dem_path) as src:
        aspect_image, aspect_transform = rasterio.mask.mask(src, shapes, crop=True)
        aspect_image = aspect_image[0]

    # 更新坡度图元数据
    slope_meta = profile.copy()
    slope_meta.update({
        "driver": "GTiff",
        "height": slope_image.shape[0],
        "width": slope_image.shape[1],
        "transform": slope_transform
    })

    # 更新坡向图元数据
    aspect_meta = profile.copy()
    aspect_meta.update({
        "driver": "GTiff",
        "height": aspect_image.shape[0],
        "width": aspect_image.shape[1],
        "transform": aspect_transform
    })

    # 保存坡度图和坡向图
    write_tiff(slope_output_path, slope_image, slope_transform, crs)
    write_tiff(aspect_output_path, aspect_image, aspect_transform, crs)

    print(f"Slope output written to {slope_output_path}")
    print(f"Aspect output written to {aspect_output_path}")


if __name__ == "__main__":
    main()
