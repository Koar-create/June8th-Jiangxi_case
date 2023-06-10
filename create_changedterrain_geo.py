import netCDF4 as nc
import xarray as xr

# 打开.nc文件（以读写模式）
file_path = '/home/koyomi/Downloads/geo_em.d00.nc'  # 将路径替换为你的文件路径
dataset = nc.Dataset(file_path, 'r+')
nc_data = xr.open_dataset(file_path)

# 获取要修改的变量
lon = nc_data['XLONG_M']
lat = nc_data['XLAT_M']
hgt = nc_data['HGT_M']
hgt1 = nc_data['HGT_M'].sel(lat=(28,30), lon=(116,119))
print(hgt.shape, hgt1.shape)
# variable = dataset.variables[variable_name]

# # 获取变量的当前数据
# data = variable[:]

# # 添加一个数字到每个元素
# number_to_add = 10
# modified_data = data + number_to_add

# # 将修改后的数据写回变量
# variable[:] = modified_data

# 关闭数据集，保存修改
dataset.close()