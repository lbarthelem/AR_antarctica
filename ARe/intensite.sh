#!/bin/bash

periode=(hist ssp245)
seuil=(seuil_hist seuil_var)
simu_hist=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)
simu_ssp245=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)

path_count_ar_py=/home/lbarthelemy/script/run_algo/count_ar.py
path_intensite_py=/home/lbarthelemy/script/intensite_ar.py

for per in ${periode[@]}; do
   echo $per
   for s in ${seuil[@]}; do
      echo $s

      if [ $per = hist ]; then
         simu=${simu_hist[*]}
         path_vivt=/data/lbarthelemy/vertical_integral/CMIP6-present/vIVT/vIVT
      else
         simu=${simu_ssp245[*]}
         path_vivt=/scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245
      fi



      for sim in ${simu[@]}; do
         echo $sim
         ar_sim=/scratchu/lbarthelemy/ssp245_2015_2055/ar_detect/$s/ar_tag_ant_CMIP6_${per}_${s}_${sim}.nc
         cdo mergetime /scratchu/lbarthelemy/ssp245_2015_2055/ar_detect/$s/$sim/ar_tag_ant_CMIP6_${per}_${s}_${sim}_*.nc $ar_sim

         #run count AR event algo
         count_ar=/scratchu/lbarthelemy/ssp245_2015_2055/ar_event/$s/count_ar_${per}_${s}_${sim}.pkl
         python path_count_ar_py "$ar_sim" "${count_ar}"

         c_ar=/data/lbarthelemy/publi_03_2023/$per/count_ar/$s/count_${per}_${s}_${sim}.pkl
         vivt=${path_vivt}_${sim}.nc
         prec=/scratchu/lbarthelemy/pr/$per/pr_6hr_${per}_${sim}.nc
         tas=/data/lbarthelemy/cmip6_temp/$per/tas_6hr/tas_6hr_${per}_${sim}.nc
         out_file=/scratchu/lbarthelemy/intensite/$per/$s/intensite_ev_ar_${per}_${s}_${sim}_v6.pkl

         python path_intensite_py "$c_ar" "$vivt" "$prec" "$tas" "$out_file"
         echo " "
      done
      echo "================================================================================================"
   done
   echo "==================================================================================================="
   echo "==================================================================================================="
done
