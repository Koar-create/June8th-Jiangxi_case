import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import netCDF4 as nc
import os

file_path = os.path.join(os.getcwd(), 'wrfout/wrfout_d01_2016-06-16_00:00:00')
dataset = nc.Dataset(file_path)

variable_names = dataset.variables.keys()

for name in variable_names:
    variable = dataset.variables[name]
    dimensions = '*'.join(str(dimension) for dimension in variable.shape)
    print(f"Variable: {name} {dimensions}")
    print("Attributes:")
    for attr_name in variable.ncattrs():
        attr_value = variable.getncattr(attr_name)
        print(f" {attr_name}: {attr_value}")
    print()

dataset.close()
