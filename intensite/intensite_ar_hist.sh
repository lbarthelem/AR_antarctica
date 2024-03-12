#!/bin/bash

periode=(hist)
simu_hist=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)
seuil=(seuil_var seuil_hist)


for per in ${periode[@]}; do
   echo $per

   for s in ${seuil[@]}; do
      #loop on sim
      echo $s
      for sim in ${simu_hist[@]}; do

         if [ $s = seuil_hist ]; then
            ar_sim=/data/lbarthelemy/vertical_integral/CMIP6-present/algo_run/ar_hist_${sim}_1995-2015.nc
         else
            ar_sim=/data/lbarthelemy/test_seuil_algo/hist/point_var_IWV/run_algo/ar_hist_hvar_${sim}_2035_2055.nc
         fi


         echo "$ar_sim"
         count_ar=/scratchu/lbarthelemy/hist/ar_event/$s/count_ar_${per}_${s}_${sim}.pkl
         python /home/lbarthelemy/script/run_algo/count_ar.py "$ar_sim" "$count_ar"
         echo "========count_ar good========"

         intensite_ar=/scratchu/lbarthelemy/hist/ar_intensite/$s/intensite_ar_${per}_${s}_${sim}.pkl
         vivt=/data/lbarthelemy/vertical_integral/CMIP6-present/vIVT/vIVT_${sim}.nc
         prec=/scratchu/lbarthelemy/pr/$per/pr_6hr_${per}_${sim}.nc
         tas=/data/lbarthelemy/cmip6_temp/$per/tas_6hr/tas_6hr_${per}_${sim}.nc
         python /home/lbarthelemy/script/intensite_ar.py "$count_ar" "$vivt" "$prec" "$tas" "$intensite_ar"
         echo "========intensite_ar good======="
      done
   done
done



