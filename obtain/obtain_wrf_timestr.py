import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import xarray as xr
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os, sys

def obtain_wrf_timestr(timelen=31, format='%Y-%m-%d %H:%M:%S', dhour=3, syear=2016, smonth=6, sday=17, shour=0, smin=0, ssec=0):
    delta = timedelta(hours=dhour)
    wrf_timestr_list = [j.strftime(format) for j in [datetime(syear, smonth, sday, shour, smin, ssec) + delta * i for i in range(timelen)]]
    return wrf_timestr_list
