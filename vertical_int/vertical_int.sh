#!/bin/bash

periode=(ssp245)
simu_hist=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)
simu_ssp245=(r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1) #r1i1p1f1

for per in ${periode[@]}; do
   echo $per

   if [ $per = hist ]; then
      simu=${simu_hist[*]}
   else
      simu=${simu_ssp245[*]}
   fi

   for sim in ${simu[@]}; do

      echo $sim
      hus=(/bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245/$sim/6hrLev/hus/gr/latest/*.nc)
      va=(/bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245/$sim/6hrLev/va/gr/latest/*.nc)


      for ((i=0;i<=${#hus[@]};i++)); do

         echo ${hus[i]}
         #create file 5 year of vIVT, save as vIVT_ssp245_r1i1p1f1_1.nc
         output_vivt=/scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245_${sim}_$i.nc
         output_iwv=/scratchu/lbarthelemy/ssp245_2015_2055/IWV/IWV_ssp245_${sim}_$i.nc
         python /home/lbarthelemy/script/vertical_int/vertical_integral.py "${hus[i]}" "${va[i]}" "$output_vivt" "$output_iwv"
         echo 'vertical int good'
      done

      #create a unique file of vIVT per member, save as vIVT_ssp245_r1i1p1f1.nc
      cdo -invertlat -sellonlatbox,-180,180,-90,-38 -mergetime /scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245_${sim}_*.nc /scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245_${sim}.nc
      rm /scratchu/lbarthelemy/ssp245_2015_2055/vIVT/vIVT_ssp245_${sim}_*.nc

      #create a unique file of 	IWV per member, save as IWV_ssp245_r1i1p1f1.nc
      cdo -invertlat -sellonlatbox,-180,180,-90,-38 -mergetime /scratchu/lbarthelemy/ssp245_2015_2055/IWV/IWV_ssp245_${sim}_*.nc /scratchu/lbarthelemy/ssp245_2015_2055/IWV/IWV_ssp245_${sim}.nc
      rm /scratchu/lbarthelemy/ssp245_2015_2055/IWV/IWV_ssp245_${sim}_*.nc
      echo 'mergetime good'

      #create monthly file of vIVT per member, save as vIVT_ssp245_01_r1i1p1f1.nc
      mkdir /scratchu/lbarthelemy/ssp245_2015_2055/vIVT/$sim

      var=vIVT
      sh /home/lbarthelemy/script/vertical_int/extract_month.sh $sim $var

      #create monthly file of vIVT per member, save as vIVT_ssp245_01_r1i1p1f1.nc
      mkdir /scratchu/lbarthelemy/ssp245_2015_2055/IWV/$sim

      var=IWV
      sh /home/lbarthelemy/script/vertical_int/extract_month.sh $sim $var
      echo 'monthly file good'


   done

done
