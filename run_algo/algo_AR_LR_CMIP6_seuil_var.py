#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 12:22:08 2021

@author: leonard

F. Codron 04/21 : General spring cleaning
    Define separately lat,lon for input and output files.
    (so output of AR tags on any grid)
    Latitudes can be increasing or decreasing (untested for input file)
    correct potential lat / lon rounding error for "reverse" sorting
    correct 0.5° for lat / lon range to res_lat/lon /2 
    correct rounding error for lat/lon to output index (off by 1)
    correct some deprecated constructs
    Add a number of comments.
"""


#from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import numpy as np
import netCDF4 as nc
import sys
import xarray as xr


np.set_printoptions(threshold=sys.maxsize)
#import pdb; pdb.set_trace()
#%%

#Also the AR time index output files have to be changed based on the quadrant/half used

#Read in the 12 files containing the monthly values from 1979_2017

datevar_list = []

# File with output grid, and land mask (if needed)
file_out_grid = "/data/lbarthelemy/vertical_integral/CMIP6-present/full_mask/land_mask_LR_CMIP6.nc"
fh = Dataset(file_out_grid, mode='r',format="NETCDF4")
# Define some output dimensions
lat_out = fh.variables['latitude'][:]
lon_out = fh.variables['longitude'][:]
lon_out = lon_out - 180. # If going from 0 - 360 to -180 180 is needed
nlon = lon_out.size
nlat = lat_out.size
lon_out_2d,lat_out_2d = np.meshgrid(lon_out,lat_out)
lat_out_orig,lon_out_orig = lat_out_2d[0,0],lon_out_2d[0,0]
lat_out_step = lat_out_2d[1,0] - lat_out_2d[0,0]
lon_out_step = lon_out_2d[0,1] - lon_out_2d[0,0]

#timevar = fh.variables['time']

# read file
file_in = str(sys.argv[1]) 
threshold_in = str(sys.argv[2])
output = str(sys.argv[3])

mon = threshold_in[-5:-3]

ds = xr.open_dataset(file_in)
time_array = ds.time
time_array = time_array.to_dataframe()


nb_day = time_array.groupby(time_array.index.year).count()
beg = []
end = []  # first year of the dataset
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
time_units=fh1.variables['time'].units # ! deprecation warning tostring -> tobytes ?
ntime = time_out.size
try :
    cal = fh1.variables['time'].calendar # ! same warning
except AttributeError : 
	# Attribute doesnt exist
    cal = 'standard' 
datevar=(nc.num2date(time_out,units=time_units,calendar=cal))

fh1.close()

# Detection algorithm
# initiations
ar_binary_tag = np.zeros((len(time_out),nlat,nlon))
	#ar_landfall_binary_tag = np.zeros((len(time2),len(lat),len(lon)))
lat_index_list = []
lon_index_list = []
landfall_idx = []

time_98 = []
y_98 = []
x_98 = []

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



time_98 = np.array(time_98)
y_98 = lat_in[np.array(y_98)]
x_98 = lon_in[np.array(x_98)]




#    river_idx = [] not used for now
landfall_idx = []
timesteps = np.arange(0,len(ivt[:,0,0])) # Complicated, why not ntime ?

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
    # !! Attention aux erreurs d'arrondi !
    # use nonzero better than where if only to find indices
    # add 1 because diff removes 1 point.
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
        # Should be elsewhere ? (when choosing group)
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
temp_time = f1.createVariable('time', 'f8', 'time')
temp_lat = f1.createVariable('lat', 'f8', 'lat')
temp_lon = f1.createVariable('lon', 'f8', 'lon')
temp_ar_binary_tag = f1.createVariable('ar_binary_tag', 'i1', ('time', 'lat', 'lon'))
temp_time[:] = time_out
temp_lon[:] = lon_out
temp_lat[:] = lat_out
temp_ar_binary_tag[:,:,:] = ar_binary_tag[:,:,:]
f1.description = "ARTMIP file format (Ullrich)"
temp_time.calendar = 'standard'
temp_time.long_name = 'time'
temp_time.standard_name = 'time'
temp_time.units = time_units

	###temp_time.calendar = timevar.calendar
temp_lat.units = 'degrees_north'
temp_lat.long_name = 'latitude'
temp_lat.standard_name = 'latitude'
temp_lat.axis = 'Y'
temp_lon.units = 'degrees_east'
temp_lon.axis = 'X'
temp_lon.long_name = 'longitude'
temp_lon.standard_name = 'longitude'
temp_ar_binary_tag.scheme = 'Wille_vIVT_2019'
temp_ar_binary_tag.description = 'Binary indicator of atmospheric river using vIVT'
temp_ar_binary_tag.version = '2.4'
temp_ar_binary_tag.credits = 'Developed by Jonathan D. Wille, Ambroise Dufour, Jai Chowdhry Beeman, and Vincent Favier'
f1.close()
