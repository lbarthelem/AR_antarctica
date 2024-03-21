import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
import sys


#file count have to be in .pkl
file_count = str(sys.argv[1])
df = pd.read_pickle(file_count)

#file vIVT in .nc
vivt_file = str(sys.argv[2])
vivt = xr.open_dataset(vivt_file).vIVT



#file precip  in .nc
pr_file = str(sys.argv[3])
pr = xr.open_dataset(pr_file).pr

#file tas in .nc
tas_file = str(sys.argv[4])
tas = xr.open_dataset(tas_file).tas

#file land_mask
land_mask_file = '/data/lbarthelemy/land_mask/antartica_mask_IPSL-CM6A-LR.nc'
land_mask = xr.open_dataset(land_mask_file).land_mask
lat_ant = land_mask.where(land_mask == 1, drop = True).lat.values
lon_ant = land_mask.where(land_mask == 1, drop = True).lon.values

#pr and tas Antarctica
pr_antar = pr.sel(lon = lon_ant, lat= lat_ant, method = 'nearest')
tas_antar = tas.sel(lon = lon_ant, lat= lat_ant, method = 'nearest')


all_area = []       # area of each time of all the ARs events
vivt_all_mean = []  # vIVT mean of each time of all the ARs events
pr_all_sum = []     # pr sum of each time of all the Ars events
tas_all_mean = []   # tas mean of each time of all the ARs events

vivt_mean_ev = []     # vIVT mean of all the ARs events
area_mean_ev = []     # area mean of all the ARs events
vivt_max_ev = []      # vIVT max of all the ARs events
pr_sum_ev = []        # sum of pr for each events
tas_mean_ev = []      # tas mean of all the ARs events
tas_max_ev = []       # tas max of all the ARs events
antar_ev = []         # 1 if event touch antarctica
tas_max_antar_ev = [] # tas max of all the ARs events in antarctica
pr_sum_antar_ev = []  # pr sum of all the ARs events in antarctica


i = 0 # indice of event

geod = Geod('+a=6378137 +f=0.0033528106647475126') # for computing area with pyproj

