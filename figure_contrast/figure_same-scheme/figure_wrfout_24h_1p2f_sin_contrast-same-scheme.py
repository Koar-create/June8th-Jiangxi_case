import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)
from netCDF4 import Dataset
import os, shapely.geometry as sgeom

def get_rain24(dirname, mode='rainc+rainnc'):
    nc_files = []
    for day in [16, 17, 18, 19, 20]:
        for hour in ['00', '03', '06', '09', '12', '15', '18', '21']:
            if (day == 20) & (hour == '21'):
                continue
            nc_files.append(dirname+'_2016-06-'+str(day)+'_'+hour+'%3A00%3A00')

    for idx, nc_file in enumerate(nc_files):
        nc_data = Dataset(nc_file, 'r')
        rainc, rainnc = nc_data.variables['RAINC'][:].data, nc_data.variables['RAINNC'][:].data
        if mode == 'rainc':
            rain_temp = rainc
        elif mode == 'rainnc':
            rain_temp = rainnc
        elif mode == 'rainc+rainnc':
            rain_temp = rainc + rainnc
        nc_data.close()
        rain = rain_temp if idx == 0 else \
            np.concatenate((rain, rain_temp), axis=0)
        rshape = rain.shape
    t = np.arange(0, 115, 3)
    rain24 = []
    for idx in range(0, 39):
        if t[idx] - 24 >= 0:
            rain_temp = rain[idx, :, :].reshape(1, rshape[1], rshape[2]) \
                - rain[idx - 8, :, :].reshape(1, rshape[1], rshape[2])
            rain24 = rain_temp if t[idx]==24 else \
                np.concatenate((rain24, rain_temp), axis=0)
    return rain24

def find_x_intersections(ax, xticks):
    '''找出xticks对应的经线与下x轴的交点在data坐标下的位置和对应的ticklabel.'''
    # 获取地图的矩形边界和最大的经纬度范围.
    x0, x1, y0, y1 = ax.get_extent()
    lon0, lon1, lat0, lat1 = ax.get_extent(ccrs.PlateCarree())
    xaxis = sgeom.LineString([(x0, y0), (x1, y0)])
    # 仅选取能落入地图范围内的ticks.
    lon_ticks = [tick for tick in xticks if tick >= lon0 and tick <= lon1]

    # 每条经线有nstep个点.
    nstep = 50
    xlocs = []
    xticklabels = []
    for tick in lon_ticks:
        lon_line = sgeom.LineString(
            ax.projection.transform_points(
                ccrs.Geodetic(),
                np.full(nstep, tick),
                np.linspace(lat0, lat1, nstep)
            )[:, :2]
        )
        # 如果经线与x轴有交点,获取其位置.
        if xaxis.intersects(lon_line):
            point = xaxis.intersection(lon_line)
            xlocs.append(point.x)
            xticklabels.append(tick)
        else:
            continue

    # 用formatter添上度数和东西标识.
    formatter = LongitudeFormatter()
    xticklabels = [formatter(label) for label in xticklabels]

    return xlocs, xticklabels

def find_y_intersections(ax, yticks):
    '''找出yticks对应的纬线与左y轴的交点在data坐标下的位置和对应的ticklabel.'''
    x0, x1, y0, y1 = ax.get_extent()
    lon0, lon1, lat0, lat1 = ax.get_extent(ccrs.PlateCarree())
    yaxis = sgeom.LineString([(x0, y0), (x0, y1)])
    lat_ticks = [tick for tick in yticks if tick >= lat0 and tick <= lat1]

    nstep = 50
    ylocs = []
    yticklabels = []
    for tick in lat_ticks:
        # 注意这里与find_x_intersections的不同.
        lat_line = sgeom.LineString(
            ax.projection.transform_points(
                ccrs.Geodetic(),
                np.linspace(lon0, lon1, nstep),
                np.full(nstep, tick)
            )[:, :2]
        )
        if yaxis.intersects(lat_line):
            point = yaxis.intersection(lat_line)
            ylocs.append(point.y)
            yticklabels.append(tick)
        else:
            continue

    formatter = LatitudeFormatter()
    yticklabels = [formatter(label) for label in yticklabels]

    return ylocs, yticklabels

def set_lambert_ticks(ax, xticks, yticks):
    # 设置x轴.
    xlocs, xticklabels = find_x_intersections(ax, xticks)
    ax.set_xticks(xlocs)
    ax.set_xticklabels(xticklabels)
    # 设置y轴.
    ylocs, yticklabels = find_y_intersections(ax, yticks)
    ax.set_yticks(ylocs)
    ax.set_yticklabels(yticklabels)

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"successfully create directory '{folder_path}'. ")
    else:
        print(f"directory '{folder_path}' already exists.")

china_provinces = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_1_states_provinces_lines',
    scale='50m',         facecolor='none',
    edgecolor='black',   linewidth=0.5)
norm = mpl.colors.Normalize(vmin=0, vmax=150)
cmap = mpl.cm.jet

dim1 = 'd01'  # or 'd02'
dim2 = ''  # or 'nan, '

