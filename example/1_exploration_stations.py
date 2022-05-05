import sys
sys.path.append("../src")
from environment import GRDC, get_params
from netCDF4 import Dataset
import numpy as np
import pandas as pd

##################################

routing_file, grdc_file, y0, y1,_,_,_ = get_params()

##################################

# open the routing file to get the stations id
nc_routing = Dataset(routing_file, "r")
stid = nc_routing.variables["st_locations"][0,:]

# open the GRDC file to get the informations for the available stations
obs = GRDC(grdc_file)
Dvar = obs.get_data_stations_available(stid,y0=y0,y1=y1)

# Extract in a csv

##################################
# Create a csv output with the metadata of the stations available

df = pd.DataFrame()
for varn in Dvar.keys():
    df[varn] = Dvar[varn]
df.set_index("index")
df.to_csv("Information_Stations_Available.csv", sep=";")

# Example to filter the stations with more than 80% availability
df_filter = df[df["data_available"]>80]
df_filter.to_csv("Information_Stations_Available_filtered.csv", sep=";")
