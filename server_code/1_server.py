### conda activate bluemarble

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
fpl=10000

def myround(x, prec=2, base=.05):
  return round(base * round(float(x)/base),prec)

#Made by SIT_and_SNOW.ipynb
d = Dataset('inputs/sit_dists_array.nc')
sit_probs = np.array(d['thicknesses'])
sit_dists = np.array(d['sit_dists'])

# Made by Make_Area_partition.ipynb

d = Dataset('inputs/snow_dists_array.nc')
depth_cols = np.array(d['snow_depths'])
snow_dists = np.array(d['snow_dists'])
pen_df = pd.read_csv('inputs/pen_df.csv')
pen_df['combo']=[(int(i*fpl),int(j*fpl)) for i,j in zip(pen_df['depth'],pen_df['sit'])]
pen_df.set_index('combo',inplace=True)

#Made by SIT_and_SNOW.ipynb
ijs = pd.read_csv('inputs/valid_ijs.csv')
valid_ijs = [(x,y) for x,y in zip(ijs['i'],ijs['j'])]

rf = np.array(Dataset('inputs/rf.nc')['ridged_fraction_filled'])
mpf = np.array(Dataset('inputs/mpf.nc')['melt_pond_fraction_filled'])/100


cum_sit_probs=np.cumsum(sit_probs)

cum_sit_probs

# -np.argmax((1-cum_sit_probs[::-1])>0.03)

def get_pen_from_combo(snow,sit):

    snow_rnd = myround(snow,prec=2,base=0.01)
    sit_rnd = myround(sit,prec=2,base=0.05)

    combo = (np.round(fpl*(snow_rnd)),
             np.round(fpl*(sit_rnd)))
             

    pen = float(pen_df.loc[[combo]]['penetration'].iloc[0])

    return pen

level_pens = np.full(shape=(896,608),fill_value=np.nan)
ridged_pens = np.full(shape=(896,608),fill_value=np.nan)

for i,j in tqdm.tqdm(valid_ijs):

    snow_probs = snow_dists[i,j]
    snow_depth_bins = depth_cols
    
    sits = sit_dists[i,j]

    ridged_fraction = rf[i,j]
    melt_pond_fraction = mpf[i,j]

    if np.isnan(sits[0]):        pass
    elif np.isnan(snow_probs[0]):        pass
    elif np.isnan(ridged_fraction):        pass
    elif np.isnan(melt_pond_fraction):        pass
    

    else:
        
        ridged_fraction = rf[i,j]
        melt_pond_fraction = mpf[i,j]

        sit_split = -np.argmax((1-cum_sit_probs[::-1])>0.2)
        
        level_pens_list=[]
        for sit in sits[:sit_split]:
            pens = [get_pen_from_combo(sd,sit) for sd in snow_depth_bins]
            level_pen = np.average(pens,weights=snow_probs)
            level_pens_list.append(level_pen)
        all_level_pen = np.average(level_pens_list,weights=sit_probs[:sit_split])
        level_pens[i,j]=all_level_pen

        if sit_split==0:
            ridged_pens[i,j]=np.nan
        
        ridged_pens_list=[]
        for sit in sits[sit_split:]:
            pens = [get_pen_from_combo(sd,sit) for sd in snow_depth_bins]
            ridged_pen = np.average(pens,weights=snow_probs)
            ridged_pens_list.append(ridged_pen)
        all_ridged_pen = np.average(ridged_pens_list,weights=sit_probs[sit_split:])
        ridged_pens[i,j]=all_ridged_pen
        
pickle.dump((level_pens,ridged_pens),open('level_ridged_pens.p','wb'))
