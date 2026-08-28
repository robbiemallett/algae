import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
from netCDF4 import Dataset
import pandas as pd
import tqdm
import pickle
import itertools

# WORKS WITH nep conda env
# dir = '/home/robbie/uit_mnt/home/romal7177/algae'
# Made on the server
print('reading')
lpp,rpp = pickle.load(open(f'level_ridged_pens.p','rb'))#Level Partial Pen, Ridged Partial Pen
ltp = lpp*0.607
rtp = rpp*0.607

grid_d = Dataset('inputs/conc.nc')
lon,lat=np.array(grid_d['longitude']),np.array(grid_d['latitude'])

# Made by process_ERA5.ipynb
ssrd = np.array(Dataset('inputs/ssrd.nc')['ssrd'])

mol = 0.79*4.44

ssrd_ridge_umol = np.multiply(mol*ssrd,rtp)
ssrd_level_umol = np.multiply(mol*ssrd,ltp)
print('saving')
pickle.dump((ssrd_ridge_umol,ssrd_level_umol),open('umols.p','wb'))
