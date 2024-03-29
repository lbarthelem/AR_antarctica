#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:19:00 2023

@author: lbarthelemy
"""


import sys
import xarray as xr
#import dask

hus = str(sys.argv[1])
va = str(sys.argv[2])
output1 = str(sys.argv[3])
output2 = str(sys.argv[4])

#hus = '/bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245/r1i1p1f1/6hrLev/hus/gr/latest/hus_6hrLev_IPSL-CM6A-LR_ssp245_r1i1p1f1_gr_201501010600-202001010000.nc'
#va = '/bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245/r1i1p1f1/6hrLev/va/gr/latest/va_6hrLev_IPSL-CM6A-LR_ssp245_r1i1p1f1_gr_201501010600-202001010000.nc'

print('hus: ' + hus)
print('va: ' + va)
print('output vIVT: ' + output1)
print('output IWV: ' + output2)

#read dateset
ds = xr.open_dataset(hus)#,chunks={'time':100})#, 'lat':20, 'lon':20})
ds2 = xr.open_dataset(va)#,chunks={'time':100})#, 'lat':20, 'lon':20})


#check the level name

try:
   l = ds.lev
   lev = 'lev'
   

except AttributeError:
   l = ds.presnivs
   lev = 'presnivs'
   
print(lev)

# compute delta_Pi 'dp', convert to float64 to float32
# 'klevp1' coordinate for layer interface
dp_b = ds.b.diff('klevp1').astype('float32') * -1
dp_ap = ds.ap.diff('klevp1').astype('float32') * -1
dp = dp_b * ds.ps + dp_ap


# convert dimensions to 'presnivs' (model levels)
dp = dp.assign_coords(klevp1 = l.values)
dp = dp.rename({'klevp1':str(lev)})  


# Multiply by weights and integrate
# v * q (yields vapor mass flux in kg/s/m)
vq_int = (ds.hus * dp * ds2.va).sum(lev) / 9.81  #here to
vq_int.name="vIVT"

#vivt = vq_int.load()

#IWV
IWV = (ds.hus * dp).sum(lev) / 9.81
IWV.name = "IWV"

iwv = IWV.load()

# Save to file
vq_int.to_netcdf(output1)
iwv.to_netcdf(output2)


