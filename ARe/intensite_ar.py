import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
import sys
import matplotlib.pyplot as plt


#file count have to be in .pkl
file_count = str(sys.argv[1])
#file_count = '/data/lbarthelemy/publi_03_2023/ssp245/count_ar/seuil_var/count_ssp245_seuil_var_r22i1p1f1.pkl'
df = pd.read_pickle(file_count)


#file vIVT in .nc
vivt_file = str(sys.argv[2])
#vivt_file = '/scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245_r22i1p1f1.nc'
vivt = xr.open_dataset(vivt_file).vIVT
#vivt = vivt * -1
#vivt = vivt.where(vivt > 0)


#file precip  in .nc
pr_file = str(sys.argv[3])
#pr_file = '/scratchu/lbarthelemy/pr/ssp245/pr_6hr_mm_ssp245_r22i1p1f1.nc'
pr = xr.open_dataset(pr_file).pr

#file tas in .nc
tas_file = str(sys.argv[4])
#tas_file = '/data/lbarthelemy/cmip6_temp/ssp245/tas_ssp245_r22i1p1f1.nc'
tas = xr.open_dataset(tas_file).tas


#file land_mask
land_mask_file = '/data/lbarthelemy/land_mask/antartica_mask_IPSL-CM6A-LR.nc'
land_mask = xr.open_dataset(land_mask_file).land_mask
lat_ant = land_mask.where(land_mask == 1, drop = True).lat.values
lon_ant = land_mask.where(land_mask == 1, drop = True).lon.values
land_mask_vivt = land_mask.sel(lat = vivt.lat, method = 'nearest')



#pr and tas Antarctica
pr_antar = pr.sel(lon = lon_ant, lat= lat_ant, method = 'nearest')
tas_antar = tas.sel(lon = lon_ant, lat= lat_ant, method = 'nearest')
vivt_antar = vivt.sel(lon = lon_ant, lat= lat_ant, method = 'nearest')
vivt = vivt.assign_coords({"lat":land_mask_vivt.lat.values})
vivt_antar = vivt.where(land_mask == 1)




#areacella
area_file = '/scratchu/lbarthelemy/areacella/areacella_fx_IPSL-CM6A-LR_historical.nc'
areacella = xr.open_dataset(area_file).areacella
areacella = areacella.assign_coords({"lat":land_mask.lat.values})
areacella_ant = areacella.where(land_mask == 1)
#%%
def sel_and_compute(coords, ds, compute = 'mean'):
    """
    Parameters
    ----------
    coords : list
        list of paired lon lat to select.
    ds : xarray dataarray
        data what we want to crop at the ar ev shape.
    compute: string
        type of computation on the selected lon/lat

    Returns
    -------
    return_val : float
        value of the ar select

    """
    selected_values = []
    for lat, lon in coords:
        value = ds.sel(lat = lat, lon = lon, method = 'nearest').values.astype(float)
        selected_values.append(value)
    df = pd.DataFrame(selected_values, columns=['value'])
    
    if compute == 'mean':
        return_val = df.value.mean()
    
    if compute == 'max':
        return_val = df.value.max()
        
    if compute == 'min':
        return_val = df.value.min()
        
    if compute == 'sum':
        return_val = df.value.sum()
    
    return (return_val)



#%%
all_area = []       # area of each time of all the ARs events
all_area_ant = []   # area in antarctica of each time of all the ARs events
vivt_all_mean = []  # vIVT mean of each time of all the ARs events
pr_all_sum = []     # pr sum of each time of all the Ars events
tas_all_mean = []   # tas mean of each time of all the ARs events

vivt_mean_ev = []     # vIVT mean of all the ARs events
area_mean_ev = []     # area mean of all the ARs events
area_mean_ev_ant = [] # area  mean in antarctica of all the ARs events
vivt_max_ev = []      # vIVT max of all the ARs events
pr_sum_ev = []        # sum of pr for each events
tas_mean_ev = []      # tas mean of all the ARs events
tas_max_ev = []       # tas max of all the ARs events
antar_ev = []         # 1 if event touch antarctica
tas_max_antar_ev = [] # tas max of all the ARs events in antarctica
pr_sum_antar_ev = []  # pr sum of all the ARs events in antarctica
vivt_max_antar_ev = []# vivt max of all the ARs events in antarctica
vivt_mean_antar_ev = []# vivt mean of all the ARs events in antarctica


