import os
import glob
import numpy as np
import rasterio
from rasterio import features
import geopandas as gpd
from shapely.geometry import shape


def process_tif_files(input_folder, output_folder_value1, output_folder_edge):
    """
    处理指定文件夹中的所有TIF文件，提取值为1的像素并创建矢量边界

    参数:
        input_folder: 输入TIF文件所在的文件夹路径
        output_folder_value1: 保存提取值为1的栅格文件的文件夹路径
        output_folder_edge: 保存值为1区域矢量边界的文件夹路径
    """
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder_value1, exist_ok=True)
    os.makedirs(output_folder_edge, exist_ok=True)

    # 获取所有TIF文件路径
    tif_files = glob.glob(os.path.join(input_folder, "*.tif"))

    if not tif_files:
        print(f"在 {input_folder} 中未找到TIF文件")
        return

    print(f"找到 {len(tif_files)} 个TIF文件待处理")

    # 处理每个TIF文件
    for tif_file in tif_files:
        try:
            # 获取文件名（不含扩展名）
            base_name = os.path.basename(tif_file)
            file_name_without_ext = os.path.splitext(base_name)[0]

            # 定义输出文件路径
            output_file_value1 = os.path.join(output_folder_value1,
                                              f"{file_name_without_ext}_value1.tif")
            output_file_edge = os.path.join(output_folder_edge,
                                            f"{file_name_without_ext}_value1edge.shp")

            print(f"处理文件: {base_name}")

            # 读取栅格文件
            with rasterio.open(tif_file) as src:
                # 读取数据
                raster_data = src.read(1)  # 读取第一个波段

                # 创建掩码（值为1的区域）
                mask = (raster_data == 1)

                # 为值不等于1的区域设置为NoData
                raster_data_masked = np.where(mask, raster_data,
                                              src.nodata if src.nodata is not None else 0)

                # 保存处理后的栅格（只有值为1的区域）
                with rasterio.open(
                        output_file_value1,
                        'w',
                        driver='GTiff',
                        height=src.height,
                        width=src.width,
                        count=1,
                        dtype=raster_data.dtype,
                        crs=src.crs,
                        transform=src.transform,
                        nodata=src.nodata if src.nodata is not None else 0
                ) as dst:
                    dst.write(raster_data_masked, 1)

                # 创建矢量边界
                # 将值为1的区域转换为矢量多边形
                shapes = features.shapes(
                    raster_data,
                    mask=mask,
                    transform=src.transform
                )

                # 收集所有形状
                geometries = []
                for geom, value in shapes:
                    if value == 1:  # 只保留值为1的区域
                        geometries.append(shape(geom))

                # 创建GeoDataFrame
                if geometries:
                    gdf = gpd.GeoDataFrame({'geometry': geometries}, crs=src.crs)

                    # 保存为shapefile
                    gdf.to_file(output_file_edge)
                    print(f"已创建矢量边界: {os.path.basename(output_file_edge)}")
                else:
                    print(f"警告: 文件 {base_name} 中未找到值为1的区域")

            print(f"已保存值为1的栅格: {os.path.basename(output_file_value1)}")

        except Exception as e:
            print(f"处理文件 {tif_file} 时出错: {str(e)}")


if __name__ == "__main__":
    # 定义路径
    input_folder = r"C:\Users\25830\OneDrive - oganneson\桌面\学习\毕业论文\SCOI\OriginalSCOI"
    output_folder_value1 = r"C:\Users\25830\OneDrive - oganneson\桌面\学习\毕业论文\SCOI\SCOI=1"
    output_folder_edge = r"C:\Users\25830\OneDrive - oganneson\桌面\学习\毕业论文\SCOI\SCOI=1Edge"

    # 执行处理
    process_tif_files(input_folder, output_folder_value1, output_folder_edge)

    print("所有TIF文件处理完成！")