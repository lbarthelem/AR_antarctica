#!/bin/bash

sim2=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)
sim1=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)

for simu in ${sim1[@]}; do
   rlds=/scratchu/lbarthelemy/sflux/hist/rlds/rlds_hist_$simu.nc
   rsds=/scratchu/lbarthelemy/sflux/hist/rsds/rsds_hist_$simu.nc
   hfss=/scratchu/lbarthelemy/sflux/hist/hfss/hfss_hist_$simu.nc
   hfls=/scratchu/lbarthelemy/sflux/hist/hfls/hfls_hist_$simu.nc
   rlus=/scratchu/lbarthelemy/sflux/hist/rlus/rlus_hist_$simu.nc
   rsus=/scratchu/lbarthelemy/sflux/hist/rsus/rsus_hist_$simu.nc

   cdo -O enssum $rlds $rsds /scratchu/lbarthelemy/sflux/hist/d_flux_hist_$simu.nc
   cdo -O enssum $hfss $hfls $rlus $rsus /scratchu/lbarthelemy/sflux/hist/u_flux_hist_$simu.nc
   cdo -O expr,'d_flux=hfss*-1' /scratchu/lbarthelemy/sflux/hist/u_flux_hist_$simu.nc /scratchu/lbarthelemy/sflux/hist/neg_u_flux_hist_$simu.nc
   cdo -O enssum /scratchu/lbarthelemy/sflux/hist/neg_u_flux_hist_$simu.nc /scratchu/lbarthelemy/sflux/hist/d_flux_hist_$simu.nc /scratchu/lbarthelemy/sflux/hist/flux_hist_$simu.nc


#   cdo expr,'down_flux=rlds+rsds' $rlds $rsds /scratchu/lbarthelemy/sflux/hist/d_flux_hist_$simu.nc
#   cdo expr,'up_flux=hfss+hfls+rlus+rsus' $hfss $hfls $rlus $rsus /scratchu/lbarthelemy/sflux/hist/u_flux_hist_$simu.nc
#   cdo expr,'sflux=down_flux-up_flux' /scratchu/lbarthelemy/sflux/hist/d_flux_hist_$simu.nc /scratchu/lbarthelemy/sflux/hist/u_flux_hist_$simu.nc /scratchu/lbarthelemy/sflux/hist/flux_hist_$simu.nc
done


for simu in ${sim2[@]}; do
   rlds=/scratchu/lbarthelemy/sflux/ssp245/rlds/rlds_ssp245_$simu.nc
   rsds=/scratchu/lbarthelemy/sflux/ssp245/rsds/rsds_ssp245_$simu.nc
   hfss=/scratchu/lbarthelemy/sflux/ssp245/hfss/hfss_ssp245_$simu.nc
   hfls=/scratchu/lbarthelemy/sflux/ssp245/hfls/hfls_ssp245_$simu.nc
   rlus=/scratchu/lbarthelemy/sflux/ssp245/rlus/rlus_ssp245_$simu.nc
   rsus=/scratchu/lbarthelemy/sflux/ssp245/rsus/rsus_ssp245_$simu.nc


   cdo -O enssum $rlds $rsds /scratchu/lbarthelemy/sflux/ssp245/d_flux_ssp245_$simu.nc
   cdo -O enssum $hfss $hfls $rlus $rsus /scratchu/lbarthelemy/sflux/ssp245/u_flux_ssp245_$simu.nc
   cdo -O expr,'d_flux=hfss*-1' /scratchu/lbarthelemy/sflux/ssp245/u_flux_ssp245_$simu.nc /scratchu/lbarthelemy/sflux/ssp245/neg_u_flux_ssp245_$simu.nc
   cdo -O enssum /scratchu/lbarthelemy/sflux/ssp245/neg_u_flux_ssp245_$simu.nc /scratchu/lbarthelemy/sflux/ssp245/d_flux_ssp245_$simu.nc /scratchu/lbarthelemy/sflux/ssp245/flux_ssp245_$simu.nc


#   cdo expr,'down_flux=rlds+rsds' $rlds $rsds /scratchu/lbarthelemy/sflux/ssp245/d_flux_ssp245_$simu.nc
#   cdo expr,'up_flux=hfss+hfls+rlus+rsus' $hfss $hfls $rlus $rsus /scratchu/lbarthelemy/sflux/ssp245/u_flux_ssp245_$simu.nc
#   cdo expr,'sflux=down_flux-up_flux' /scratchu/lbarthelemy/sflux/ssp245/d_flux_ssp245_$simu.nc /scratchu/lbarthelemy/sflux/ssp245/u_flux_ssp245_$simu.nc /scratchu/lbarthelemy/sflux/ssp245/flux_ssp245_$simu.nc
done
