## 0.1
import numpy as np
import matplotlib as mpl, matplotlib.pyplot as plt
import cartopy.crs as ccrs
from netCDF4 import Dataset
import os, sys

## 0.2
sys.path.append("D:\\Repositories\\June8th-Jiangxi_case")
sys.path.append("D:\\Repositories\\June8th-Jiangxi_case\\obtain")
from add_figure import add_cfeature, add_gridlines, add_colorbar

## 0.3 function
# no function

## 0.4 basic settings
vmin, vmax = 0, 1000
levels = np.linspace(vmin, vmax, 11)
crop_box = [116, 120, 28, 31]
cmap = mpl.cm.gray_r

## 0.5 dim
dim1 = 'd01'  # 'd01' or 'd02'
mode = 'modified'  # 'modified' or 'unmodified'
res  = '9-km'

## 0.6
# string
title       = f"{mode} terrain"
file_path   = f"D:\\Repositories\\June8th-Jiangxi_case\\geo_em.d0"  # or '/home/username/Downloads/geo_em.d01(modified).nc'  # path in linux system
save_path   = f"D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_terrain"
# other
central_latitude = 26 if dim1 == 'd01' else 28.4
cax_box = [0.83,0.12,0.03,0.75] if dim1 == 'd01' else \
          [0.83,0.15,0.03,0.71]

## 1. & 2. open .nc file (in read-write mode), read necessary variables  ##
dataset = Dataset(os.path.join(file_path, f"geo_em.{dim1}.{mode}_{res}.nc"), 'r+')
lon,     lat, hgt = dataset.variables['XLONG_M'][0, 0, :].data, dataset.variables['XLAT_M'][0, :, 0].data, dataset.variables['HGT_M']
lon_idx, lat_idx  = np.where((lon>=crop_box[0])&(lon<=crop_box[1]))[0], np.where((lat>=crop_box[2])&(lat<=crop_box[3]))[0]
# hgt[0, lon_idx, lat_idx] = 0.
''''''''''''''''''''''''''' ↓ test part ↓ '''''''''''''''''''''''''''
## 3.1 create figure and axes
fig = plt.figure(figsize=(10, 8))
ax  = plt.axes(projection=ccrs.LambertConformal(central_longitude=116, central_latitude=central_latitude, standard_parallels=(30.0, 60.0)))

## 3.2 add borders, coastlines, and states
add_cfeature(ax, linewidth=0.8)

## 3.3 add grid
add_gridlines(ax, linewidth=1, color='gray', linestyle='--', alpha=0.5, fontsize=18, fontname='Consolas')

# 3.4 restrict x-y extent
LON, LAT = np.meshgrid(lon, lat)
box = [np.min(LON)+1.41, np.max(LON)-1.51, np.min(LAT)+0.10, np.max(LAT)-0.21] if dim1 == 'd01' else \
      [np.min(LON)+0.12, np.max(LON)-0.20, np.min(LAT)+0.00, np.max(LAT)-0.10]
ax.set_extent(box, crs=ccrs.PlateCarree())

## 3.5 create image
im = ax.contourf(LON, LAT, hgt[0, :, :].data, extend='max', levels=levels, cmap=cmap, transform=ccrs.PlateCarree())

## 3.6 add colorbar
add_colorbar(im, ax, fig.add_axes(cax_box), fig, title='units: m', levels=levels, extend='max', orientation='vertical', labelsize=18, fontsize=26, fontname='Consolas', x_axis=0.95, y_axis=0.5)

## 3.7 set up title
ax.set_title(title, fontdict={'size': 28, 'family': 'Arial', 'weight': 'bold'})

## 3.8 adjust axes position
plt.subplots_adjust(right=0.79)

## 3.9 show, save and close
# plt.show()  # don't show.
if not os.path.exists(save_path):
    os.makedirs(save_path), print(f"Successfully create directory '{save_path}'!")
plt.savefig(os.path.join(save_path, f"{mode}-terrain_{res}_{dim1}.png"), dpi=300)
plt.close(fig), print("DONE."), dataset.close()
