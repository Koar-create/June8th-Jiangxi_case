import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.gridspec as gridspec
import cartopy.feature as cfeature
from netCDF4 import Dataset
from PIL import Image

def crop_image(image_path):
    # 打开图像
    image = Image.open(image_path)

    # 获取图像宽度和高度
    width, height = image.size

    # 计算裁剪后的宽度
    new_width = int(width * 0.75)

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
nc_files = []
for day in [16,17,18,19,20]:
    for hour in ['00','03','06','09','12','15','18']:
        nc_files.append(r'D:\Repositories\wrfout (no scheme, 2 domains) (fnl)\wrfout_d01_2016-06-'+str(day)+'_'+hour+'%3A00%3A00')

for nc_file in nc_files: 
    
    # Create time string
    date = nc_file.split("_")[-2]
    hour = nc_file.split("%3A")[-3][-2:]
    timestr = date + ' ' + hour + ':00:00 UTC'

    # open dataset
    nc_data = Dataset(nc_file, 'r')

    # 读取经度、纬度和变量数据
    lon = nc_data.variables['XLONG'][0, :, :]
    lat = nc_data.variables['XLAT'][0, :, :]
    rainc = nc_data.variables['RAINC'][0, :, :]
    rainnc = nc_data.variables['RAINNC'][0, :, :]
    rain = rainc + rainnc

    # 输出维度数据
    print("lon shape:", lon.shape)
    print("lat shape:", lat.shape)
    print("rain shape:", rain.shape)

    # 创建地图投影
    proj = ccrs.LambertConformal(central_longitude=115.5, central_latitude=25, standard_parallels=(30, 60))
    # proj = ccrs.PlateCarree(central_longitude=115.5)

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
    gl.xlabels_bottom = False
    gl.ylabels_right = True
    gl.ylabels_left = True
    # gl.xlabel_style = {'fontsize': 14, 'fontname': 'Consolas'}
    gl.ylabel_style = {'fontsize': 14, 'fontname': 'Consolas'}

    # 绘制数据
    im = ax.pcolormesh(lon, lat, rain, cmap='jet', vmin=0, vmax=350, transform=ccrs.PlateCarree())

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
    ax.set_title('without scheme\naccumulated total cumulus precipitation '+timestr, fontsize=16, fontname='Arial')
    ax.set_xlabel('Longitude', fontsize=14, fontname='Consolas')
    ax.set_ylabel('Latitude', fontsize=14, fontname='Consolas')

    print(np.max(rain),np.min(rain))
    print(np.min(lat),np.max(lat))
    print(np.min(lon),np.max(lon))
    ax.set_xlim(np.min(lon)-900000, np.max(lon)+900000)
    ax.set_ylim(np.min(lat)-700000, np.max(lat)+1100000)
    
    plt.subplots_adjust(right=0.65)

    # plt.show()

    plt.savefig("D:\\Repositories\\June8th-Jiangxi_case\\fig_wrfout (no scheme, 2 domains) (fnl)\\rainc+rainnc_"+timestr[:-10]+".png", dpi=600)
    crop_image("D:\\Repositories\\June8th-Jiangxi_case\\fig_wrfout (no scheme, 2 domains) (fnl)\\rainc+rainnc_"+timestr[:-10]+".png")