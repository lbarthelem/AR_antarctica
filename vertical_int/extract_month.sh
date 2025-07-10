#!/bin/bash

for m in 1 2 3 4 5 6 7 8 9 10 11 12
do
    if [ $m -le 9 ]
    then
        imonth=0$m
    else
        imonth=$m
    fi

    cdo select,month=$mois $1/$2/${2}_${3}_${4}.nc $1/$2/$4/${2}_${3}_${imonth}_${4}.nc

done
