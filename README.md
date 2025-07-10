AR Antarctica

This code (BASH, CDO and Python) is used to determine the impact and characteristics of AR in Antarctica in the present or future periods, using the IPSL-CM6 model here.

To run this analysis, run the following scripts in order:
  - vertical_int.sh in the vertical_int folder to compute the vertical integral of IWV and vIVT.
  - Run run_algo.sh in the run_algo folder to detect the AR footprint.
  - intensite.sh in the ARe folder to cluster the AR detection in time and space.
  - flux.sh in the 'melt' folder to determine the daily melt amount.
  - Finally, run impact_ar.sh to compute the AR impact on the SMB.

Changes will be made to make this code more user-friendly. 
