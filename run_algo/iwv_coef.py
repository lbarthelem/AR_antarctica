#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 25 16:06:50 2022

@author: leonard
"""
import numpy as np
import pandas as pd
import xarray as xr
import sys


#read arg path
glob_mean = str(sys.argv[1])
yearly_mean = str(sys.argv[2])
output = str(sys.argv[3])


ds_glob_mean = xr.open_dataset(glob_mean)
ds_yearly_mean = xr.open_dataset(yearly_mean).IWV

#create global mean in time serie from yearly file
time = ds_yearly_mean.time.dt.year
s = len(time.values)
global_IWV = np.repeat(ds_glob_mean.IVW.values[:,:,:],s, axis = 0)


ds_glob_mean = xr.Dataset(
    data_vars = dict(
        IWV = (["time","lat", "lon"], global_IWV)),
    coords = dict(
        time = np.arange(0,s),
        lat = ds_glob_mean.lat,
        lon = ds_glob_mean.lon
        )
    )

ds_yearly_mean = xr.Dataset(
    data_vars = dict(
        IWV = (["time","lat", "lon"], ds_yearly_mean.values)),
    coords = dict(
        time = np.arange(0,s),
        lat = ds_yearly_mean.lat,
        lon = ds_yearly_mean.lon
        )
    )


#compute iwv_year/iwv_clim_hist
ds_var = ds_yearly_mean.IWV / ds_glob_mean.IWV

#linear regresion
c_reg = ds_var.polyfit(dim = 'time', deg = 1, )
slope = np.repeat(c_reg.polyfit_coefficients[0,:,:].drop('degree').values[:,:,np.newaxis],s, axis = 2)
intercept = np.repeat(c_reg.polyfit_coefficients[1,:,:].drop('degree').values[:,:,np.newaxis],s, axis = 2)

#create ntcdf whith all the linear reg per points
final_reg = slope * np.arange(0,s) + intercept
final_reg = np.transpose(final_reg, (2,0,1))

ds_reg = xr.Dataset(
    data_vars = dict(
        varIWV = (["time","lat", "lon"], final_reg)),
    coords = dict(
        time = time,
        lat = ds_glob_mean.lat,
        lon = ds_glob_mean.lon
        )
    )

#compute the spatial mean of this reg
ds_reg = ds_reg.varIWV.mean(dim =['lon','lat'] ).to_dataframe()

#write file in .csv
ds_reg.to_csv(output)

