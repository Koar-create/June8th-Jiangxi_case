import numpy as np
import netCDF4 as nc
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import os

# 打开.nc文件（以读写模式）
# file_path = '/home/koyomi/Downloads/geo_em.d00.nc'  # 将路径替换为你的文件路径
file_path = 'D:\\Repositories\\June8th-Jiangxi_case\\geo_em.d01(modified).nc'

nc_data = xr.open_dataset(file_path)
lon = nc_data['XLONG_M'][0,:,:][0,:].data
lat = nc_data['XLAT_M'][0,:,:][:,0].data
lon_idx = np.where((lon>=116)&(lon<=120))
lat_idx = np.where((lat>=28)&(lat<=31))
nc_data.close()

# 获取要修改的变量
dataset = nc.Dataset(file_path, 'r+')
hgt = dataset.variables['HGT_M']
# hgt[0, lat_idx[0], lon_idx[0]] = 0.

#####################################################检验部分####################################################
# 创建投影
X, Y = np.meshgrid(lon, lat)
standard_parallels = (30.0, 60.0)
central_longitude = 115.0
projection = ccrs.LambertConformal(central_latitude=standard_parallels[0],
                                   central_longitude=central_longitude,
                                   standard_parallels=standard_parallels)

# 创建绘图窗口和轴
fig = plt.subplots(figsize=(10, 8))

# 创建自定义图形布局
gs = gridspec.GridSpec(1, 2, width_ratios=[9.8, 0.2])  # 分为左右两列，左列宽度为9，右列宽度为1
ax = plt.subplot(gs[0], projection=projection)

# 作图
im = plt.pcolormesh(X, Y, hgt[0,:,:], vmin=0, vmax=500, shading='auto', transform=ccrs.PlateCarree(), cmap='jet')

# 绘制地图边界、海岸线和国家边界线
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.5)

# 设置标题和坐标轴标签
ax.set_title('Height', fontsize=16, fontname='Arial')
ax.set_xlabel('Longitude', fontsize=14, fontname='Consolas')
ax.set_ylabel('Latitude', fontsize=14, fontname='Consolas')

# set up x-y axis limit
ax.set_xlim(np.min(lon)-700000, np.max(lon)+750000)  # geo_em.d01
ax.set_ylim(np.min(lat)-1200000, np.max(lat)+440000)  # geo_em.d01
# ax.set_xlim(np.min(lon)-198000, np.max(lon)+408000)
# ax.set_ylim(np.min(lat)-430000, np.max(lat)+ 80000)

# 经纬网格
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5, linewidth=0.5, linestyle='--')
gl.top_labels = False
gl.bottom_labels = False
gl.right_labels = True
gl.left_labels = True
gl.xlabel_style = {'fontsize': 14, 'fontname': 'Consolas'}
gl.ylabel_style = {'fontsize': 14, 'fontname': 'Consolas'}

# 添加颜色条
cax = plt.subplot(gs[1])
cbar = plt.colorbar(im, extend='max', \
    ax=ax, orientation='vertical', cax=cax)
ticklabels = cbar.ax.get_yticklabels()          # 刻度1
c_font = {'family': 'Consolas', 'size': 14}     # 刻度2
cbar.ax.tick_params(labelsize=14)               # 刻度3
for label in ticklabels:                        # 刻度4
    label.set_fontproperties(c_font)            # 刻度5
cbar.set_label('units: m', fontdict=c_font)   # 标题1
cbar.ax.set_aspect(40)  # 调整高度和宽度的比例，此处为10

plt.show()

# plt.savefig("D:\\Desktop\\changed_terrain_d01.png", dpi=500)

# 关闭数据集，保存修改
dataset.close()
