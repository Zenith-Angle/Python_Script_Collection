# -*- coding:utf-8 -*-
'''
用于将NDVI的hdf文件转为tif
'''
import os
import arcpy
from arcpy import env

time_mon = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
for i in range(0, 12):
    # print(i)
    sourceDir = (u'F:\\MODIS_NDVI_Monthly_1km_v006\\hdf\\2010' + time_mon[i] + '\\')  # 输入
    targetDir = (u'F:\\MODIS_NDVI_Monthly_1km_v006\\tif\\2010' + time_mon[i])  # 输出

    arcpy.CheckOutExtension("Spatial")
    env.workspace = sourceDir
    arcpy.env.scratchWorkspace = sourceDir
    hdfList = arcpy.ListRasters('*', 'hdf')
    for hdf in hdfList:
        print
        hdf
        eviName = os.path.basename(hdf).replace('hdf', 'tif')
        outname = targetDir + '\\' + eviName
        print
        outname
        data1 = arcpy.ExtractSubDataset_management(hdf, outname,
                                                   "MOD_Grid_monthly_1km_VI")  # MOD_Grid_monthly_1km_VI是子数据集名称
print
'all done'