# 读取.nc文件, 读取Latitude, Longitude和变量数据
nc_file = 'D:\\Repositories\\wrfout (scheme 1, 2 domains)\\wrfout_' + dim1
nc_data = Dataset(nc_file + '_2016-06-17_00%3A00%3A00', 'r')
lon = nc_data.variables['XLONG'][0, :, :]
lat = nc_data.variables['XLAT'][0, :, :]
hgt = nc_data.variables['HGT'][0, :, :]

# 计算24小时累计降水
rainc24  = get_rain24(nc_file, mode='rainc')
rainnc24 = get_rain24(nc_file, mode='rainnc')

# 输出维度数据
print("lon shape:", lon.shape)
print("lat shape:", lat.shape)
print("rain24 shape:", rainc24.shape)

# title
title = 'Scheme 1 in past 24 hours\n2016-06-17 00:00:00 UTC'
title1 = 'accumulated total\ncumulus precipitation'     # dim3
title2 = 'accumulated total\ngrid scale precipitation'  # dim3

# 创建地图投影
proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))

# 创建绘图窗口和轴
fig = plt.figure(figsize=(15, 8))
ax1 = fig.add_subplot(121, projection=proj)
ax2 = fig.add_subplot(122, projection=proj)
plt.subplots_adjust(wspace=0.3)

# 绘制地图边界、海岸线和国家边界线
if dim1 == 'd01':
    ax1.set_extent([np.min(lon)+2, np.max(lon)-2, np.min(lat)+1, np.max(lat)-1], crs=ccrs.PlateCarree())
    ax2.set_extent([np.min(lon)+2, np.max(lon)-2, np.min(lat)+1, np.max(lat)-1], crs=ccrs.PlateCarree())
elif dim2 == 'd02':
    ax1.set_extent([np.min(lon)+0.12, np.max(lon)-0.2, np.min(lat)+0, np.max(lat)-0.1], crs=ccrs.PlateCarree())
    ax2.set_extent([np.min(lon)+0.12, np.max(lon)-0.2, np.min(lat)+0, np.max(lat)-0.1], crs=ccrs.PlateCarree())
ax1.add_feature(cfeature.BORDERS, linewidth=0.5), ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)  # ax1.add_feature(cfeature.STATES, linewidth=0.5)  # ruler
ax2.add_feature(cfeature.BORDERS, linewidth=0.5), ax2.add_feature(cfeature.COASTLINE, linewidth=0.5)  # ax2.add_feature(cfeature.STATES, linewidth=0.5)  # ruler
ax1.add_feature(china_provinces),                 ax2.add_feature(china_provinces)

# 绘制经纬网格
gl1 = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, \
                    linewidth=1, color='gray', linestyle='--', alpha=0.5)
gl2 = ax2.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, \
                    linewidth=1, color='gray', linestyle='--', alpha=0.5)
set_lambert_ticks(ax1, ax1.get_xticks(), ax1.get_yticks())
set_lambert_ticks(ax2, ax2.get_xticks(), ax2.get_yticks())
gl1.xlabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
gl1.ylabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
gl1.top_labels    = False
gl1.rotate_labels = False
gl2.xlabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
gl2.ylabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
gl2.top_labels    = False
gl2.rotate_labels = False


# 绘制数据
XX1 =  rainc24[0, :, :].copy()
XX2 = rainnc24[0, :, :].copy()
if dim2 == 'nan, ':
    XX1[np.where(XX1 < 0.1)] = np.nan
    XX2[np.where(XX2 < 0.1)] = np.nan
ax1.contourf(lon, lat, hgt, cmap='gray_r', transform=ccrs.PlateCarree(), \
                  extend='max', levels=[float(i) for i in range(0,1000,100)])
ax2.contourf(lon, lat, hgt, cmap='gray_r', transform=ccrs.PlateCarree(), \
                  extend='max', levels=[float(i) for i in range(0,1000,100)])
im1 = ax1.pcolormesh(lon, lat, XX1, cmap=cmap, norm=norm, alpha=0.8, transform=ccrs.PlateCarree())
im2 = ax2.pcolormesh(lon, lat, XX2, cmap=cmap, norm=norm, alpha=0.8, transform=ccrs.PlateCarree())

# 添加颜色条
cax = fig.add_axes([0.12,0.12,0.76,0.03]) if dim1 == 'd01' else \
    fig.add_axes([0.12,0.12,0.76,0.03])
cbar = plt.colorbar(im1, extend='max', \
    ax=ax1, orientation='horizontal', cax=cax)
cbar.ax.tick_params(labelsize=20)
cbar.set_ticks(np.linspace(0, 150, 11))
fig.text(0.5, 0.02, 'units: mm', fontdict={'size': 28, 'family': 'Consolas', 'ha': 'center'})

# 设置标题和坐标轴标签
ax1.set_title(title1, fontdict={'size': 20, 'family': 'Arial', 'weight': 'bold'})
ax2.set_title(title2, fontdict={'size': 20, 'family': 'Arial', 'weight': 'bold'})
fig.text(0.5, 0.86, title, fontdict={'size': 28, 'family': 'Arial', 'weight': 'bold', 'ha': 'center'})

# plt.show()

plt.savefig('D:\\Desktop\\test.png', dpi=300)

plt.close(fig)