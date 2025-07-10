#!/bin/bash

#indicate periods and members per period:
periode=(hist) #(hist ssp245)
simu_hist=(r1i1p1f1 r2i1p1f1) #(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r7i1p1f1 r8i1p1f1 r9i1p1f1 r10i1p1f1)
simu_ssp245=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)
#simu_ssp370=(r1i1p1f1 r2i1p1f1 r3i1p1f1 r4i1p1f1 r5i1p1f1 r6i1p1f1 r10i1p1f1 r11i1p1f1 r14i1p1f1 r22i1p1f1)

#indicate absolute path of model data:
path_hist=/bdd/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical
path_ssp245=/bdd/CMIP6/ScenarioMIP/IPSL/IPSL-CM6A-LR/ssp245
#path_ssp370= ..... if needed bud indicate ssp370 in line 4

#indicate absolute output path
output_vertical_int=/scratchu/lbarthelemy/data_test/vertical_int
#please check for the existance of all the folder

#path python script:
path_vertical_py=/home/lbarthelemy/script/good_code/vertical_int/vertical_integral.py

#path extract_month:
path_extract_month_sh=/home/lbarthelemy/script/good_code/vertical_int/extract_month.sh

#path select_file:
path_select_file=/home/lbarthelemy/script/good_code/vertical_int/select_file.sh

#indicate periode for historical in year
date_beg_hist=1995
date_end_hist=2015

#indicate periode for futur
date_beg_futur=2035
date_end_futur=2055

#loop on periode
for per in ${periode[@]}; do
   echo $per

   if [ $per = hist ]; then
      date_beg=$date_beg_hist
      date_end=$date_end_hist
   else
      date_beg=$date_beg_futur
      date_end=$date_end_futur
   fi

   #select good list of members
   eval simu_list=(\"\${simu_${per}[@]}\")
   eval begin_path=\"\${path_${per}}\"

   #loop on members
   for sim in ${simu_list[@]}; do
      echo $sim

      #paths for hus and va, change here with your own path
      #hus=(${begin_path}/$sim/6hrLev/hus/gr/latest/*.nc)
      #va=(${begin_path}/$sim/6hrLev/va/gr/latest/*.nc)

      hus=($($path_select_file ${begin_path}/$sim/6hrLev/hus/gr/latest $date_beg $date_end))
      va=($($path_select_file ${begin_path}/$sim/6hrLev/va/gr/latest $date_beg $date_end))

      for ((i=0;i<${#hus[@]};i++)); do

         # test if the periode of hus and va file are the same
         hus_end=${hus[i]##*_}  # end of string hus[î] from the last "_"
         va_end=${va[i]##*_}    # same

         if [[ "$hus_end" == "$va_end" ]]; then
            echo ${hus[i]}
            echo ${va[i]}
            echo ""
         else
            echo ${hus[i]}
            echo ${va[i]}

            echo "date of hus and va file didn't match"
            echo ""
            exit 1 #interupt script
         fi

	 #output path for vIVT and IWV
	 output_begin=$output_vertical_int/$per

	 if [ ! -d "$output_begin" ]; then
	    mkdir -p "${output_begin}/vIVT/"
	    mkdir -p "${output_begin}/IWV/"
	    echo "Folder $output_begin/vIVT/ and /IWV/ have been created"
            echo ""
	 else
	    echo ""
	 fi

         output_vivt=$output_begin/vIVT/vIVT_${per}_${sim}_$i.nc
         output_iwv=$output_begin/IWV/IWV_${per}_${sim}_$i.nc

	 #run python script for computing vertical integral
         echo "Run vertical_integral.py"
         python $path_vertical_py "${hus[i]}" "${va[i]}" "$output_vivt" "$output_iwv"
         echo 'Vertical integral good'
         echo " "
      done

      #create a unique file of vIVT per member
      cdo -invertlat -sellonlatbox,-180,180,-90,-38 -mergetime $output_begin/vIVT/vIVT_${per}_${sim}_*.nc $output_begin/vIVT/vIVT_${per}_${sim}.nc
      rm $output_begin/vIVT/vIVT_${per}_${sim}_*.nc

      #create a unique file of  IWV per member
      cdo -invertlat -sellonlatbox,-180,180,-90,-38 -mergetime $output_begin/IWV/IWV_${per}_${sim}_*.nc $output_begin/IWV/IWV_${per}_${sim}.nc
      rm $output_begin/IWV/IWV_${per}_${sim}_*.nc
      echo 'mergetime good'
      echo " "

      #create monthly file of vIVT per member
      mkdir $output_begin/vIVT/$sim
      var=vIVT
      sh $path_extract_month_sh $output_begin $var $per $sim

      #create monthly file of IWV per member
      mkdir $output_begin/IWV/$sim
      var=IWV
      sh $path_extract_month_sh $output_begin $var $per $sim
      echo 'monthly file good'
      echo " "

   done
   echo '--------------------------'
done
