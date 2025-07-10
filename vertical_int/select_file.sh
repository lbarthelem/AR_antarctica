#!/bin/bash

path_folder=$1
date_beg=$2
date_end=$3

date_beg=${date_beg}01010600
date_end=${date_end}01010000
# List for storage valid file
files=()

# look on all .nc on folder
for file in "$path_folder"/*.nc; do
  # Extrac file name 
  filename=$(basename -- "$file")

  # look for date format end extract start end  YYYYMMDDHHMM
  if [[ "$filename" =~ ([0-9]{12})-([0-9]{12}) ]]; then
    start="${BASH_REMATCH[1]}"  # Date de début
    end="${BASH_REMATCH[2]}" 

    # compare to date_beg and date_end
    if [[ "$start" -ge "$date_beg" && "$end" -le "$date_end" ]]; then
      files+=("$file")
    fi
  else
    echo "no date find in  $file"
  fi
done

echo "${files[@]}"
