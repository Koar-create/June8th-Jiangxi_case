import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)
from netCDF4 import Dataset
import xarray as xr
from datetime import datetime, timedelta
import os, shapely.geometry as sgeom

def obtain_tp24h(tp):
    for i in range(0, 5):
        tp[ (1+24*i):(25+24*i), :, :] += tp[ 24*i, :, :]
    tp = tp[24:, :, :] - tp[:-24, :, :]
    return tp

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"successfully create directory '{folder_path}'. ")
    else:
        print(f"directory '{folder_path}' already exists.")

china_provinces = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_1_states_provinces_lines',
    scale='50m',         facecolor='none',
    edgecolor='black',   linewidth=0.8)
vmin, vmax = 0, 150
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
levels = np.linspace(vmin, vmax, 6)
cmap = mpl.cm.jet

dim1 = 'd01'  # or 'd02'
dim2 = 'nan, '  # or 'nan, '

# read .nc file
nc_file_path = 'D:\\Repositories\\adaptor\\adaptor.land_hourly_rain.nc'
nc_data = xr.open_dataset(nc_file_path)

# read LON, LAT, tp
year, month = nc_data["time"].dt.year.data, nc_data["time"].dt.month.data
day , hour  = nc_data["time"].dt.day.data , nc_data["time"].dt.hour.data
lon = nc_data["lon"].data
lat = nc_data["lat"].data
tp  = nc_data["tp" ].data

tp  = obtain_tp24h(tp)
year, month = year[24:], month[24:]
day , hour  =  day[24:],  hour[24:]

# print their shapes
print("time shape:", year.shape)
print("lon shape:",   lon.shape)
print("lat shape:",   lat.shape)
print("tp shape:",     tp.shape)

# title
title = 'observation records (from ERA-5)\ntotal precipitation in\npast 24 hours'
save_path = os.path.join('D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_era5', dim2 + dim1)

for i in range(0, year.shape[0]):
    
    # time string
    date_UTC = datetime(year[i], month[i], day[i], hour[i], 0, 0)
    date_BJT = date_UTC + timedelta(hours=8)
    timestr_UTC = f"{date_UTC.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    timestr_BJT = f"{date_BJT.strftime('%Y-%m-%d %H:%M:%S')} BJT"

    # create map projection
    proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))
    # proj = ccrs.PlateCarree(central_longitude=115.5)

    # create figure and axes
    fig = plt.figure(figsize=(10, 8))
    ax  = plt.axes(projection=proj)

    # paint borders, coastlines and states
    if   dim1 == 'd01':
        ax.set_extent([105.2, 125.8, 18.6, 35.3], crs=ccrs.PlateCarree())
    elif dim1 == 'd02':
        ax.set_extent([112.8, 119.4, 26.1, 30.8], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.BORDERS, linewidth=0.8)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    # ax.add_feature(cfeature.STATES, linewidth=0.8)  # ruler
    ax.add_feature(china_provinces)
    
    # paint zonal and meridian grid
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, \
        linewidth=1, color='gray', linestyle='--', alpha=0.5)
    gl.xformatter = LongitudeFormatter()
    gl.yformatter =  LatitudeFormatter()
    gl.xlabel_style  = {'fontsize': 18, 'fontname': 'Consolas'}
    gl.ylabel_style  = {'fontsize': 18, 'fontname': 'Consolas'}
    gl.top_labels    = False
    gl.bottom_labels = True
    gl.rotate_labels = False
    gl.left_labels = True
    gl.right_labels = False
    
    # figure
    XX = tp[i, :, :].copy() * 1000
    if dim2 == 'nan, ':
        XX[np.where(XX < 0.1)] = np.nan
    im = ax.pcolormesh(lon, lat, XX, cmap=cmap, norm=norm, alpha=1, transform=ccrs.PlateCarree())

    # add colorbar
    cax = fig.add_axes([0.83,0.14,0.03,0.69]) if dim1 == 'd01' else \
        fig.add_axes([0.83,0.15,0.03,0.69])
    cbar = plt.colorbar(im, extend='max', \
        ax=ax, orientation='vertical', cax=cax)
    cbar.ax.tick_params(labelsize=18)
    cbar.set_ticks(levels)
    fig.text(0.95, 0.5, 'units: mm', va='center', ha='center', rotation='vertical', \
        fontdict={'size': 28, 'family': 'Consolas'})

    # put on title
    fig.text(0.5, 0.87, title, fontdict={'size': 24, 'family': 'Arial', 'weight': 'bold', 'ha': 'center'})

    # put on time string
    fig.text(0.71, 0.90, timestr_UTC, fontdict={'size': 16, 'family': 'Consolas', 'weight': 'normal'})
    fig.text(0.71, 0.86, timestr_BJT, fontdict={'size': 16, 'family': 'Consolas', 'weight': 'normal'})

    plt.subplots_adjust(right=0.79)

    # plt.show()

    if i == 0:
        create_folder(save_path)
    plt.savefig(os.path.join(save_path, f"tp_{timestr_UTC[:-10]}.png"), dpi=300)

    plt.close(fig)