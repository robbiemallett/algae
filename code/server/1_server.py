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

    
def get_pen_from_combo(snow,sit,melt_pond_fraction=None):

    if melt_pond_fraction:

        factor=4.17
        sit=sit * (1 + (1 / factor - 1) * melt_pond_fraction)
    
    snow_rnd = myround(snow,prec=2,base=0.01)
    sit_rnd = myround(sit,prec=2,base=0.05)

    combo = (np.round(fpl*(snow_rnd)),
             np.round(fpl*(sit_rnd)))
             

    pen = float(pen_df.loc[[combo]]['penetration'].iloc[0])

    return pen

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
        
mpf = np.array(Dataset('inputs/mpf.nc')['melt_pond_fraction_filled'])/100
    
failures=0
    
for rfcode in ['20','60']:
    
    if rfcode=='60':
        rf = np.array(Dataset(f'inputs/rf_L{rfcode}_D{rfcode}.nc')['ridged_fraction_filled'])
    else:
        rf = np.array(Dataset(f'inputs/rf_W{rfcode}_D{rfcode}.nc')['ridged_fraction_filled'])

    
    cum_sit_probs=np.cumsum(sit_probs)
    
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

            try:
                ridged_fraction = rf[i,j]
                melt_pond_fraction = mpf[i,j]
    
                if ridged_fraction>100:raise
                if melt_pond_fraction>100:raise
        
                sit_split = -np.argmax((1-cum_sit_probs[::-1])>ridged_fraction)
        
                if sit_split==0:
                    # Ridge fraction = 1
                    level_pens[i,j]=np.nan
                else:
                    level_pens_list=[]
                    for sit in sits[:sit_split]:
                        pens = [get_pen_from_combo(sd,sit) for sd in snow_depth_bins]
                        # Adjust the first penetration value for extra melt pond penetration
                        pens[0]=get_pen_from_combo(snow_depth_bins[0],sit,melt_pond_fraction)
                        level_pen = np.average(pens,weights=snow_probs)
                        level_pens_list.append(level_pen)
                    all_level_pen = np.average(level_pens_list,weights=sit_probs[:sit_split])
                    level_pens[i,j]=all_level_pen
        
        
                ridged_pens_list=[]
                for sit in sits[sit_split:]:
                    pens = [get_pen_from_combo(sd,sit) for sd in snow_depth_bins]
                    ridged_pen = np.average(pens,weights=snow_probs)
                    ridged_pens_list.append(ridged_pen)
                all_ridged_pen = np.average(ridged_pens_list,weights=sit_probs[sit_split:])
                ridged_pens[i,j]=all_ridged_pen
            except Exception as e:
                print(e)
                failures+=1
                
            
    pickle.dump((level_pens,ridged_pens),open(f'level_ridged_pens_{rfcode}.p','wb'))

print('number of failures:')
print(failures)
