import netCDF4 as nc

# open the .nc file
# file_path = '/home/koyomi/WRF-ARW/WPS/geo_em.d01.nc'
file_path = '/home/koyomi/Repositories/June8th-Jiangxi_case/wrfout_d01_2016-06-16_00:00:00.nc'
dataset = nc.Dataset(file_path)

# Attain start time and end time
# start_time = dataset.variables['Times'][0, 0]
# end_time = dataset.variables['Times'][0, -1]

# 获取起始经度和结束经度
start_longitude = dataset.variables['XLONG'][0, 0, 0]
end_longitude = dataset.variables['XLONG'][0, 0, -1]

# 获取起始纬度和结束纬度
start_latitude = dataset.variables['XLAT'][0, 0, 0]
end_latitude = dataset.variables['XLAT'][0, -1, 0]

# 获取各维度的长度
# time_dim = dataset.variables['Times'].shape
latitude_dim = dataset.variables['XLAT'].shape
longitude_dim = dataset.variables['XLONG'].shape
# vertical_length = len(dataset.dimensions['vertical'])

# 输出信息
# print("起始时间:", start_time)
# print("结束时间:", end_time)
print(f"起始/结束经度:({start_longitude}, {end_longitude})")
print(f"起始/结束纬度:({start_latitude}, {end_latitude})")
# print("时间维度:", time_dim)
print("经向维度:", longitude_dim)
print("纬向维度:", latitude_dim)
# print("垂直维度长度:", vertical_length)

# 关闭数据集
dataset.close()