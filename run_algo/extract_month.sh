#!/bin/bash

for mois in 1 2 3 4 5 6 7 8 9 10 11 12
do
    if [ $mois -le 9 ]
    then
        imois=0$mois
    else
        imois=$mois
    fi

    echo ${2}_ssp245_${mois}_$1.nc

    cdo select,month=$mois /scratchu/lbarthelemy/ssp245_2015_2055/$2/${2}_ssp245_$1.nc /scratchu/lbarthelemy/ssp245_2015_2055/$2/$1/${2}_ssp245_${mois}_${1}.nc

done