i = 0 # indice of event

#geod = Geod('+a=6378137 +f=0.0033528106647475126') # for computing area with pyproj

for ev in df.time_ar:
    area = []           #successive area of the event
    area_ant = []       #successive area of the event in antarctica
    vivt_mean = []      #successive vIVT mean of the event
    vivt_max = []       #successive vIVT max of the event
    tas_mean = []       #successive tas mean of the event
    tas_max = []        #successive tas max of the event
    pr_sum = []         #successive sum of pr of the event
    antar = []          #successive touch of antarctica
    tas_max_antar = []  #successive tas max in antarctica of the event
    pr_sum_antar = []   #successive sum of pr in antarctica of the event
    vivt_max_antar = []  #successive vivt max in antarctica of the event
    vivt_mean_antar = []  #successive vivt mean in antarctica of the event
    
    
    if type(ev) is list:
        j = 0           # indice of time in the event

        for time in ev:
            
            print(time)
            lon = df.ar_pos[i][j][:,1]
            lat = df.ar_pos[i][j][:,0]
            coords = df.ar_pos[i][j]

            "============= compute area if more than 1 time step =============="
            #poly_area, poly_perimeter = geod.polygon_area_perimeter(lon, lat)
            area_ev = sel_and_compute(coords, areacella, 'sum') #m2
            area.append(area_ev)
            
            area_ev_ant = sel_and_compute(coords, areacella_ant, 'sum') #m2
            area_ant.append(area_ev_ant)
            "============= compute vIVT mean if more than 1 time step =============="
            vivt_date = vivt.sel(time = time)
            #vivt_ar = vivt_date.sel(lon = lon, lat = lat, method="nearest")
            #mean_value = float(vivt_ar.mean().values)
            #max_value = float(vivt_ar.min().values)
            mean_value = sel_and_compute(coords, vivt_date, 'mean')
            max_value = sel_and_compute(coords, vivt_date, 'min')
            vivt_mean.append(mean_value)
            vivt_max.append(max_value)
            
            pr_date = pr.sel(time = time)
            #pr_ar = pr_date.sel(lon = lon, lat = lat, method = 'nearest')
            #sum_value = float(pr_ar.sum().values)
            sum_value = sel_and_compute(coords, pr_date, 'sum')
            pr_sum.append(sum_value)
            
            tas_date = tas.sel(time = time)
            #tas_ar = tas_date.sel(lon = lon, lat = lat, method = 'nearest')
            #mean_value = float(tas_ar.mean().values)
            #max_value = float(tas_ar.max().values) 
            mean_value = sel_and_compute(coords, tas_date, 'mean')
            max_value = sel_and_compute(coords, tas_date, 'max') 
            tas_mean.append(mean_value)
            tas_max.append(max_value)

            #ar_antar = land_mask.sel(lon = lon, lat = lat, method="nearest")
            max_value = sel_and_compute(coords, land_mask, 'max')
            antar.append(max_value)
            
            pr_antar_date = pr_antar.sel(time = time)
            sum_value = sel_and_compute(coords, pr_antar_date, 'sum')
            pr_sum_antar.append(sum_value)
            
            tas_antar_date = tas_antar.sel(time = time) 
            max_value = sel_and_compute(coords, tas_antar_date, 'max') 
            tas_max_antar.append(max_value)
            
            vivt_antar_date = vivt_antar.sel(time = time)
            mean_value = sel_and_compute(coords, vivt_antar_date, 'mean')
            max_value = sel_and_compute(coords, vivt_antar_date, 'min')
            vivt_max_antar.append(max_value)
            vivt_mean_antar.append(mean_value)


            j += 1


    else:
        time = ev
        lon = df.ar_pos[i][:,1]
        lat = df.ar_pos[i][:,0]
        coords = df.ar_pos[i]

        "============= compute area if only 1 time step =============="
        area_ev = sel_and_compute(coords, areacella, 'sum') #m2
        area.append(area_ev)
        
        area_ev_ant = sel_and_compute(coords, areacella_ant, 'sum') #m2
        area_ant.append(area_ev_ant)

        "============= compute vIVT mean if only 1 time step =============="
        vivt_date = vivt.sel(time = ev)
        #vivt_ar = vivt_date.sel(lon = lon, lat = lat, method="nearest")
        #mean_value = float(vivt_ar.mean().values)
        #max_value = float(vivt_ar.min().values)
        mean_value = sel_and_compute(coords, vivt_date, 'mean')
        max_value = sel_and_compute(coords, vivt_date, 'min')
        vivt_mean.append(mean_value)
        vivt_max.append(max_value)
        
        pr_date = pr.sel(time = ev)
        #pr_ar = pr_date.sel(lon = lon, lat = lat, method = 'nearest')
        #sum_value = float(pr_ar.sum().values)
        sum_value = sel_and_compute(coords, pr_date, 'sum')
        pr_sum.append(sum_value)
        
        tas_date = tas.sel(time = ev)
        #tas_ar = tas_date.sel(lon = lon, lat = lat, method = 'nearest')
        #mean_value = float(tas_ar.mean().values)
        #max_value = float(tas_ar.max().values) 
        mean_value = sel_and_compute(coords, tas_date, 'mean')
        max_value = sel_and_compute(coords, tas_date, 'max') 
        tas_mean.append(mean_value)
        tas_max.append(max_value)

        #ar_antar = land_mask.sel(lon = lon, lat = lat, method="nearest")
        max_value = sel_and_compute(coords, land_mask, 'max')
        antar.append(max_value)
        
        pr_antar_date = pr_antar.sel(time = ev)
        sum_value = sel_and_compute(coords, pr_antar_date, 'sum')
        pr_sum_antar.append(sum_value)
        
        tas_antar_date = tas_antar.sel(time = ev) 
        max_value = sel_and_compute(coords, tas_antar_date, 'max') 
        tas_max_antar.append(max_value)
        
        vivt_antar_date = vivt_antar.sel(time = time)
        mean_value = sel_and_compute(coords, vivt_antar_date, 'mean')
        max_value = sel_and_compute(coords, vivt_antar_date, 'min')
        vivt_max_antar.append(max_value)
        vivt_mean_antar.append(mean_value)
        
        

    "========= Construction of array event by event ============"
    all_area.append([area])
    all_area_ant.append([area_ant])
    vivt_all_mean.append([vivt_mean])
    pr_all_sum.append([pr_sum])
    tas_all_mean.append([tas_mean])

    vivt_mean_ev.append(np.nanmean(np.array(vivt_mean)))
    area_mean_ev.append(np.nanmean(np.array(area)))
    area_mean_ev_ant.append(np.nanmax(np.array(area_ant)))
    vivt_max_ev.append(np.nanmean(np.array(vivt_max)))   #moyenne des max
    pr_sum_ev.append(np.array(pr_sum).sum())
    tas_mean_ev.append(np.nanmean(np.array(tas_mean)))
    tas_max_ev.append(np.nanmax(np.array(tas_max)))
    antar_ev.append(np.nanmax(np.array(antar)))
    
    tas_max_antar_ev.append(np.nanmax(np.array(tas_max_antar)))
    pr_sum_antar_ev.append(np.array(pr_sum_antar).sum())
    vivt_max_antar_ev.append(np.nanmean(np.array(vivt_max_antar)))
    vivt_mean_antar_ev.append(np.nanmean(np.array(vivt_mean_antar)))
    i += 1
#%%

df["area"] = all_area
df["vIVT"] = vivt_all_mean
df["pr"] = pr_all_sum
df["tas"] = tas_all_mean

df["area_mean"] = area_mean_ev
df["area_mean_ant"] = area_mean_ev_ant
df["vIVT_mean"] = vivt_mean_ev
df["vIVT_max"] = vivt_max_ev
df["pr_tot"] = pr_sum_ev
df["pr_tot_antar"] = pr_sum_antar_ev
df["tas_mean"] = tas_mean_ev
df["tas_max"] = tas_max_ev
df["tas_max_antar"] = tas_max_antar_ev
df["vivt_max_antar"] = vivt_max_antar_ev
df["vivt_mean_antar"] = vivt_mean_antar_ev
df["antar"] = antar_ev


df['df_end'] = df.ar_end.astype('datetime64[s]')
df['df_begin'] = df.ar_begin.astype('datetime64[s]')

df['year'] = pd.DatetimeIndex(df.ar_begin).year
df['month'] = pd.DatetimeIndex(df.ar_begin).month
df['duration'] = df.ar_end - df.ar_begin


#out_file = '/scratchu/lbarthelemy/test_intensite.pkl'

out_file = str(sys.argv[5])
df.to_pickle(out_file)
#%%




