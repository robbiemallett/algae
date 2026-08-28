import xarray as xr
import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
from netCDF4 import Dataset
import pandas as pd
import cartopy
import cartopy.crs as ccrs
import tqdm
import pickle
import itertools

grid_d = Dataset('inputs/conc.nc')
lon,lat=np.array(grid_d['longitude']),np.array(grid_d['latitude'])

# Made by process_ERA5
dt = d = np.array(Dataset('inputs/ssrd.nc')['time'])

# Made by plot_pens.ipynb
(ssrd_ridge_umol,ssrd_level_umol) = pickle.load(open('umols.p','rb'))

dsr = xr.DataArray(name='ridged_ice_bottom_PAR',
    data=ssrd_ridge_umol,
    coords={'time':dt,
            'latitude':(['x','y'],lat),
            'longitude':(['x','y'],lon),
           },
    dims=['time','x','y'],
)

dsl = xr.DataArray(name='level_ice_bottom_PAR',
    data=ssrd_level_umol,
    coords={'time':dt,
            'latitude':(['x','y'],lat),
            'longitude':(['x','y'],lon),
           },
    dims=['time','x','y'],
)



ds = xr.merge([dsr,dsl])

ds.to_netcdf('PAR_V1_5.nc')
