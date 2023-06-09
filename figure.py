import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

file_path = os.path.join(os.getcwd(), 'Repositories/June8th-Jiangxi_case/wrfout/wrfout_d01_2016-06-16_00:00:00')
dataset = nc.Dataset(file_path)

lon = dataset.variables['XLONG'][0, :, :]
lat = dataset.variables['XLAT'][0, :, :]
variable = dataset.variables['HGT'][0, :, :]


dataset.close()

# 计算经度和纬度的单元格边缘
lon_edges = np.linspace(lon[0, 0], lon[-1, -1], lon.shape[1] + 1)
lat_edges = np.linspace(lat[0, 0], lat[-1, -1], lat.shape[0] + 1)

X, Y = np.meshgrid(lon_edges, lat_edges)

standard_parallels = (30.0, 60.0)
central_longitude = 115.0
projection = ccrs.LambertConformal(central_latitude=standard_parallels[0],
                                   central_longitude=central_longitude,
                                   standard_parallels=standard_parallels)

fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': projection})

plt.pcolormesh(X, Y, variable, shading='auto', transform=ccrs.PlateCarree(), cmap='jet')

ax.gridlines(draw_labels=True, alpha=0.5)
ax.set_title('HGT_M')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.show()
