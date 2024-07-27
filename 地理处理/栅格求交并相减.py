import rasterio
import numpy as np
from shapely.geometry import box
import fiona
from fiona.crs import from_epsg
import rasterio.mask
from rasterio.warp import reproject, Resampling


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


def save_intersection_shapefile(bbox, crs, output_path):
    """保存交集边界为Shapefile"""
    schema = {
        'geometry': 'Polygon',
        'properties': {}
    }

    with fiona.open(output_path, 'w', 'ESRI Shapefile', schema=schema,
                    crs=from_epsg(crs.to_epsg())) as c:
        c.write({
            'geometry': box(*bbox).__geo_interface__,
            'properties': {}
        })


def main():
    tiff1_path = r"E:\juan_wan\21正射\3_dsm_ortho\1_dsm\21正射_dsm.tif"
    tiff2_path = r"E:\juan_wan\jw22正射\3_dsm_ortho\1_dsm\jw22_dsm.tif"
    intersection_shapefile = r"E:\juan_wan\处理\dsm\交集.shp"
    output_path = r"E:\juan_wan\处理\dsm\21reduce22.tif"

    # 读取两个TIFF文件
    data1, transform1, crs1, profile1 = read_tiff(tiff1_path)
    data2, transform2, crs2, profile2 = read_tiff(tiff2_path)

    # 计算两个TIFF文件的边界范围
    bounds1 = rasterio.transform.array_bounds(data1.shape[0], data1.shape[1], transform1)
    bounds2 = rasterio.transform.array_bounds(data2.shape[0], data2.shape[1], transform2)

    # 计算交集范围
    intersection_bounds = (
        max(bounds1[0], bounds2[0]),
        max(bounds1[1], bounds2[1]),
        min(bounds1[2], bounds2[2]),
        min(bounds1[3], bounds2[3])
    )

    # 保存交集范围为Shapefile
    save_intersection_shapefile(intersection_bounds, crs1, intersection_shapefile)
    print(f"Intersection shapefile saved to {intersection_shapefile}")

    # 读取交集范围形状
    with fiona.open(intersection_shapefile, 'r') as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]

    # 使用交集范围裁剪第一个TIFF文件
    with rasterio.open(tiff1_path) as src1:
        out_image1, out_transform1 = rasterio.mask.mask(src1, shapes, crop=True)
        out_meta1 = src1.meta.copy()

    # 使用交集范围裁剪第二个TIFF文件
    with rasterio.open(tiff2_path) as src2:
        out_image2, out_transform2 = rasterio.mask.mask(src2, shapes, crop=True)
        out_meta2 = src2.meta.copy()

    # 确保裁剪后的TIFF文件具有相同的维度，如果不同则对第二个栅格文件进行重新投影和重新采样
    if out_image1.shape != out_image2.shape:
        new_data2 = np.empty_like(out_image1)
        reproject(
            source=out_image2,
            destination=new_data2,
            src_transform=out_transform2,
            src_crs=out_meta2['crs'],
            dst_transform=out_transform1,
            dst_crs=out_meta1['crs'],
            resampling=Resampling.bilinear
        )
        out_image2 = new_data2

    # 计算两个栅格文件的差值，并处理异常值
    diff_data = np.nan_to_num(out_image1[0]) - np.nan_to_num(out_image2[0])

    # 保留-100到+100之间的值，其余值设为NaN
    diff_data[(diff_data < -100) | (diff_data > 100)] = np.nan

    # 设置任何NaN值为0
    diff_data[np.isnan(diff_data)] = 0

    # 更新元数据
    out_meta1.update({
        "driver": "GTiff",
        "height": diff_data.shape[0],
        "width": diff_data.shape[1],
        "transform": out_transform1
    })

    # 将结果保存为新的TIFF文件
    with rasterio.open(output_path, 'w', **out_meta1) as dst:
        dst.write(diff_data, 1)

    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
