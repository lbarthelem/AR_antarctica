#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 16:16:00 2023

@author: lbarthelemy
"""
import numpy as np           
import xarray as xr 
import sys


#path 
ar_path = str(sys.argv[1])
precip_tot_path = str(sys.argv[2])
snow_path = str(sys.argv[3])
rain_path = str(sys.argv[4])
output1 = str(sys.argv[5])
output2 = str(sys.argv[6])


#open netcdf and good format in lat and time
ar = xr.open_dataset(ar_path)
ar = ar.drop_isel(time = -1)
ar = ar.ar_binary_tag.isel(lat = np.arange(0,42))


pr_tot = xr.open_dataset(precip_tot_path).pr.isel(time = np.arange(0, len(ar.time))).values
snow = xr.open_dataset(snow_path).isel(time = np.arange(0, len(ar.time))).prsn.values
rain = xr.open_dataset(rain_path).isel(time = np.arange(0, len(ar.time))).pr.values

#create new pr dataset with good lat/lon/time
pr_good_time = xr.Dataset(
    data_vars=dict(
            pr_tot = (['time', "lat", "lon"], pr_tot),
            snow = (['time', "lat", "lon"], snow),
            rain = (['time', "lat", "lon"], rain)
            ),
    coords=dict(
            lon = ar.lon,
            lat = ar.lat,
            time = ar.time
            )
)

pr_ar = xr.where(ar >= 1, pr_good_time, np.nan)

pr_ar.to_netcdf(output1)

contrib_pr = pr_ar.groupby('time.year').sum(dim = 'time') / pr_good_time.groupby('time.year').sum(dim = 'time')
contrib_pr = contrib_pr.mean(dim = 'year') * 100

contrib_pr.to_netcdf(output2)






