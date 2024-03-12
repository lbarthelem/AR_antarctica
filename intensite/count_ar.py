"""
Created on Tue Apr 26 13:39:57 2022

@author: leonard
"""
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
import pandas as pd
import xarray as xr

from math import sin, cos, acos, pi
import sys


#fuction to compute distenci between point in earth:
def deg2rad(dd):
    #convert degre to radian
    return dd/180*pi

def rad2deg(rd):
    #convert radian to degre
    return rd/pi*180

def dist(latA, lonA, latB, lonB):
    #return the dist between 2 points (coord in degre):

    latA = deg2rad(latA)
    latB = deg2rad(latB)
    lonA = deg2rad(lonA)
    lonB = deg2rad(lonB)
    ER = 6378137 #earth radius

    if latA == latB and lonA == lonB:
        S = 0
    else:
        S = acos(sin(latA)*sin(latB) + cos(latA)*cos(latB)*cos(abs(lonB-lonA)))
    # dist return in degre
    return (rad2deg(S))
#%% get the centroid of DBSCAN clustering

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)
#%%
def diff_ar(ds, times):
    ### splits a map into different ARs using DBSCAN clustering
    # ds = tag dataset, times = dates.
    # Returns number of rivers, and centroid position (longitude)

    # select points with river at given time
    ar = ds.sel(time = times).to_dataframe().reset_index()
    ar = ar.where(ar.ar_binary_tag == 1 )
    ar = ar.dropna()


    # Group by longitude clusters
    x = ar[['lat','lon']].to_numpy()

    if len(x) == 0: # no rivers detected
        date = [times]
        lat_lon_ar = [np.nan]
        centroid = [np.nan]
        label = [np.nan]
        num_clusters = 0


    else:
        kms_per_radian = 6371.0088
        epsilon = 900/ kms_per_radian #nb of km maximum betwenn point in the same cluster

        #computaion of the DBSCAN clustering
        db = DBSCAN(eps=epsilon, min_samples = 20, algorithm='ball_tree',
                    metric='haversine').fit(np.radians(x))


        cluster_labels = db.labels_ #each point is recording to a cluster label


        num_clusters = len(set(cluster_labels) - set([-1])) #nb of labels
        clusters = pd.Series([x[cluster_labels == i] for i in set(db.labels_) - set([-1])]) #group each point in the same cluster

        centermost_points = clusters.map(get_centermost_point)# centroïd of the clusters
        clusters= clusters.tolist()

        lat_lon_ar = clusters
        centroid = centermost_points
        label = np.arange(0,num_clusters)
        date = [times] * num_clusters


    return(num_clusters, centroid, label, lat_lon_ar, )



#### Initialisations ###

file = str(sys.argv[1])
output = str(sys.argv[2])   

ar = xr.open_dataset(file)

nb_ar = 0 # number of events detected


# Event characteristics (arrays, index = event number 0, 1, 2... nb_ar)
date_beg = [] # first date of event
date_end = [] #last date of event
centroids = [] # last centroid of event


list_time = [] #all time step of event
list_centroid = [] #all centroid of event
ar_pos = [] # all coord of AR event at each time step

# Create list of events (event numbers) present at each date :
dat = [ [] for i in range (len(ar.time))]
event_list = pd.Series(dat, index=ar.time.values)
label_all = []


# --- Loop over time steps --- #
t = 0
for times in ar.time.values :
    print(times)
    nb, cents, label, lat_lon_ar = diff_ar(ar, times)
    label_all.append(label)


    #first AR detected:
    if nb_ar == 0 and nb > 0:
        nb_ar = nb

        date_beg.extend([times]*nb)
        date_end.extend([times]*nb)
        centroids.extend(cents)

        list_time.extend([times]*nb)
        for k in range(nb):
            list_centroid.extend([cents[k]])
            ar_pos.extend([lat_lon_ar[k]])


        event_list[times] = list(range(nb))


    elif nb > 0 :

        for i in range(nb) :
            new_ar = True
            # look for centroids at previous timestep
            for j in range(len(event_list[t-1])):

                event = event_list[t-1][j]
                diff = dist(cents[i][0], cents[i][1], centroids[event][0], centroids[event][1])

                # continuation of previous river
                if diff < 15: #dist max for the same event in degree

                    # Creation of centroid,pos and time list of each event
                    if np.shape(list_centroid[event]) == (2,):
                        lc = [list_centroid[event]]
                        lpos = [ar_pos[event]]
                        ltime = [list_time[event]]

                    else:
                        lc = list_centroid[event]
                        lpos = ar_pos[event]
                        ltime = list_time[event]

                    lc.append(cents[i])
                    lpos.append(lat_lon_ar[i])
                    ltime.append(times)

                    date_end[event] = times
                    centroids[event] = cents[i]
                    event_list[times].append(event)

                    list_time[event] =  ltime
                    list_centroid[event] = lc
                    ar_pos[event] = lpos

                    new_ar = False

            # If no previous centroid, create new event
            if new_ar :

                date_beg.append(times)
                date_end.append(times)
                centroids.append(cents[i])

                list_time.extend([times])
                list_centroid.extend([cents[i]])
                ar_pos.extend([lat_lon_ar[i]])

                event_list[times].append(nb_ar)
                nb_ar += 1
    t += 1

#df creation whith all information of the event
df = pd.DataFrame()
df['ar_begin'] = date_beg
df['ar_end'] = date_end
df["last_centroid"] = centroids
df['time_ar'] = list_time
df["list_centroid"] = list_centroid
df["ar_pos"] = ar_pos

#save file
out_file = output
df.to_pickle(out_file)

