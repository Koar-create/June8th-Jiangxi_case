import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset

# 读取.nc文件
nc_file = r'D:\Repositories\wrfout (no scheme, 2 domains) (fnl)\wrfout_d01_2016-06-16_00%3A00%3A00'
nc_data = Dataset(nc_file, 'r')

# 读取经度、纬度和变量数据
lon = nc_data.variables['XLONG'][0, :, :]
lat = nc_data.variables['XLAT'][0, :, :]
rainc = nc_data.variables['RAINC'][0, :, :]

# 输出维度数据
print("lon shape:", lon.shape)
print("lat shape:", lat.shape)
print("rainc shape:", rainc.shape)

# 字体设置和colormap设置
cmap = 'jet'
xtick_font = {'fontname': 'Consolas', 'fontsize': 12}
ytick_font = {'fontname': 'Consolas', 'fontsize': 12}
xlabel_font = {'family': 'Consolas', 'size': 14}
ylabel_font = {'family': 'Consolas', 'size': 14}
title_font = {'family': 'Arial', 'size': 14}
cbar_font = {'family': 'Consolas', 'size': 12}

# 创建地图投影
proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))

# 创建绘图窗口和轴
fig = plt.subplots(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, projection=proj)

# 绘制地图边界、海岸线和国家边界线
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.5)

# 绘制经纬网格
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5, linewidth=0.5, linestyle='--')
gl.xlabels_top = False
gl.ylabels_right = False
gl.xlabel_style = xtick_font
gl.ylabel_style = ytick_font

# 绘制数据
im = ax.pcolormesh(lon, lat, rainc, cmap=cmap, transform=ccrs.PlateCarree())

# 添加颜色条
cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05)
cbar.ax.tick_params(labelsize=12)
cbar.set_label('units: mm', fontdict=cbar_font)

# 设置标题和坐标轴标签
ax.set_title('accumulated total cumulus precipitation', fontdict=title_font)
ax.set_xlabel('Longitude', fontdict=xlabel_font)
ax.set_ylabel('Latitude', fontdict=ylabel_font)

# 设置x-y刻度大小
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# 设置图像范围
ax.set_xlim(lon.min(), lon.max())
ax.set_ylim(lat.min(), lat.max())

# 显示图像
plt.show()

# 关闭.nc文件
nc_data.close()