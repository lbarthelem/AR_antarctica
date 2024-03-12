#!/bin/bash

simu_ssp245=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)
seuil=(seuil_var seuil_hist)

for s in ${seuil[@]}; do
   #loop on sim
  for sim in ${simu_ssp245[@]}; do
      echo $sim
      ar_sim=/scratchu/lbarthelemy/ssp245_2015_2055/ar_detect/$s/ar_tag_ant_CMIP6_ssp245_${s}_${sim}.nc
      #run count AR event algo
      count_ar=/scratchu/lbarthelemy/ssp245_2015_2055/ar_event/$s/count_ar_ssp245_${s}_${sim}.pkl
      python /home/lbarthelemy/script/run_algo/count_ar.py "$ar_sim" "${count_ar}"

      intensite_ar=/scratchu/lbarthelemy/ssp245_2015_2055/intensite_ar/$s/intensite_ar_ssp245_${s}_${sim}.pkl
      vivt=/scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245_$sim.nc
      prec=/scratchu/lbarthelemy/pr/ssp245/pr_6hr_ssp245_${sim}.nc
      tas=/data/lbarthelemy/cmip6_temp/ssp245/tas_ssp245_${sim}.nc

      python /home/lbarthelemy/script/intensite_ar.py "$count_ar" "$vivt" "$prec" "$tas" "$intensite_ar"
   done
done
