#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 14:30:13 2025

@author: lbarthelemy
"""

from netCDF4 import Dataset
import numpy as np
import netCDF4 as nc
import sys
import xarray as xr


# File with output grid, and land mask (if needed)
file_out_grid = "/data/lbarthelemy/vertical_integral/CMIP6-present/full_mask/land_mask_LR_CMIP6.nc"
fh = Dataset(file_out_grid, mode='r',format="NETCDF4")

# Define some output dimensions
lat_out = fh.variables['latitude'][:]
lon_out = fh.variables['longitude'][:]

lon_out = lon_out - 180. # If going from 0 - 360 to -180 180 is needed

# size of lon/lat array
nlon = lon_out.size
nlat = lat_out.size

#output grid
lon_out_2d,lat_out_2d = np.meshgrid(lon_out,lat_out)
lat_out_orig,lon_out_orig = lat_out_2d[0,0],lon_out_2d[0,0]
lat_out_step = lat_out_2d[1,0] - lat_out_2d[0,0]
lon_out_step = lon_out_2d[0,1] - lon_out_2d[0,0]



# Read file
file_in = str(sys.argv[1]) 
threshold_in = str(sys.argv[2])
output = str(sys.argv[3])
threshold_type = str(sys.argv[4])

# Read in data
# restrict to the latitude range of consideration if needed
# input coordinates
fh1 = Dataset(file_in, mode='r',format="NETCDF4")
lat_in = fh1.variables['lat'][:]
lon_in = fh1.variables['lon'][:]
res_lon = lon_in[1] - lon_in[0]
res_lat = np.abs(lat_in[1] - lat_in[0])
# input data
ivt_full = fh1.variables['vIVT'][:]
# Change sign and keep only positive values (southward flux)
ivt = ivt_full[:]   
ivt = ivt * -1
ivt[ivt < 0] = 0
# input times (for output) 
time_out = fh1.variables['time'][:] 
time_units=fh1.variables['time'].units 
ntime = time_out.size
try :
    cal = fh1.variables['time'].calendar 
except AttributeError : 
	# Attribute doesnt exist
    cal = 'standard' 
datevar=(nc.num2date(time_out,units=time_units,calendar=cal))

fh1.close()

# initiations for the algorithm
ar_binary_tag = np.zeros((len(time_out),nlat,nlon)) #final output
lat_index_list = []
lon_index_list = []

time_98 = []
y_98 = []
x_98 = []

# Threshold selection

# Fixed threshold, computed on the vIVT ensemble for each month
if threshold_type == 'fixed':
    th = Dataset(threshold_in, mode = 'r', format = "NETCDF4")
    ivt_seuil = th.variables['vIVT'][:]
    ivt_seuil = ivt_seuil[:]
    ivt_seuil = ivt_seuil * -1
    ivt_seuil[ivt_seuil < 0] = 0
    ivt_per  = np.percentile(ivt_seuil, 98, axis=0)
    th.close()  
    
    indices_98 = np.where(ivt > ivt_per)
    time_98 = indices_98[0] 
    y_98 = lat_in[indices_98[1]]
    x_98 = lon_in[indices_98[2]]
    
    

# some file haven't the same time lenth and the number of day changes between month
# so we need to reconstruct the day number per yer for .
if threshold_type == 'adaptive':
    mon = threshold_in[-5:-3]

    ds = xr.open_dataset(file_in)
    time_array = ds.time
    time_array = time_array.to_dataframe()


    nb_day = time_array.groupby(time_array.index.year).count()
    beg = []
    end = [] 
    # first year of the dataset
    f_year = 'yes'
    j = 0
    for i in nb_day.time:
        if f_year == 'yes':
            beg.append(0)
            end.append(i - 1)
            f_year = 'no'
        else:
            beg.append(end[j - 1] + 1)
            end.append(beg[j] + i - 1)
    
        j += 1
    
    nb_day['beg'] = beg
    nb_day['end'] = end
        
    
    threshold = xr.open_dataset(threshold_in)
    threshold = threshold.vIVT_threshold
    
    if mon == '01':
        for year in nb_day.index[:-1]:
            threshold_year = np.array(threshold.sel(year = year))
            ivt_month = ivt[nb_day.beg[year]:nb_day.end[year]]
            indice_98_year = np.array(np.where(ivt_month > threshold_year))
            time_98.extend(indice_98_year[0] + nb_day.beg[year])
            
            y_98.extend(indice_98_year[1])
            x_98.extend(indice_98_year[2])
            
    else:
        for year in nb_day.index:
            threshold_year = np.array(threshold.sel(year = year))
            ivt_month = ivt[nb_day.beg[year]:nb_day.end[year]]
            indice_98_year = np.array(np.where(ivt_month > threshold_year))
            time_98.extend(indice_98_year[0] + nb_day.beg[year])
            
            y_98.extend(indice_98_year[1])
            x_98.extend(indice_98_year[2])

timesteps = np.arange(0,len(ivt[:,0,0]))

# --- Loop over all original timesteps ---
for timestep in timesteps:

    #print(time_array.index[timestep])
    # Find indices above 98th percentile for the given timestep  
    timestep_idx = np.where(timestep == time_98)[0]
    #print(timestep_idx)
    # Corresponding latitudes and longitudes
    x_idx = x_98[timestep_idx]
    
    y_idx = y_98[timestep_idx]
    
    # Split in groups continuous in latitude 
    split_loc = np.where(np.abs(np.diff(y_idx)) > res_lat)
    y_splitted_temp = np.split(y_idx, split_loc[0] +1)
    x_splitted_temp = np.split(x_idx, split_loc[0] +1)

    # Pick the group with the most points 
    # (not necessarily the largest latitude range...)
    y_longest = max(y_splitted_temp, key=len)
    x_longest = max(x_splitted_temp, key=len)

    # Sort that group by longitude (x_reverse, y_reverse)
    # latitude still increasing for each longitude
    x_reverse = [] # New longitudes and latitudes
    y_reverse = [] # for the chosen latitude group

    try:
        # test if latitude range at least 20 degrees
        if y_longest.max() - y_longest.min() > 20 :
            # List of grid longitudes in longitude range.
            reverse_grid = np.arange(min(x_longest),max(x_longest)+res_lon/2.,res_lon)
            # sort by longitude
            for i in reverse_grid: # i is a longitude
                x_index_reverse = np.where(np.abs(x_longest - i) < 1e-2)
                x_reverse = np.concatenate((x_reverse,x_longest[x_index_reverse]))
                y_reverse = np.concatenate((y_reverse,y_longest[x_index_reverse]))

    except ValueError:
        pass
	
    # Split into groups if more than 20 degrees of longitude difference.
    split_loc = np.where(np.diff(x_reverse) > 20) 
    x_splitted = np.split(x_reverse, split_loc[0] +1)
    y_splitted = np.split(y_reverse, split_loc[0] +1) 

    # Incorrect split if one group wraps around 360 / 180
    # Try to correct : move first group at the end in needed.
    try:
        if x_splitted[0][0]+360 - x_splitted[-1][-1] < 20:
            x_splitted[-1] = np.concatenate((x_splitted[-1],x_splitted[0]))
            # ! deprecated x_splitted = np.delete(x_splitted,0,0)
            x_splitted = x_splitted[1:]

            y_splitted[-1] = np.concatenate((y_splitted[-1],y_splitted[0]))
            y_splitted = y_splitted[1:]

    except IndexError:
        pass		

    # Now, check again that each lon group / AR has enough latitude extension,
    # And save the shapes for that timestep
    x_shape = [] # AR latitudes and longitudes
    y_shape = [] # for the given timestep

    x_shape_landfall = []
    y_shape_landfall = []

    # --- loop over longitude groups ---
    for i in range(0,len(y_splitted)):
        x_reverse2 = [] # Re-sorted lon, lats 
        y_reverse2 = [] # for each longitude group

        x_final = [] # "final" lat / lon accepeted
        y_final = [] # for each longitude group

        # sort back each lon group / AR by latitude
        try:	
            # range of possible latitudes
            reverse_grid2 = np.arange(max(y_splitted[i]),min(y_splitted[i])-0.5,res_lat*-1)
            # sort by latitude
            for j in reverse_grid2:
                y_index_reverse2 = np.where(np.abs(y_splitted[i] -  j)<1e-2)
                x_reverse2 = np.concatenate((x_reverse2,x_splitted[i][y_index_reverse2]))
                y_reverse2 = np.concatenate((y_reverse2,y_splitted[i][y_index_reverse2]))

        except ValueError:
            pass

        # Split again if not continuous in latitude
        try:
            split_loc = np.where(np.abs(np.diff(y_reverse2)) > res_lat)
            y_splitted_final = np.split(y_reverse2, split_loc[0] +1)
            x_splitted_final = np.split(x_reverse2, split_loc[0] +1)

            # For each final group, test the latitude extent.
            for z in range(0,len(y_splitted_final)):
                if y_splitted_final[z].max() - y_splitted_final[z].min() > 20:
                    y_final = np.concatenate((y_final, y_splitted_final[z]))
                    x_final = np.concatenate((x_final, x_splitted_final[z]))

            # Add to the AR shapes if any found
            x_shape = np.concatenate((x_shape,x_final))
            y_shape = np.concatenate((y_shape,y_final))
            
		
        except ValueError:
            pass
    # --- End loop over longitude groups ---

    # Convert latitudes, longitudes back to indices
    # add 0.5 to prevent error in rounding (116.9995 becoming 116 not 117...)
    lat_index = (y_shape - lat_out_orig) / lat_out_step + 0.5 * np.abs(res_lat / lat_out_step) 
    lon_index = (x_shape - lon_out_orig) / lon_out_step + 0.5 * res_lon / lon_out_step
    lat_index = lat_index.astype(int)
    lon_index = lon_index.astype(int)

    if(len(lat_index) > 0):
        lat_index_list.append(lat_index.data)
    else:
        lat_index_list.append(lat_index)

    if(len(lon_index) > 0):
        lon_index_list.append(lon_index.data)
    else:
        lon_index_list.append(lon_index)
    
    ar_binary_tag[timestep,lat_index,lon_index] = 1

# --- End timestep loop ---

# Define and save output file
file_out_tag = output
f1 = nc.Dataset(file_out_tag,'w', format='NETCDF4')
f1.createDimension('time')	
f1.createDimension('lon', nlon)
f1.createDimension('lat', nlat)
ar_time = f1.createVariable('time', 'f8', 'time')
ar_lat = f1.createVariable('lat', 'f8', 'lat')
ar_lon = f1.createVariable('lon', 'f8', 'lon')
ar_ar_binary_tag = f1.createVariable('ar_binary_tag', 'i1', ('time', 'lat', 'lon'))
ar_time[:] = time_out
ar_lon[:] = lon_out
ar_lat[:] = lat_out
ar_ar_binary_tag[:,:,:] = ar_binary_tag[:,:,:]
f1.description = "ARTMIP file format (Ullrich)"
ar_time.calendar = 'standard'
ar_time.long_name = 'time'
ar_time.standard_name = 'time'
ar_time.units = time_units

ar_lat.units = 'degrees_north'
ar_lat.long_name = 'latitude'
ar_lat.standard_name = 'latitude'
ar_lat.axis = 'Y'
ar_lon.units = 'degrees_east'
ar_lon.axis = 'X'
ar_lon.long_name = 'longitude'
ar_lon.standard_name = 'longitude'
ar_ar_binary_tag.scheme = 'Wille_vIVT_2019'
ar_ar_binary_tag.description = 'Binary indicator of atmospheric river using vIVT'
ar_ar_binary_tag.version = '2.4'
ar_ar_binary_tag.credits = 'Developed by Léonard Barthelemy from Jonathan D. Wille, Ambroise Dufour, Jai Chowdhry Beeman, and Vincent Favier'
f1.close()