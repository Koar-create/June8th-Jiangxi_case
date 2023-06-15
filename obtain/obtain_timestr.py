import xarray as xr
from datetime import datetime, timedelta

def obtain_era5_timestr(era5_file_path, timeinterval=1):
    skipnum = int(24 / timeinterval)
    era5_data = xr.open_dataset(era5_file_path)
    time = era5_data["time"].dt
    year, month, day , hour = time.year.data, time.month.data, time.day.data, time.hour.data
    year, month, day , hour = year[skipnum:], month[skipnum:], day[skipnum:] , hour[skipnum:]
    era5_data.close()
    era5_timestr_list = [j.strftime('%Y-%m-%d %H:%M:%S') for j in [datetime(year[i], month[i], day[i], hour[i], 0, 0) for i in range(year.shape[0])]]
    return era5_timestr_list

def obtain_wrf_timestr(timelen=31, format='%Y-%m-%d %H:%M:%S', dhour=3, syear=2016, smonth=6, sday=17, shour=0, smin=0, ssec=0):
    delta = timedelta(hours=dhour)
    wrf_timestr_list = [j.strftime(format) for j in [datetime(syear, smonth, sday, shour, smin, ssec) + delta * i for i in range(timelen)]]
    return wrf_timestr_list