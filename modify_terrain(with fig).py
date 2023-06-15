import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)
import os, netCDF4 as nc, xarray as xr

def add_cfeature(ax, linewidth=0.8):
    china_provinces = cfeature.NaturalEarthFeature(
        category='cultural', name='admin_1_states_provinces_lines',
        scale='50m',         facecolor='none',
        edgecolor='black',   linewidth=linewidth)
    ax.add_feature(cfeature.BORDERS, linewidth=linewidth)
    ax.add_feature(cfeature.COASTLINE, linewidth=linewidth)
    # ax.add_feature(cfeature.STATES, linewidth=linewidth)  # ruler
    ax.add_feature(china_provinces)

def add_gridlines(ax, linewidth=1, color='gray', linestyle='--', alpha=0.5, fontsize=18, fontname='Consolas'):
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, \
        linewidth=linewidth, color=color, linestyle=linestyle, alpha=alpha)
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    gl.xlabel_style = {'fontsize': fontsize, 'fontname': fontname}
    gl.ylabel_style = {'fontsize': fontsize, 'fontname': fontname}
    gl.top_labels    = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.rotate_labels = False

def add_colorbar(im, ax, cax, title='units: m', levels=np.linspace(0, 1000, 11), extend='max', orientation='vertical', labelsize=18, fontsize=26, fontname='Consolas', x_axis=0.95, y_axis=0.5):
    cbar = plt.colorbar(im, ax=ax, cax=cax, extend=extend, orientation=orientation)
    cbar.ax.tick_params(labelsize=labelsize)
    cbar.set_ticks(levels)
    if orientation == 'vertical':
        fig.text(x_axis, y_axis, title, va='center', ha='center', rotation='vertical', fontdict={'size': fontsize, 'family': fontname})  # cbar title

# basic setting
vmin, vmax = 0, 1000
levels = np.linspace(vmin, vmax, 11)
crop_box = [116, 120, 28, 31]
cmap = mpl.cm.gray_r

dim1 = 'd01'  # 'd01' or 'd02'
mode = 'modified'  # 'modified' or 'unmodified'
res  = '9-km'

# title
title       = f"{mode} terrain"
# file_path = '/home/username/Downloads/geo_em.d01(modified).nc'  # path in linux system
file_path   = f"D:\\Repositories\\June8th-Jiangxi_case"
save_path   = f"D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_terrain"

## 1. open .nc file (in read-write mode), read necessary variables  ##
dataset = nc.Dataset(os.path.join(file_path, f"geo_em.{dim1}.{mode}_{res}.nc"), 'r+')
lon = dataset.variables['XLONG_M'][0, 0, :].data
lat = dataset.variables['XLAT_M'][ 0, :, 0].data
hgt = dataset.variables['HGT_M']
lon_idx = np.where((lon>=crop_box[0])&(lon<=crop_box[1]))
lat_idx = np.where((lat>=crop_box[2])&(lat<=crop_box[3]))
# hgt[0, lon_idx[0], lat_idx[0]] = 0.
''''''''''''''''''''''''''' ↓ test part ↓ '''''''''''''''''''''''''''

## 2. paint figure ##
# create figure and axes
LON, LAT = np.meshgrid(lon, lat)
central_latitude = 26 if dim1 == 'd01' else 28.4
fig = plt.figure(figsize=(10, 8))
ax  = plt.axes(projection=ccrs.LambertConformal(central_longitude=116, central_latitude=central_latitude, standard_parallels=(30.0, 60.0)))
# restrict x-y axis
box = [np.min(LON)+1.41, np.max(LON)-1.51, np.min(LAT)+0.10, np.max(LAT)-0.21] if dim1 == 'd01' else \
      [np.min(LON)+0.12, np.max(LON)-0.20, np.min(LAT)+0.00, np.max(LAT)-0.10]
ax.set_extent(box, crs=ccrs.PlateCarree())
# add borders, coastlines, and states
add_cfeature(ax, linewidth=0.8)
# add grid
add_gridlines(ax, linewidth=1, color='gray', linestyle='--', alpha=0.5, fontsize=18, fontname='Consolas')
# im
im = ax.contourf(LON, LAT, hgt[0, :, :].data, extend='max', levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
# add colorbar
cax = fig.add_axes([0.83,0.12,0.03,0.75]) if dim1 == 'd01' else \
      fig.add_axes([0.83,0.15,0.03,0.71])
add_colorbar(im, ax, cax, title='units: m', levels=levels, extend='max', orientation='vertical', labelsize=18, fontsize=26, fontname='Consolas', x_axis=0.95, y_axis=0.5)
# set up title
ax.set_title(title, fontdict={'size': 28, 'family': 'Arial', 'weight': 'bold'})
# plt.show()  # don't show.
# adjust axes position
plt.subplots_adjust(right=0.79)

## 3. save picfure ##
if os.path.exists(save_path):
    print(f"directory '{save_path}' already exists.")
else:
    os.makedirs(save_path)
    print(f"Successfully create directory '{save_path}'!")
plt.savefig(os.path.join(save_path, f"{mode}-terrain_{res}_{dim1}.png"), dpi=300)

## 4. ending ##
plt.close(fig)
print("DONE.")
dataset.close()
