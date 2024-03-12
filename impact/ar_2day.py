#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 17:20:11 2024

@author: lbarthelemy
"""

import numpy as np          
import xarray as xr 
import sys


f_ar = str(sys.argv[1]) # ar file
out= str(sys.argv[2]) # out file

ar = xr.open_dataset(f_ar)
ar = ar.ar_binary_tag.resample(time="1D").sum() #somme par jour pour avoir les forme d'AR par jour
ar = xr.where(ar > 1, 1, ar) #remise à 1 des zones avec AR

   
v = np.zeros_like(ar.values)
for t in range(len(ar.time)):
   prec_ar = ar.isel(time = t).sum()
   if prec_ar >= 1 and t < len(ar.time) - 1:
      v[t,:,:] = v[t,:,:] + ar.isel(time = t)
      v[t+1,:,:] = v[t+1,:,:] + ar.isel(time = t)
   
ar_2day = xr.Dataset(
   data_vars = dict(
      ar_binary_tag = (["time", "lat", "lon"], v)
      ),
   coords = dict(
      time = ar.time,
      lat = ar.lat,
      lon = ar.lon),
   attrs = dict(description = "impact ar day")
   )

ar_2day = xr.where(ar_2day > 1, 1, ar_2day)
   
ar_2day.to_netcdf(out)
