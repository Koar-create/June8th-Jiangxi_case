## 0.1
import numpy as np
import matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os, sys

## 0.2
sys.path.append("D:\\Repositories\\June8th-Jiangxi_case")
sys.path.append("D:\\Repositories\\June8th-Jiangxi_case\\obtain")
from obtain_rainx_in_24h import obtain_rainx_in_24h
from add_figure          import add_cfeature, add_gridlines, add_colorbar
from obtain_timestr      import obtain_wrf_timestr

## 0.3 function
# no function.

## 0.4 basic settings
vmin_color, vmax_color = 0, 150
vmin_gray , vmax_gray  = 0, 1000
levels_gray  = np.linspace(vmin_gray , vmax_gray , 11)
levels_color = np.linspace(vmin_color, vmax_color, 11)
norm = mpl.colors.Normalize(vmin=vmin_color, vmax=vmax_color)
cmap_gray  = mpl.cm.gray_r
cmap_color = mpl.cm.jet

## 0.5 dim
dim1 = 'd02'       # 'd01'      or 'd02'
dim2 = ''          # ''         or 'nan, '
dim3 = ''          # ''         or 'rainc'    or 'rainnc'
dim4 = 'scheme 1'  # 'scheme 1' or 'scheme 2' or 'scheme 3'
dim5 = '0.1 mm'    # '0.1 mm'   or '10 mm'    or '25 mm'    or '50 mm' or '100 mm' or '250 mm'
dim6 = ''          # ''         or 'modified'
res  = '9 km'      # '3 km'     or '9 km'

## 0.6
# string
var_long_name = {''      : 'total precipitation', 
                 'rainc' : 'accumulated total cumulus precipitation',
                 'rainnc': 'accumulated total grid scale precipitation'}
timestr_UTC_list = obtain_wrf_timestr(timelen=31, format='%Y-%m-%d %H:%M:%S', sday=17, shour=0)
timestr_BJT_list = obtain_wrf_timestr(timelen=31, format='%Y-%m-%d %H:%M:%S', sday=17, shour=8)
title = f"{dim4.capitalize()}"      +         f"\n{var_long_name[dim3]} in past 24 hours" if dim6 == '' else \
        f"{dim4.capitalize()} (modified terrain)\n{var_long_name[dim3]} in past 24 hours"
file_path = f"D:\\Repositories\\wrfout ({dim4}, 2 domains, {res})"       +       f"\\wrfout_{dim1}_" if dim6 == '' else \
            f"D:\\Repositories\\wrfout ({dim4}, 2 domains, {res}, modified terrain)\\wrfout_{dim1}_"
save_path = f"D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_wrfout ({dim4}, 2 domains, {res})"       +       f"\\{dim2 + dim1}" if dim6 == '' else \
            f"D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_wrfout ({dim4}, 2 domains, {res}, modified terrain)\\{dim2 + dim1}"
save_path = os.path.join(save_path, dim3.upper()) if dim3 != '' else save_path
## other
central_latitude = 26           if dim1 == 'd01' else 28.4
cax_box = [0.83,0.12,0.03,0.75] if dim1 == 'd01' else \
          [0.83,0.15,0.03,0.71]

## 1. read .nc file
dataset = Dataset(f"{file_path}2016-06-17_00%3A00%3A00", 'r')
LON, LAT, hgt = dataset.variables['XLONG'][0, :, :].data, dataset.variables['XLAT'][ 0, :, :].data, dataset.variables['HGT'][0, :, :].data
dataset.close()

## 2. process data: calculate total rainfall in past 24 hours.
rain24 = obtain_rainx_in_24h(file_path, timelen=39, timeinterval=3, mode=dim3)
XX = rain24.copy()
threshold = float(dim5.split(' ')[0])
XX = np.where(XX < threshold, np.nan, XX) if dim2 == 'nan, ' else XX
# 输出维度数据
print("LON shape:",       LON.shape)
print("lat shape:",       LAT.shape)
print("rain24 shape:", rain24.shape)

## 3.0 don't need to cycle
box = [np.min(LON)+1.92, np.max(LON)-1.82, np.min(LAT)+0.10, np.max(LAT)-0.26] if dim1 == 'd01' else \
      [np.min(LON)+0.12, np.max(LON)-0.20, np.min(LAT)+0.00, np.max(LAT)-0.10]
xaxis_UTC, yaxis_UTC = 0.82, 0.92
xaxis_BJT, yaxis_BJT = 0.82, 0.88
for i in range(0, rain24.shape[0]):

    ## 3.1 create figure and axes
    fig = plt.figure(figsize=(10, 8))
    ax  = plt.axes(projection=ccrs.LambertConformal(central_longitude=116, central_latitude=central_latitude, standard_parallels=(30.0, 60.0)))
    
    ## 3.2 add borders, coastlines, and states
    add_cfeature(ax, linewidth=0.8)

    ## 3.3 add grid
    add_gridlines(ax, linewidth=1, color='gray', linestyle='--', alpha=0.5, fontsize=18, fontname='Consolas')

    # 3.4 restrict x-y extent
    ax.set_extent(box, crs=ccrs.PlateCarree())

    ## 3.5 figure
    ax.contourf(LON, LAT, hgt, cmap=cmap_gray, transform=ccrs.PlateCarree(), extend='max', levels=levels_gray)
    im = ax.pcolormesh(LON, LAT, XX[i, :, :], cmap=cmap_color, norm=norm, alpha=0.8, transform=ccrs.PlateCarree())

    ## 3.6 add colorbar
    add_colorbar(im, ax, fig.add_axes(cax_box), fig, title='units: mm', levels=levels_color, extend='max', orientation='vertical', labelsize=18, fontsize=26, fontname='Consolas', x_axis=0.95, y_axis=0.5)
    
    ## 3.7 set up title
    ax.set_title(title, fontdict={'size': 20, 'family': 'Arial', 'weight': 'bold'})
    # put on time string
    fig.text(xaxis_UTC, yaxis_UTC, f"{timestr_UTC_list[i]} UTC", fontdict={'size': 18, 'family': 'Consolas', 'weight': 'normal', 'ha': 'center'})
    fig.text(xaxis_BJT, yaxis_BJT, f"{timestr_BJT_list[i]} BJT", fontdict={'size': 18, 'family': 'Consolas', 'weight': 'normal', 'ha': 'center'})

    ## 3.8 adjust axes position
    plt.subplots_adjust(right=0.74)
    
    ## 3.9 show, save and close
    # plt.show()
    if not os.path.exists(save_path):
        os.makedirs(save_path), print(f"Successfully create directory '{save_path}'!")
    plt.savefig(os.path.join(save_path, 'rain24h_'+timestr_UTC_list[i][:13]+'.png'), dpi=300)
    plt.close(fig), print(f"{timestr_UTC_list[i]} DONE.")