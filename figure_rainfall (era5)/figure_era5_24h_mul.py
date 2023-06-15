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
from obtain_tp_in_24h import obtain_tp_in_24h
from add_figure       import add_cfeature, add_gridlines, add_colorbar
from obtain_timestr   import obtain_era5_timestr

## 0.3 function
# no function.

## 0.4 basic settings
vmin_color, vmax_color = 0, 150
levels_color = np.linspace(vmin_color, vmax_color, 11)
norm = mpl.colors.Normalize(vmin=vmin_color, vmax=vmax_color)
cmap_color = mpl.cm.jet

## 0.5 dim
dim1 = 'd01'       # 'd01'      or 'd02'
dim2 = ''          # ''         or 'nan, '
# dim3 = ''          # ''         or 'rainc'    or 'rainnc'
# dim4 = 'scheme 1'  # 'scheme 1' or 'scheme 2' or 'scheme 3'
dim5 = '0.1 mm'    # '0.1 mm'   or '10 mm'    or '25 mm'    or '50 mm' or '100 mm' or '250 mm'
# dim6 = 'modified'  # ''         or 'modified'

## 0.6
# string
title     = f"observation records (from ERA-5)\ntotal precipitation in\npast 24 hours"
file_path = f'D:\\Repositories\\adaptor\\adaptor.land_hourly_rain.nc'
save_path = f"D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_era5\\{dim2 + dim1}"
timestr_UTC_list = obtain_era5_timestr(file_path)
timestr_BJT_list = [date.strftime('%Y-%m-%d %H:%M:%S') for date in [datetime.strptime(i, '%Y-%m-%d %H:%M:%S')+timedelta(hours=8) for i in timestr_UTC_list]]
## other
central_latitude = 26           if dim1 == 'd01' else 28.4
cax_box = [0.83,0.12,0.03,0.75] if dim1 == 'd01' else \
          [0.83,0.15,0.03,0.71]


## 1. read .nc file
dataset = Dataset(file_path, 'r')
lon, lat, tp = dataset["lon"][:].data, dataset["lat"][:].data, dataset["tp" ][:].data
LON, LAT = np.meshgrid(lon, lat)
dataset.close()

## 2. process data: calculate total rainfall in past 24 hours.
tp = obtain_tp_in_24h(tp, skipnum=24) * 1000
XX = tp.copy()
threshold = float(dim5.split(' ')[0])
XX = np.where(XX < threshold, np.nan, XX) if dim2 == 'nan, ' else XX
# print their shapes
print("lon shape:",   lon.shape)
print("lat shape:",   lat.shape)
print("tp shape:",     tp.shape)

box = [105.2, 125.8, 18.6, 35.3] if dim1 == 'd01' else \
      [112.8, 119.4, 26.1, 30.8]
xaxis_UTC, yaxis_UTC = 0.82, 0.92
xaxis_BJT, yaxis_BJT = 0.82, 0.88
for i in range(0, tp.shape[0]):
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
    im = ax.pcolormesh(lon, lat, XX[i, :, :], cmap=cmap_color, norm=norm, alpha=1, transform=ccrs.PlateCarree())

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
    plt.savefig(os.path.join(save_path, 'tp_'+timestr_UTC_list[i][:13]+'.png'), dpi=300)
    plt.close(fig), print(f"{timestr_UTC_list[i]} DONE.")