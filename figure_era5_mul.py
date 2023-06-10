import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.gridspec as gridspec
import cartopy.feature as cfeature
from netCDF4 import Dataset
from PIL import Image
import xarray as xr

def crop_image(image_path, fraction):
    # 打开图像
    image = Image.open(image_path)

    # 获取图像宽度和高度
    width, height = image.size

    # 计算裁剪后的宽度
    new_width = int(width * fraction)

    # 创建一个新的图像对象，尺寸为裁剪后的尺寸
    new_image = Image.new("RGB", (new_width, height))

    # 裁剪图像
    new_image.paste(image.crop((0, 0, new_width, height)), (0, 0))

    # 保存裁剪后的图像
    new_image.save(image_path)

    # 关闭图像
    image.close()
    new_image.close()

# 读取.nc文件
nc_file = r'D:\Repositories\adaptor\adaptor.land_hourly.nc'
# nc_data = Dataset(nc_file, 'r')
nc_data = xr.open_dataset(nc_file)

# 读取经度、纬度和变量数据
year, month = np.array(nc_data["time"].dt.year), np.array(nc_data["time"].dt.month)
day, hour = np.array(nc_data["time"].dt.day), np.array(nc_data["time"].dt.hour)
# t = nc_data.variables['time'][:]
# lon = nc_data.variables['lon'][:]
# lat = nc_data.variables['lat'][:]
# tp = nc_data.variables['tp'][:]
lon, lat = np.array(nc_data["lon"]), np.array(nc_data["lat"])
tp = np.array(nc_data["tp"])

# 输出维度数据
print("time shape:", year.shape)
print("lon shape:", lon.shape)
print("lat shape:", lat.shape)
print("tp shape:", tp.shape)

# 创建地图投影
# proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))
proj = ccrs.PlateCarree(central_longitude=115.5)

for i in range(0, year.shape[0]):
    # 创建绘图窗口和轴
    fig = plt.subplots(figsize=(10, 8))

    # 创建自定义图形布局
    gs = gridspec.GridSpec(1, 2, width_ratios=[9.8, 0.2])  # 分为左右两列，左列宽度为9，右列宽度为1
    ax = plt.subplot(gs[0], projection=proj)

    # 绘制地图边界、海岸线和国家边界线
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.5)

    # 绘制经纬网格
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5, linewidth=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.xlabels_bottom = True
    gl.ylabels_left = True
    gl.ylabels_right = True
    gl.xlabel_style = {'fontsize': 14, 'fontname': 'Consolas'}
    gl.ylabel_style = {'fontsize': 14, 'fontname': 'Consolas'}

    # 绘制数据
    im = ax.pcolormesh(lon, lat, tp[i,:,:]*1000, vmin=0, vmax=100, cmap='jet', transform=ccrs.PlateCarree())

    # 添加颜色条
    cax = plt.subplot(gs[1])
    cbar = plt.colorbar(im, extend='max', \
        ax=ax, orientation='vertical', cax=cax)
    ticklabels = cbar.ax.get_yticklabels()          # 刻度1
    c_font = {'family': 'Consolas', 'size': 14}     # 刻度2
    cbar.ax.tick_params(labelsize=14)               # 刻度3
    for label in ticklabels:                        # 刻度4
        label.set_fontproperties(c_font)            # 刻度5
    cbar.set_label('units: mm', fontdict=c_font)    # 标题1
    cbar.ax.set_aspect(40)  # 调整高度和宽度的比例，此处为10

    # 设置标题和坐标轴标签
    timestr = f'{year[i]:02}-{month[i]:02}-{day[i]:02} {hour[i]:02}:00:00 UTC'
    ax.set_title('observation records (from ERA-5) \ntotal precipitation '+timestr, fontsize=14, fontname='Arial')
    ax.set_xlabel('Longitude', fontsize=14, fontname='Consolas')
    ax.set_ylabel('Latitude', fontsize=14, fontname='Consolas')

    # x-y axis limit
    ax.set_xlim([np.min(lon)-93, np.max(lon)-137])
    ax.set_ylim([np.min(lat)+20, np.max(lat)-20])
    # ax.set_xlim([np.min(lon)-900000, np.max(lon)+900000])
    # ax.set_ylim([np.min(lat)-700000, np.max(lat)+1100000])

    plt.subplots_adjust(right=0.65)

    # plt.show()

    plt.savefig('D:\\Repositories\\June8th-Jiangxi_case\\fig_era5\\tp_'+timestr[:-10]+'.png', dpi=600)

    crop_image('D:\\Repositories\\June8th-Jiangxi_case\\fig_era5\\tp_'+timestr[:-10]+'.png', 0.75)