for ev in df.time_ar:
    area = []           #successive area of the event
    vivt_mean = []      #successive vIVT mean of the event
    vivt_max = []       #successive vIVT max of the event
    tas_mean = []       #successive tas mean of the event
    tas_max = []        #successive tas max of the event
    pr_sum = []         #successive sum of pr of the event
    antar = []          #successive touch of antarctica
    tas_max_antar = []  #successive tas max in antarctica of the event
    pr_sum_antar = []   #successive sum of pr in antarctica of the event
    
    
    if type(ev) is list:
        j = 0           # indice of time in the event

        for time in ev:
            
            print(time)
            lon = df.ar_pos[i][j][:,1]
            lat = df.ar_pos[i][j][:,0]

            "============= compute area if more than 1 time step =============="
            poly_area, poly_perimeter = geod.polygon_area_perimeter(lon, lat)
            area.append(abs(poly_area))

            "============= compute vIVT mean if more than 1 time step =============="
            vivt_date = vivt.sel(time = time)
            vivt_ar = vivt_date.sel(lon = lon, lat = lat, method="nearest")
            mean_value = float(vivt_ar.mean().values)
            max_value = float(vivt_ar.min().values)
            vivt_mean.append(mean_value)
            vivt_max.append(max_value)
            
            pr_date = pr.sel(time = time)
            pr_ar = pr_date.sel(lon = lon, lat = lat, method = 'nearest')
            sum_value = float(pr_ar.sum().values)
            pr_sum.append(sum_value)
            
            tas_date = tas.sel(time = time)
            tas_ar = tas_date.sel(lon = lon, lat = lat, method = 'nearest')
            mean_value = float(tas_ar.mean().values)
            max_value = float(tas_ar.max().values) 
            tas_mean.append(mean_value)
            tas_max.append(max_value)

            ar_antar = land_mask.sel(lon = lon, lat = lat, method="nearest")
            max_value = float(ar_antar.max().values)
            antar.append(max_value)
            
            pr_antar_date = pr_antar.sel(time = time)
            pr_ar_antar_date = pr_antar_date.sel(lon = lon, lat = lat, method="nearest")
            sum_value = float(pr_ar_antar_date.mean().values)
            pr_sum_antar.append(sum_value)
            
            tas_antar_date = tas_antar.sel(time = time)
            tas_ar_antar_date = tas_antar_date.sel(lon = lon, lat = lat, method = "nearest")
            max_value = float(tas_ar_antar_date.max().values)
            tas_max_antar.append(max_value)


            j += 1


    else:
        time = ev
        lon = df.ar_pos[i][:,1]
        lat = df.ar_pos[i][:,0]

        "============= compute area if only 1 time step =============="
        poly_area, poly_perimeter = geod.polygon_area_perimeter(lon, lat)
        area.append(abs(poly_area))

        "============= compute vIVT mean if only 1 time step =============="
        vivt_date = vivt.sel(time = ev)
        vivt_ar = vivt_date.sel(lon = lon, lat = lat, method="nearest")
        max_value = float(vivt_ar.min().values)
        mean_value = float(vivt_ar.mean().values)

        vivt_mean.append(mean_value)
        vivt_max.append(max_value)

        pr_date = pr.sel(time = time)
        pr_ar = pr_date.sel(lon = lon, lat = lat, method = 'nearest')
        sum_value = float(pr_ar.sum().values)
        pr_sum.append(sum_value)

        tas_date = tas.sel(time = time)
        tas_ar = tas_date.sel(lon = lon, lat = lat, method = 'nearest')
        mean_value = float(tas_ar.mean().values)
        max_value = float(tas_ar.max().values) 
        tas_mean.append(mean_value)
        tas_max.append(max_value)


        ar_antar = land_mask.sel(lon = lon, lat = lat, method="nearest")
        max_value = float(ar_antar.max().values)
        antar.append(max_value)
        
        pr_antar_date = pr_antar.sel(time = time)
        pr_ar_antar_date = pr_antar_date.sel(lon = lon, lat = lat, method="nearest")
        mean_value = float(pr_ar_antar_date.mean().values)
        pr_sum_antar.append(mean_value)
        
        tas_antar_date = tas_antar.sel(time = time)
        tas_ar_antar_date = tas_antar_date.sel(lon = lon, lat = lat, method = "nearest")
        max_value = float(tas_ar_antar_date.max().values)
        tas_max_antar.append(max_value)

    "========= Construction of array event by event ============"
    all_area.append([area])
    vivt_all_mean.append([vivt_mean])
    pr_all_sum.append([pr_sum])
    tas_all_mean.append([tas_mean])

    vivt_mean_ev.append(np.array(vivt_mean).mean())
    area_mean_ev.append(np.array(area).mean())
    vivt_max_ev.append(np.array(vivt_max).max())
    pr_sum_ev.append(np.array(pr_sum).sum())
    tas_mean_ev.append(np.array(tas_mean).mean())
    tas_max_ev.append(np.array(tas_max).max())
    antar_ev.append(np.array(antar).max())
    
    tas_max_antar_ev.append(np.array(tas_max_antar).max())
    pr_sum_antar_ev.append(np.array(pr_sum_antar).sum())

    i += 1


df["area"] = all_area
df["vIVT"] = vivt_all_mean
df["pr"] = pr_all_sum
df["tas"] = tas_all_mean

df["area_mean"] = area_mean_ev
df["vIVT_mean"] = vivt_mean_ev
df["vIVT_max"] = vivt_max_ev
df["pr_tot"] = pr_sum_ev
df["pr_tot_antar"] = pr_sum_antar_ev
df["tas_mean"] = tas_mean_ev
df["tas_max"] = tas_max_ev
df["tas_max_antar"] = tas_max_antar_ev
df["antar"] = antar_ev


df['df_end'] = df.ar_end.astype('datetime64[s]')
df['df_begin'] = df.ar_begin.astype('datetime64[s]')

df['year'] = pd.DatetimeIndex(df.ar_begin).year
df['month'] = pd.DatetimeIndex(df.ar_begin).month
df['duration'] = df.ar_end - df.ar_begin




out_file = str(sys.argv[5])
df.to_pickle(out_file)

