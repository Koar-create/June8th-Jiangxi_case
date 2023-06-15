import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os, shapely.geometry as sgeom

def get_rain24_diffscheme(dirname):
    # most concise: nc_files = [dirname+f'_2016-06-{day}_{hour:02}%3A00%3A00' for day in list(range(16,21)) for hour in [j for j in range(0,22,3)] if not (day == 20 and hour == 21)]
    start_time, end_time, delta = datetime(2016, 6, 16, 0, 0, 0), datetime(2016, 6, 20, 18, 0, 0), timedelta(hours=3)
    date_list = [start_time + i * delta for i in range((end_time - start_time) // delta + 1)]
    nc_file_list = [f"{dirname}{str(date.strftime('%Y-%m-%d_%H:%M:%S')).replace(':', '%3A')}" for date in date_list]

    for idx, nc_file in enumerate(nc_file_list):
        nc_data = Dataset(nc_file, 'r')
        rain = nc_data.variables['RAINNC'][:].data if idx == 0 else np.concatenate((rain, nc_data.variables['RAINNC'][:].data), axis=0)
        nc_data.close()
    
    rain24 = rain[8:, :, :] - rain[:-8, :, :]
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

'''''''''fundamental setup'''''''''
china_provinces = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_1_states_provinces_lines',
    scale='50m',         facecolor='none',
    edgecolor='black',   linewidth=0.8)
vmin, vmax = 0, 250
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
levels = np.linspace(vmin, vmax, 6)
cmap = mpl.cm.jet
'''''''''fundamental setup'''''''''
'''
code that need modification ↓
'''
dim1 = 'd01'    # 'd01'  or 'd02'
dim2 = ''       # ''     or 'nan, '
'''
code that need modification ↑
-----------------------------
↓ code unneeded to change
'''
# 读取.nc文件, 读取Latitude, Longitude和变量数据
nc_file1 = 'D:\\Repositories\\wrfout (scheme 1, 2 domains)\\wrfout_' + dim1 + '_'
nc_file2 = 'D:\\Repositories\\wrfout (scheme 1, 2 domains, modified terrain)\\wrfout_' + dim1 + '_'
nc_data1 = Dataset(nc_file1 + '2016-06-17_00%3A00%3A00', 'r')
nc_data2 = Dataset(nc_file2 + '2016-06-17_00%3A00%3A00', 'r')
lon = nc_data1.variables['XLONG'][0, :, :]
lat = nc_data1.variables['XLAT'][0, :, :]
hgt1 = nc_data1.variables['HGT'][0, :, :]
hgt2 = nc_data2.variables['HGT'][0, :, :]

# 计算24小时累计降水
rainnc24_1 = get_rain24_diffscheme(nc_file1)
rainnc24_2 = get_rain24_diffscheme(nc_file2)

# 输出维度数据
print("lon shape:", lon.shape)
print("lat shape:", lat.shape)
print("rain24 shape:", rainnc24_1.shape)

for i in range(0, rainnc24_1.shape[0]):
    
    # save path
    dirpath = 'D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_wrfout (scheme 1, terrain contrast)'
    subdirectory = dim1 if dim2 == '' else dim2 + dim1
    save_path = os.path.join(dirpath, subdirectory)
    
    # title
    title = 'accumulated total grid scale precipitation\n in past 24 hours'
    title1 = 'Scheme 1'
    title2 = 'Scheme 1 (modified terrain)'
    
    #time string
    delta = timedelta(hours=3)
    date_UTC = datetime(2016, 6, 17, 0, 0, 0) + delta * i
    date_BJT = date_UTC + timedelta(hours=8)
    timestr_UTC = f"{date_UTC.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    timestr_BJT = f"{date_BJT.strftime('%Y-%m-%d %H:%M:%S')} BJT"
    
    # 创建地图投影
    proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))
    
    # 创建绘图窗口和轴
    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_subplot(121, projection=proj)
    ax2 = fig.add_subplot(122, projection=proj)
    plt.subplots_adjust(wspace=0.4)
    
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
    # set_lambert_ticks(ax1, ax1.get_xticks(), ax1.get_yticks())
    # set_lambert_ticks(ax2, ax2.get_xticks(), ax2.get_yticks())
    gl1.xformatter = LongitudeFormatter()
    gl1.yformatter =  LatitudeFormatter()
    gl2.xformatter = LongitudeFormatter()
    gl2.yformatter =  LatitudeFormatter()
    gl1.xlabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
    gl1.ylabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
    gl1.top_labels    = False
    gl1.rotate_labels = False
    gl2.xlabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
    gl2.ylabel_style  = {'fontsize': 16, 'fontname': 'Consolas'}
    gl2.top_labels    = False
    gl2.rotate_labels = False

    # 绘制数据
    XX1 = rainnc24_1[i, :, :].copy()
    XX2 = rainnc24_2[i, :, :].copy()
    if dim2 == 'nan, ':
        XX1[np.where(XX1 < 0.1)] = np.nan
        XX2[np.where(XX2 < 0.1)] = np.nan
    ax1.contourf(lon, lat, hgt1, cmap='gray_r', transform=ccrs.PlateCarree(), \
                    extend='max', levels=[float(i) for i in range(0,1000,100)])
    ax2.contourf(lon, lat, hgt2, cmap='gray_r', transform=ccrs.PlateCarree(), \
                    extend='max', levels=[float(i) for i in range(0,1000,100)])
    # im1 = ax1.pcolormesh(lon, lat, XX1, cmap=cmap, norm=norm, alpha=0.8, transform=ccrs.PlateCarree())
    # im2 = ax2.pcolormesh(lon, lat, XX2, cmap=cmap, norm=norm, alpha=0.8, transform=ccrs.PlateCarree())
    im1 = ax1.contourf(lon, lat, XX1, cmap=cmap, extend='max', levels=levels, alpha=0.8, transform=ccrs.PlateCarree())
    im2 = ax2.contourf(lon, lat, XX2, cmap=cmap, extend='max', levels=levels, alpha=0.8, transform=ccrs.PlateCarree())
    im3 = ax1.contour(im1, colors='k', levels=levels, alpha=0.8, linewidths=0.3, transform=ccrs.PlateCarree())
    im4 = ax2.contour(im2, colors='k', levels=levels, alpha=0.8, linewidths=0.2, transform=ccrs.PlateCarree())
    # ax1.clabel(im3, fmt='%.0f', fontsize=12)
    # ax2.clabel(im4, fmt='%.0f', fontsize=12)
    
    # 添加颜色条
    cax = fig.add_axes([0.12,0.20,0.81,0.03]) if dim1 == 'd01' else \
        fig.add_axes([0.12,0.20,0.81,0.03])
    cbar = plt.colorbar(im1, extend='max', \
        ax=ax1, orientation='horizontal', cax=cax)
    cbar.ax.tick_params(labelsize=20)
    cbar.set_ticks(levels)
    fig.text(0.5, 0.08, 'units: mm', fontdict={'size': 28, 'family': 'Consolas', 'ha': 'center'})

    # 设置标题和坐标轴标签
    ax1.set_title(title1, fontdict={'size': 22, 'family': 'Arial', 'weight': 'bold'})
    ax2.set_title(title2, fontdict={'size': 22, 'family': 'Arial', 'weight': 'bold'})
    fig.text(0.5, 0.86, title, fontdict={'size': 28, 'family': 'Arial', 'weight': 'bold', 'ha': 'center'})

    # put on time string
    fig.text(0.21, 0.80, timestr_UTC, fontdict={'size': 18, 'family': 'Consolas', 'weight': 'normal', 'ha': 'center'})
    fig.text(0.21, 0.76, timestr_BJT, fontdict={'size': 18, 'family': 'Consolas', 'weight': 'normal', 'ha': 'center'})
    
    # plt.show()
    
    if i == 0:
        create_folder(save_path)
    plt.savefig(os.path.join(save_path, 'rain24h_'+timestr_UTC[:-10]+'.png'), dpi=300)
    
    plt.close(fig)