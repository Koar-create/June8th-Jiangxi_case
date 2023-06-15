import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import xarray as xr
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os, sys

sys.path.append('D:\\Repositories\\June8th-Jiangxi_case')
sys.path.append('D:\\Repositories\\June8th-Jiangxi_case\\obtain')
from obtain_wrf_timestr import obtain_wrf_timestr


def obtain_rainx_in_24h(wrf_file_path, timelen=39, timeinterval=3, mode=''):
    skipnum = int(24 / timeinterval)
    nc_file_list = [f"{wrf_file_path}{date.replace(':', '%3A')}" for date in obtain_wrf_timestr(timelen, format='%Y-%m-%d_%H:%M:%S', sday=16)]
    
    for idx, nc_file in enumerate(nc_file_list):
        nc_data = Dataset(nc_file, 'r')
        rainc_temp  = nc_data.variables['RAINC' ][:].data
        rainnc_temp = nc_data.variables['RAINNC'][:].data
        nc_data.close()
        rain_temp   = rainc_temp + rainnc_temp
        if mode == '':
            rain24h_temp = rain_temp
        elif mode.lower() == 'rainc':
            rain24h_temp = rainc_temp
        elif mode.lower() == 'rainnc':
            rain24h_temp = rainnc_temp
        rain24h = rain24h_temp if idx == 0 else np.concatenate((rain24h, rain24h_temp), axis=0)
    rain24h = rain24h[skipnum:, :, :] - rain24h[:-skipnum, :, :]
    return rain24h