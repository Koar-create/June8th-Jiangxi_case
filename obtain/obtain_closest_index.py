import numpy as np, xarray as xr, pandas as pd
from netCDF4 import Dataset

dim1 = 'd02'  # 'd01' or 'd02'

era5_file_path = 'D:\\Repositories\\adaptor\\adaptor.land_hourly_rain.nc'
wrf_file_path = f"D:\\Repositories\\wrfout (scheme 1, 2 domains, modified terrain)\\wrfout_{dim1}_"

era5_data = xr.open_dataset(era5_file_path)
era5_lon, era5_lat = era5_data["lon"][:].data, era5_data["lat"][:].data
era5_data.close()
era5_LON, era5_LAT = np.meshgrid(era5_lon, era5_lat)


wrf_data = Dataset(wrf_file_path + '2016-06-17_00%3A00%3A00', 'r')
wrf_LON, wrf_LAT = wrf_data.variables['XLONG'][0, :, :].data, wrf_data.variables['XLAT'][ 0, :, :].data

closest_index_list = [np.unravel_index(np.argmin(np.sqrt((era5_LON - wrf_LON.ravel()[i])**2 + (era5_LAT - wrf_LAT.ravel()[i])**2)), era5_LON.shape) for i in range(0, wrf_LAT.shape[0] * wrf_LAT.shape[1])]

print(f"show partial closest indexs: {closest_index_list[:5]}")
print(f"Two lengths are: {len(closest_index_list)}, {wrf_LAT.shape[0] * wrf_LAT.shape[1]}.")

# create DataFrame 
df = pd.DataFrame(closest_index_list, columns=['closest_index_1', 'closest_index_2'])
df.to_csv('D:\\Repositories\\June8th-Jiangxi_case\\closest_index_list.txt', sep='\t', index=False, header=True)
print("Successfully write into closest_index_list.txt. ")

df = pd.read_csv('D:\\Repositories\\June8th-Jiangxi_case\\closest_index_list.txt', sep='\t')
closest_index_list = [tuple(row) for row in df.values]

if len(closest_index_list) == wrf_LAT.shape[0] * wrf_LAT.shape[1]:
    print(f"Successfully read closest_index_list.txt. Two lengths are: {len(closest_index_list)}, {wrf_LAT.shape[0] * wrf_LAT.shape[1]}.")
    print(f"show partial closest indexs: {closest_index_list[:5]}")