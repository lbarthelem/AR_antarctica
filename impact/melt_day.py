#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:40:12 2023

@author: leonard
"""

import xarray as xr
import numpy as np

sim_h = ['r1i1p1f1','r2i1p1f1','r3i1p1f1','r4i1p1f1','r5i1p1f1','r6i1p1f1','r7i1p1f1','r8i1p1f1','r9i1p1f1','r10i1p1f1']
sim_f = ['r1i1p1f1','r2i1p1f1','r3i1p1f1','r4i1p1f1','r5i1p1f1','r6i1p1f1','r10i1p1f1','r11i1p1f1','r14i1p1f1','r22i1p1f1']

#T2m treshold to define day melt
tlim = 272

#loop over historical member
for h in sim_h:

   #day with tas > -1°C
   file = '/scratchu/lbarthelemy/temp_day/hist/daymean_tas_hist_'+ h + '.nc'
   print(file)
   file_ant = '/data/lbarthelemy/land_mask/antartica_mask_IPSL-CM6A-LR.nc'

   ant = xr.open_dataset(file_ant).land_mask
   df = xr.open_dataset(file).tas.sel(time = slice('1995-01-01', '2014-12-31'))
   
   #df = df.isel(time = slice(1826, 9131))

   ant= ant.isel(lat = slice(40))
   ant = ant.assign_coords(lat = ('lat', df.lat.values))

   df = df.where(ant == 1)
   df_tas = xr.where(df>tlim, 1, 0)



   df_tas.to_netcdf('/scratchu/lbarthelemy/temp_day/hist/day_melt/day_taspos_hist_'+ h +'_v2.nc')

   #day with sflux > 0:
   file = '/scratchu/lbarthelemy/sflux/hist/flux_hist_'+ h +'.nc'
   print(file)

   ant = xr.open_dataset(file_ant).land_mask
   df = xr.open_dataset(file).d_flux

   ant= ant.isel(lat = slice(28))
   ant = ant.assign_coords(lat = ('lat', df.lat.values))

   df = df.where(ant == 1)
   df_flux = xr.where(df>=0, 1, 0)

   df_flux.to_netcdf('/scratchu/lbarthelemy/temp_day/hist/day_melt/day_sfluxpos_hist_'+ h +'_v2.nc')
   df_flux = df_flux.assign_coords(time = ('time', df_tas.time.values))


   day_melt = df_tas + df_flux
   day_melt = xr.where(day_melt == 2, 1, np.nan)
   day_melt = day_melt.rename('melt_day')
   day_melt.attrs['temperature_threshold'] = str(tlim) + '°K'
   day_melt.to_netcdf('/scratchu/lbarthelemy/temp_day/hist/day_melt/day_melt_hist_'+ h +'_v2.nc')



#loop over futur member
for f in sim_f:

   #day with tas > -1°C
   file = '/scratchu/lbarthelemy/temp_day/ssp245/daymean_tas_ssp245_'+ f + '.nc'
   print(file)
   file_ant = '/data/lbarthelemy/land_mask/antartica_mask_IPSL-CM6A-LR.nc'

   ant = xr.open_dataset(file_ant).land_mask
   df = xr.open_dataset(file).tas
   #df = df.isel(time = slice(7305, 14610))

   ant= ant.isel(lat = slice(32))
   ant = ant.assign_coords(lat = ('lat', df.lat.values))

   df = df.where(ant == 1)
   df_tas = xr.where(df>tlim, 1, 0)


   df_tas.to_netcdf('/scratchu/lbarthelemy/temp_day/ssp245/day_melt/day_taspos_ssp245_'+ f +'_v2.nc')

   #day with sflux > 0:
   file = '/scratchu/lbarthelemy/sflux/ssp245/flux_ssp245_'+ f +'.nc'
   print(file)

   ant = xr.open_dataset(file_ant).land_mask
   df = xr.open_dataset(file).d_flux
   time0 = df.time.isel(time = 0).values
   time1 = df.time.isel(time = -1).values

   df_tas = df_tas.sel(time = slice(time0, time1))

   ant= ant.isel(lat = slice(28))
   ant = ant.assign_coords(lat = ('lat', df.lat.values))

   df = df.where(ant == 1)
   df_sflux = xr.where(df>=0, 1, 0)


   df_sflux.to_netcdf('/scratchu/lbarthelemy/temp_day/ssp245/day_melt/day_sfluxpos_ssp245_'+ f +'_v2.nc')
   df_sflux = df_sflux.assign_coords(time = ('time', df_tas.time.values))


   day_melt = df_tas + df_sflux
   day_melt = xr.where(day_melt == 2, 1, 0)
   day_melt = day_melt.rename('melt_day')
   day_melt.attrs['temperature_threshold'] = str(tlim) + '°K'

   day_melt.to_netcdf('/scratchu/lbarthelemy/temp_day/ssp245/day_melt/day_melt_ssp245_'+ f +'_v2.nc')
