#!/bin/bash

#indicate periods and members per period:
periode=(hist ssp245)
simu_hist=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)
simu_ssp245=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)
simu_100=(r1i1p1f1 r5i1p1f1 r10i1p1f1 r11i1p1f1) # Indicate here the simulation that goes to 2100
#simu_ssp370=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)




seuil=(fixed addapt)
month=(1 2 3 4 5 6 7 8 9 10 11 12)

#indicate absolute path of vIVT and IWV data
vertical_int_path=/scratchu/lbarthelemy/data_test/vertical_int

#indicate absolute output path
output_run_algo=/scratchu/lbarthelemy/data_test/file_run_algo
output_ar=/scratchu/lbarthelemy/data_test/ar_detect
#please check for the existance of all the folder

#path python iwv_coef script
path_iwv_coef_py=/home/lbarthelemy/script/run_algo/iwv_coef.py

#path python threshold script
path_threshold_py=/home/lbarthelemy/script/run_algo/threshold_all_sim.py

#path python run_algo script
path_algo_py=/home/lbarthelemy/script/good_algo/run_algo/algo_AR_LR_CMIP6.py


for per in ${periode[@]}; do
   echo $per
   if [ $per = hist ]; then
      simu=${simu_hist[*]}
   else
      simu=${simu_ssp245[*]}
   fi

   #compute the variable threshold for each month
   for m in ${month[@]}; do

      if [ $m -le 9 ]
      then
         mon=0$m
      else
         mon=$m
      fi
      echo $mon

      for sim in ${simu[@]}; do
         #if you use the vertical_int.sh script, no need to change iwv path
         iwv=$vertical_int_path/$per/IWV/$sim/IWV_ssp245_${mon}_${sim}.nc
         output1=$output_run_algo/IWV/month/IWV_60_38_${sim}_${mon}.nc

         cdo selyear,2015/2054 -sellonlatbox,-180,180,-60,-38 $iwv $output1
      done


      for s100 in ${simu_100[@]}; do
         iwv=$vertical_int_path/$per/IWV/$s100/IWV_ssp245_${mon}_${s100}.nc
         output2=$output_run_algo/IWV/month/IWV_2055_2100_60_38_${s100}_${mon}.nc

         cdo selyear,2055/2100 -sellonlatbox,-180,180,-60,-38 $iwv $output2
      done


      #compute historical clim of IWV between -60° and -38°
      iwv_hist="$vertical_int_path/hist/IWV/*/IWV_${mon}_*.nc"
      clim_hist_iwv=$output_run_algo/IWV/IWV_hist/IWV_global_mean_all_sim_$mon.nc

      #compute yearly mean of IWV between -60° and -38°
      year_iwv_beg=$output_run_algo/IWV/yearly_mean/IWV_yearly_mean_all_sim_15_54_$mon.nc
      year_iwv_end=$output_run_algo/IWV/yearly_mean/IWV_yearly_mean_all_sim_55_100_$mon.nc
      year_iwv=$output_run_algo/IWV/yearly_mean/IWV_yearly_mean_all_sim_$mon.nc
      cdo -f nc2 monmean -ensmean '$output_run_algo/IWV/month/IWV_60_38_*_*.nc' $year_iwv_beg
      cdo -f nc2 monmean -ensmean '$output_run_algo/IWV/month/IWV_2055_2100_60_38_*_*.nc' $year_iwv_end
      cdo mergetime $year_iwv_beg $year_iwv_end $year_iwv
      rm $year_iwv_beg $year_iwv_end


      #clean folder month/
      rm /scratchu/lbarthelemy/ssp245_2015_2055/IWV/month/*.nc

      #run iwv_coef.py to compute the var coeficient
      coef_iwv=$output_run_algo/IWV/coef_iwv/coef_IWV_$mon.csv
      python $path_iwv_coef_py "$glob_iwv" "$year_iwv" "$coef_iwv"
      echo "compute coef = Good"
      echo "==================="

      #run threshold_all_sim.py to compute the variative threshold
      vivt_hist="$vertical_int_path/hist/vIVT/*/vIVT_hist_${mon}_*.nc"
      thr_var=$output_run_algo/threshold_var/threshold_ssp245_$mon.nc
      python /home/lbarthelemy/script/run_algo/threshold_all_sim.py "$coef_iwv" "$vivt_hist" "$thr_var"
      echo "compute threshold = Good"
      echo "========================"

      #run algo
      #loop on seuil (threshold):
      for s in ${seuil[@]}; do
         #loop on sim
         for sim in ${simu[@]}; do
            mkdir /scratchu/lbarthelemy/ssp245_2015_2055/ar_detect/$s/$sim/
            vivt=/scratchu/lbarthelemy/ssp245_2015_2055/vIVT/$sim/vIVT_${per}_${m}_${sim}.nc
            thr_hist=/scratchu/lbarthelemy/ssp245_2015_2055/vivt_hist/vivt_threshold/vIVT_hist_all_${mon}.nc
            output_ar=/scratchu/lbarthelemy/ssp245_2015_2055/ar_detect/$s/$sim/ar_tag_ant_CMIP6_${per}_${s}_${sim}_$mon.nc
            vivt80=/scratchu/lbarthelemy/ssp245_2015_2055/vIVT/$sim/vIVT_80_${per}_${m}_${sim}.nc
            cdo sellonlatbox,-180,180,-80,-38 "$vivt" "$vivt80"

            if [ $s = seuil_hist ]; then
               thr=$thr_hist

            else
               thr=$thr_var
            fi

            python /home/lbarthelemy/script/run_algo/algo_AR_LR_CMIP6_${s}.py "$vivt80" "$thr" "$output_ar"
            echo "compute ar $s"
            echo "============="
         done
      done
   done
