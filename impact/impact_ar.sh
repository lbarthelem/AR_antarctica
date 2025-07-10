#!/bin/bash

periode=(hist ssp245)
seuil=(seuil_hist seuil_var)
simu_hist=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)
simu_ssp245=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)

for per in ${periode[@]}; do
   echo $per
   for s in ${seuil[@]}; do
      echo $s

      if [ $per = hist ]; then
         simu=${simu_hist[*]}
      else
         simu=${simu_ssp245[*]}
      fi

      for sim in ${simu[@]}; do
         echo $sim
         if [ $per = hist ] && [ $s = seuil_hist ]; then
	    ar=/data/lbarthelemy/vertical_integral/CMIP6-present/algo_run/ar_hist_${sim}_1995-2015.nc

         elif [ $per = hist ] && [ $s = seuil_var ]; then
            ar=/data/lbarthelemy/test_seuil_algo/hist/point_var_IWV/run_algo/ar_hist_hvar_${sim}_2035_2055.nc

         else
            ar=/scratchu/lbarthelemy/ssp245_2015_2055/ar_detect/$s/ar_tag_ant_CMIP6_ssp245_${s}_${sim}.nc
         fi

         ar_2d=/scratchu/lbarthelemy/impact/$per/$s/ar_2d/ar_2day_${per}_${s}_${sim}.nc
         echo $ar
         python /home/lbarthelemy/script/impact/ar_2day.py "$ar" "$ar_2d"
         echo "ar_2d good"
         precip_tot=/scratchu/lbarthelemy/pr/day/$per/pr_mm_day_${per}_${sim}.nc
         snow=/scratchu/lbarthelemy/snow/$per/day/prsn_day_${per}_${sim}.nc
         rain=/scratchu/lbarthelemy/precip_liq/$per/prl_mm_eq_${per}_${sim}.nc
         output1=/scratchu/lbarthelemy/impact/$per/$s/all_precip/ar_precip_${per}_${s}_${sim}.nc
         output2=/scratchu/lbarthelemy/impact/$per/$s/all_precip/contrib_ar_precip_${per}_${s}_${sim}.nc

         python /home/lbarthelemy/script/impact/impact_pr.py "$ar_2d" "$precip_tot" "$snow" "$rain" "$output1" "$output2"
      done
      echo "================================================================================================"
   done
   echo "==================================================================================================="
   echo "==================================================================================================="
done

python ar_melt.py
