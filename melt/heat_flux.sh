#!/bin/bash

simu_55=(r2i1p1f1 r3i1p1f1 r4i1p1f1 r6i1p1f1 r14i1p1f1 r22i1p1f1)
simu_100=(r1i1p1f1 r5i1p1f1 r10i1p1f1 r11i1p1f1)
sim2=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)

l_flux=(hfss hfls rlds rlus rsds rsus)

for simu in ${simu_55[@]}; do
   echo $simu
   for flux in ${l_flux[@]}; do
      echo $flux
      cdo sellonlatbox,-180,180,-90,-55 -selyear,2015/2054 /bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245/$simu/day/$flux/gr/latest/* /scratchu/lbarthelemy/sflux/ssp245/${flux}/${flux}_ssp245_$simu.nc
   done
done

for simu in ${simu_100[@]}; do
   echo $simu
   for flux in ${l_flux[@]}; do
      echo $flux
      cdo sellonlatbox,-180,180,-90,-55 -selyear,2015/2100 /bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245/$simu/day/$flux/gr/latest/* /scratchu/lbarthelemy/sflux/ssp245/${flux}/${flux}_ssp245_$simu.nc
   done
done


for simu in ${sim2[@]}; do
   echo $simu
   for flux in ${l_flux[@]}; do
      echo $flux
      cdo sellonlatbox,-180,180,-90,-55 -selyear,1995/2014 /bdd/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/$simu/day/$flux/gr/latest/* /scratchu/lbarthelemy/sflux/hist/${flux}/${flux}_hist_$simu.nc
   done
done
