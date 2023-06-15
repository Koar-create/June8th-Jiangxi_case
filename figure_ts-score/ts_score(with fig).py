import os, numpy as np, pandas as pd, xarray as xr
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from netCDF4 import Dataset
from datetime import datetime, timedelta
from matplotlib.font_manager import FontProperties

def obtain_tp24h(tp, skipnum=24):
    tp_added = np.concatenate((tp[:skipnum], tp[skipnum:] - tp[:-skipnum]), axis=0)
    tp_sum = np.cumsum(tp_added, axis=0)
    tp_24h = tp_sum[skipnum:]
    return tp_24h

def get_rainx_in_24h(wrf_file_path, timelen=39, timeinterval=3, mode=''):
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

def obtain_era5_timestr(era5_file_path, timeinterval=1):
    skipnum = int(24 / timeinterval)
    era5_data = xr.open_dataset(era5_file_path)
    time = era5_data["time"].dt
    year, month, day , hour = time.year.data, time.month.data, time.day.data, time.hour.data
    year, month, day , hour = year[skipnum:], month[skipnum:], day[skipnum:] , hour[skipnum:]
    era5_data.close()
    era5_timestr_list = [j.strftime('%Y-%m-%d %H:%M:%S') for j in [datetime(year[i], month[i], day[i], hour[i], 0, 0) for i in range(tp.shape[0])]]
    return era5_timestr_list

def obtain_wrf_timestr(timelen=31, format='%Y-%m-%d %H:%M:%S', dhour=3, syear=2016, smonth=6, sday=17, shour=0, smin=0, ssec=0):
    delta = timedelta(hours=dhour)
    wrf_timestr_list = [j.strftime(format) for j in [datetime(syear, smonth, sday, shour, smin, ssec) + delta * i for i in range(timelen)]]
    return wrf_timestr_list

def obtain_ts_score(tp, rain24, era5_timestr_list, wrf_timestr_list, closest_index_path):
    df = pd.read_csv(closest_index_path, sep='\t')
    closest_index_list = [tuple(row) for row in df.values]
    '''
    ts_score_list = []
    for idx_wrf in range(len(wrf_timestr_list)):
        idx_era5 = era5_timestr_list.index(wrf_timestr_list[idx_wrf])
        tp_temp  = tp[idx_era5, :, :]
        wrf_temp = rain24[idx_wrf , :, :].ravel()
        num = sum((np.isnan(tp_temp[closest_index_list[i]]) and np.isnan(wrf_temp[i])) or (not np.isnan(tp_temp[closest_index_list[i]]) and not np.isnan(wrf_temp[i])) for i in range(len(wrf_temp)))
        den = len(wrf_temp) + 1
        ts_score = num / den * 100
        ts_score_list.append(ts_score)
    '''
    ts_score_list = [sum((np.isnan(tp[era5_timestr_list.index(wrf_timestr_list[idx_wrf]), :, :][closest_index_list[i]]) and np.isnan(rain24[idx_wrf , :, :].ravel()[i])) or (not np.isnan(tp[era5_timestr_list.index(wrf_timestr_list[idx_wrf]), :, :][closest_index_list[i]]) and not np.isnan(rain24[idx_wrf , :, :].ravel()[i])) for i in range(len(rain24[idx_wrf , :, :].ravel()))) / (len(rain24[idx_wrf , :, :].ravel()) + 1) * 100 for idx_wrf in range(len(wrf_timestr_list))]
    return ts_score_list

font = FontProperties(family='Consolas')

dim1 = 'd02'     # 'd01'      or 'd02'
dim4 = 'all'     # 'scheme 1' or 'scheme 2' or 'scheme 3' or 'all'
dim5 = '10 mm'  # '0.1 mm'   or '10 mm' or '25 mm' or '50 mm'  or '100 mm' or '250 mm'

era5_file_path     = f'D:\\Repositories\\adaptor\\adaptor.land_hourly_rain.nc'
wrf_file_path      = f"D:\\Repositories\\wrfout ({dim4}"+f", 2 domains)\\wrfout_{dim1}_" if dim4 != 'all' else \
                    [f"D:\\Repositories\\wrfout (scheme {i}, 2 domains)\\wrfout_{dim1}_" for i in range(1, 4)]
