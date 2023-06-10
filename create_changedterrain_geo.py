import numpy as np
import netCDF4 as nc
import xarray as xr

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

# 打开.nc文件（以读写模式）
file_path = '/home/koyomi/Downloads/geo_em.d00.nc'  # 将路径替换为你的文件路径

nc_data = xr.open_dataset(file_path)
lon = nc_data['XLONG_M'][0,:,:][0,:].data
lat = nc_data['XLAT_M'][0,:,:][:,0].data
lon_idx = np.where((lon>=116)&(lon<=119))
lat_idx = np.where((lat>=28)&(lat<=30))
# hgt[0,lat_idx[0],lon_idx[0]] = 0.
nc_data.close()

# 获取要修改的变量
dataset = nc.Dataset(file_path, 'r+')
hgt = dataset.variables['HGT_M']
# hgt[0, lat_idx[0], lon_idx[0]] = 0.

X, Y = np.meshgrid(lon, lat)
standard_parallels = (30.0, 60.0)
central_longitude = 115.0
projection = ccrs.LambertConformal(central_latitude=standard_parallels[0],
                                   central_longitude=central_longitude,
                                   standard_parallels=standard_parallels)

fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': projection})

plt.pcolormesh(X, Y, hgt[0,:,:], shading='auto', transform=ccrs.PlateCarree(), cmap='jet')

ax.gridlines(draw_labels=True, alpha=0.5)
ax.set_title('HGT_M')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.show()

# 关闭数据集，保存修改
dataset.close()
