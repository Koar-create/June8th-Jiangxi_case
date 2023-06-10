import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset

# 读取.nc文件
nc_file = r'D:\Repositories\wrfout (no scheme, 2 domains) (fnl)\wrfout_d01_2016-06-16_03%3A00%3A00'
nc_data = Dataset(nc_file, 'r')

# 读取经度、纬度和变量数据
lon = nc_data.variables['XLONG'][0, :, :]
lat = nc_data.variables['XLAT'][0, :, :]
rainc = nc_data.variables['RAINC'][0, :, :]
rainnc = nc_data.variables['RAINNC'][0, :, :]
rain = rainc + rainnc

# 输出维度数据
print("lon shape:", lon.shape)
print("lat shape:", lat.shape)
print("rain shape:", rain.shape)

# Create time string
date = nc_file.split("_")[-2]
hour = nc_file.split("%3A")[-3][-2:]
timestr = date + ' ' + hour + ':00:00 UTC'

# 创建地图投影
proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))
# proj = ccrs.PlateCarree(central_longitude=115.5)

# 创建绘图窗口和轴
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection=proj))





# 绘制地图边界、海岸线和国家边界线
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.5)

# 绘制经纬网格
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5, linewidth=0.5, linestyle='--')
gl.xlabels_top = False
gl.xlabels_bottom = False
gl.ylabels_left = True
gl.ylabels_right = True
# gl.xlabel_style = {'fontsize': 14, 'fontname': 'Consolas'}
gl.ylabel_style = {'fontsize': 14, 'fontname': 'Consolas'}

# 绘制数据
im = ax.pcolormesh(lon, lat, rain, cmap='jet', transform=ccrs.PlateCarree())

# 添加颜色条
cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05)
cbar.ax.tick_params(labelsize=12)
cbar.set_label('units: mm', fontsize=12, fontname='Consolas')

# 设置标题和坐标轴标签
ax.set_title('without scheme, accumulated total cumulus precipitation '+timestr, fontsize=14, fontname='Arial')
ax.set_xlabel('Longitude', fontsize=14, fontname='Consolas')
ax.set_ylabel('Latitude', fontsize=14, fontname='Consolas')

plt.show()