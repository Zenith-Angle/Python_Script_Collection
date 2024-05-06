import geopandas as gpd


def update_landmarks(points_shp, buffer_shp, output_shp):
    # 加载点和缓冲区的Shapefile
    points = gpd.read_file(points_shp)
    buffers = gpd.read_file(buffer_shp)

    # 确保坐标参考系统相同
    if points.crs != buffers.crs:
        points = points.to_crs(buffers.crs)

    # 使用空间连接找到每个点所在的缓冲区，使用 'predicate="within"'
    joined = gpd.sjoin(points, buffers, how='left', predicate='within')

    # 根据列的位置更新 'landmark' 字段，buffers的'name'字段是第一列（从0开始计数）
    joined['landmark'] = joined.iloc[:, len(points.columns) + 0]  # buffers的'name'字段添加到joined后成为新的列

    # 删除除了原点数据和新landmark外的其它列
    updated_points = joined[points.columns.tolist() + ['landmark']]

    # 保存更新后的点文件
    updated_points.to_file(output_shp, index=False)


    # 使用示例
update_landmarks(
    r"D:\开发竞赛\数据\景点数据\landmarks\缓冲区裁剪点.shp",
    r"D:\开发竞赛\数据\景点数据\landmarks\缓冲区.shp",
    r"D:\开发竞赛\数据\景点数据\landmarks\点重分类.shp"
)