save_path          = f"D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_ts-score"
closest_index_path = f'D:\\Repositories\\June8th-Jiangxi_case\\closest_index_list.txt'
title = f"TS score series of 3 schemes from 2016-06-17 00:00:00\nto 2016-06-20 18:00:00 (UTC) ({dim5})" if dim4 == 'all' else \
        f"TS score series of {dim4}" +"from 2016-06-17 00:00:00\nto 2016-06-20 18:00:00 (UTC)"

## 1.read nc files ##
# read era5 file
era5_data = xr.open_dataset(era5_file_path)
tp = era5_data["tp" ][:].data
era5_data.close()
tp = obtain_tp24h(tp)
# read wrfout files
rain24 = [get_rainx_in_24h(i, mode='') for i in wrf_file_path] if dim4 == 'all' else get_rainx_in_24h(wrf_file_path, mode='')

## 2. process data ##
tp_0, rain24_0 = tp.copy(), rain24.copy()
threshold = float(dim5.split(' ')[0])
tp[np.where(tp < threshold)] = np.nan
'''
if dim4 == 'all':
    for i in range(3):
        rain24[i][np.where(rain24[i] < threshold)] = np.nan
else:
    rain24[np.where(rain24 < threshold)] = np.nan
'''
rain24 = [np.where(rain24[i] < threshold, np.nan, rain24[i]) for i in range(3)] if dim4 == 'all' else np.where(rain24 < threshold, np.nan, rain24)

## 3. get time strings of era5 file and wrfout file ##
era5_timestr_list = obtain_era5_timestr(era5_file_path)
wrf_timestr_list  = obtain_wrf_timestr()

## 4. calculate ts score ##
# law: TT or FF means hit; TF or FT means miss.
ts_score_list = [obtain_ts_score(tp,      i, era5_timestr_list, wrf_timestr_list, closest_index_path) for i in rain24] if dim4 == 'all' else \
                 obtain_ts_score(tp, rain24, era5_timestr_list, wrf_timestr_list, closest_index_path)

## 5. paint figure ##
fig, ax = plt.subplots(figsize=(10,11))
xdates = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in wrf_timestr_list]
if dim4 == 'all':
    p1 = ax.plot(xdates, ts_score_list[0], linewidth=2, color='r', linestyle='-' , label='scheme 1')
    p2 = ax.plot(xdates, ts_score_list[1], linewidth=2, color='b', linestyle='--', label='scheme 2')
    p3 = ax.plot(xdates, ts_score_list[2], linewidth=2, color='k', linestyle=':' , label='scheme 3')
else:
    p1 = ax.plot(xdates, ts_score_list,    linewidth=3, color='r', linestyle='-' , label=dim5)
# put on title
fig.text(0.50, 0.91, title         , fontdict={'size': 27, 'family': 'Arial'   , 'weight': 'bold'  , 'ha': 'center'})
# x-label
fig.text(0.50, 0.01, 'time'        , fontdict={'size': 24, 'family': 'Consolas', 'weight': 'normal', 'va': 'bottom', 'ha': 'center'})
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %Hh'))
ax.set_xticklabels(ax.get_xticklabels(),       rotation=30,   fontsize=18)
# y-label
fig.text(0.07, 0.50, 'TS score (%)', fontdict={'size': 24, 'family': 'Consolas', 'weight': 'normal', 'va': 'center', 'ha': 'center', 'rotation': 'vertical'})
ax.set_yticks(np.linspace(0, 100, 11))
ax.set_yticklabels(ax.get_yticklabels(), fontproperties=font, fontsize=18)
# add grid and legend
ax.grid(linewidth=1, color='k', linestyle='--', alpha=0.6)
ax.legend(loc='best', fontsize=18)
# plt.show()

## 6. save picture ##
if os.path.exists(save_path):
    print(f"directory {save_path} already exists.")
else:
    os.makedirs(save_path)
    print(f"Successfully create directory {save_path}.")
plt.savefig(os.path.join(save_path, f"ts-score_{dim4}_{dim5}.png"), dpi=100)

## 7. close figure ##
plt.close(fig)
