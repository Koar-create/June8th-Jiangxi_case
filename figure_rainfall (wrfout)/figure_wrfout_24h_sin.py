import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)
from netCDF4 import Dataset
import os, shapely.geometry as sgeom

def get_rain24(dirname, mode='rain'):
    nc_files = []
    for day in [16, 17, 18, 19, 20]:
        for hour in ['00', '03', '06', '09', '12', '15', '18', '21']:
            if (day == 20) & (hour == '21'):
                continue
            nc_files.append(dirname+'2016-06-'+str(day)+'_'+hour+'%3A00%3A00')

    for idx, nc_file in enumerate(nc_files):
        nc_data = Dataset(nc_file, 'r')
        rainc, rainnc = nc_data.variables['RAINC'][:].data, nc_data.variables['RAINNC'][:].data
        if mode == 'rainc':
            rain_temp = rainc
        elif mode == 'rainnc':
            rain_temp = rainnc
        elif mode == 'rain':
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
            rain24 = rain_temp if t[idx] == 24 else \
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

china_provinces = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_1_states_provinces_lines',
    scale='50m',         facecolor='none',
    edgecolor='black',   linewidth=0.5)
norm = mpl.colors.Normalize(vmin=0, vmax=150)
cmap = mpl.cm.jet

dim1 = 'd02'  # or 'd02'
dim2 = ''  # or 'nan, '
dim3 = 'rain'  # or 'rainc', 'rainnc'

# 读取.nc文件, 读取Latitude, Longitude和变量数据
nc_file_path = 'D:\\Repositories\\wrfout (scheme 1, 2 domains, modified terrain)\\wrfout_' + dim1
nc_data = Dataset(nc_file_path + '_2016-06-17_00%3A00%3A00', 'r')
lon = nc_data.variables['XLONG'][0, :, :]
lat = nc_data.variables['XLAT'][ 0, :, :]
hgt = nc_data.variables['HGT'][  0, :, :]

# 计算24小时累计降水
rain24 = get_rain24(nc_file_path + '_', mode=dim3)  # dim3

# 输出维度数据
print("lon shape:",       lon.shape)
print("lat shape:",       lat.shape)
print("rain24 shape:", rain24.shape)

# title
title = 'Scheme 1 (modified terrain)\ntotal precipitation in past 24 hours\n2016-06-17 00:00:00 UTC'

# create map projection
proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))

# create figure and axes
fig = plt.figure(figsize=(10, 8))
ax  = plt.axes(projection=proj)

# paint borders, coastlines and states
if   dim1 == 'd01':
    ax.set_extent([np.min(lon)+2, np.max(lon)-2, np.min(lat)+1, np.max(lat)-1], crs=ccrs.PlateCarree())
elif dim1 == 'd02':
    ax.set_extent([np.min(lon)+0.12, np.max(lon)-0.2, np.min(lat)+0, np.max(lat)-0.1], crs=ccrs.PlateCarree()) 
ax.add_feature(cfeature.BORDERS, linewidth=0.8)
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
# ax.add_feature(cfeature.STATES, linewidth=0.5)  # ruler
ax.add_feature(china_provinces)

# paint zonal and meridian grid
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, \
    linewidth=1, color='gray', linestyle='--', alpha=0.5)
set_lambert_ticks(ax, ax.get_xticks(), ax.get_yticks())
gl.xlabel_style = {'fontsize': 18, 'fontname': 'Consolas'}
gl.ylabel_style = {'fontsize': 18, 'fontname': 'Consolas'}
gl.top_labels    = False
gl.rotate_labels = False
# gl.bottom_labels = False
# gl.left_labels = True
# gl.right_labels = True

# figure
XX = rain24[0, :, :].copy()
if dim2 == 'nan, ':
    XX[np.where(XX < 0.1)] = np.nan
ax.contourf(lon, lat, hgt, cmap='gray_r', transform=ccrs.PlateCarree(), \
                  extend='max', levels=[float(i) for i in range(0,1000,100)])
im = ax.pcolormesh(lon, lat, XX, cmap=cmap, norm=norm, alpha=0.8, transform=ccrs.PlateCarree())

# add colorbar
cax = fig.add_axes([0.83,0.12,0.03,0.75]) if dim1 == 'd01' else \
    fig.add_axes([0.83,0.15,0.03,0.71])
cbar = plt.colorbar(im, extend='max', \
    ax=ax, orientation='vertical', cax=cax)
cbar.ax.tick_params(labelsize=18)
cbar.set_ticks(np.linspace(0, 150, 11))
fig.text(0.95, 0.5, 'units: mm', va='center', ha='center', rotation='vertical', \
    fontdict={'size': 28, 'family': 'Consolas'})

# set up title
ax.set_title(title, fontdict={'size': 20, 'family': 'Arial', 'weight': 'bold'})

plt.subplots_adjust(right=0.74)

# plt.show()

plt.savefig('D:\\Desktop\\test.png', dpi=300)
# crop_image("D:\\Desktop\\Figure_1.png", 0.75)

plt.close(fig)