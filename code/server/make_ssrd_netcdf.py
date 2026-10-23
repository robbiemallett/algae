### conda activate bluemarble

#import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
from netCDF4 import Dataset
#from regrid import regrid
import pandas as pd
import cartopy
import cartopy.crs as ccrs
import tqdm
import pickle
import itertools
import xarray as xr

ssrd = pickle.load(open('inputs/ssrd.p','rb'))
dts = pickle.load(open('inputs/dts.p','rb'))

d=Dataset('inputs/conc.nc')
pslon = np.array(d['longitude'])
pslat = np.array(d['latitude'])

attrs = {"units": "watts per m2 per second"}

ds = xr.DataArray(name='ssrd',
    data=ssrd/3600,
    coords={'time':dts,
            'latitude':(['x','y'],pslat),
            'longitude':(['x','y'],pslon),
           },
                  attrs=attrs,
    dims=['time','x','y'],
)

ds.to_netcdf('ssrd.nc')
