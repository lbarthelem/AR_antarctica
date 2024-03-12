#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 25 16:06:50 2022

@author: leonard
"""
import numpy as np
import xarray as xr
import pandas as pd
import sys


#read arg path
coef_iwv = str(sys.argv[1])
vivt_hist = str(sys.argv[2])
output = str(sys.argv[3])



df = pd.read_csv(coef_iwv)
ds = xr.open_dataset(vivt_hist)


#set the time index of coef iwv
df.time = pd.to_datetime(df.time, format='%Y')
df.set_index(df.time.dt.year, drop = True, inplace = True)
df.time = pd.to_datetime(df.time)


#compute the 98th percentile of negative vivt hist values  
perc = ds.vIVT * -1
    
perc = perc.where(perc > 0 , 0)
perc = perc.quantile(0.98, dim = 'time')


#create xarray dataarray of this threshold repeat eact year
perc_year = np.zeros((len(df.time), len(perc.lat.values), len(perc.lon.values)))

for i in range(len(df.time)):
    perc_year[i,:,:] = perc.values

ds_perc = xr.DataArray(data = perc_year, 
                   dims = ["year",'lat', 'lon'], 
                   coords = dict(
                       year = df.index.to_numpy(),
                       lat = perc.lat,
                       lon = perc.lon),
               
                   name = 'vIVT_98')

# create dataarray of coef iwv 
var = xr.DataArray(data = df['varIWV'].to_numpy(), 
                   dims = ["year"], 
                   coords = dict(
                       year = df.index.to_numpy()),
                   name = 'vIVT_threshold')


#compute varitive threshold
threshold = ds_perc * var


#create final dataset
final = xr.Dataset(
    data_vars = dict(
        vIVT_threshold = (["year", "lat", "lon"], np.array(threshold))
        ),
    coords = dict(
        lon = ds.lon, 
        lat = ds.lat, 
        year = var.year)
    )

#write dataset in output
final.to_netcdf(output)
