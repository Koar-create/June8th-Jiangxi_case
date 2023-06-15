import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import xarray as xr
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os, sys

def obtain_tp_in_24h(tp, skipnum=24):
    for i in range(5):
        tp[(1 + skipnum * i):(1 + skipnum + skipnum * i), :, :] += tp[skipnum * i, :, :]
    tp_24h = tp[skipnum:, :, :] - tp[:-skipnum, :, :]
    return tp_24h