import sys
sys.path.append("../src")
from environment import GRDC, get_params, interactive_plot
from netCDF4 import Dataset
import numpy as np
import pandas as pd

####################################################################
###############          DO NOT EDIT THIS PART          ############
####################################################################

routing_file, grdc_file, y0, y1,_,_,_ = get_params()

# open the routing file to get the stations id
nc_routing = Dataset(routing_file, "r")
stid = nc_routing.variables["st_locations"][0,:]

# open the GRDC file to get the informations for the available stations
obs = GRDC(grdc_file)
Dvar = obs.get_data_stations_available(stid,y0=y0,y1=y1)


# Creation of a DataFrame with all the stations available
# ... and their metadata 
df = pd.DataFrame()
for varn in Dvar.keys():
    df[varn] = Dvar[varn]
df.set_index("index")
# Save it in a csv file
df.to_csv("Information_ALL_Stations_Available.csv", sep=";")

####################################################################
####################################################################
###############                EDIT BELOW               ############
####################################################################
####################################################################

# You can apply different filters to the DataFrame of stations available

# Example 1:
# filter the stations with more than 80% availability
df_80percent = df[df["data_available"]>80]
df_80percent.to_csv("Information_Stations_Available_80percent.csv", sep=";")

# To show the list of stations in df_80percent
#stations_id_list = df_80percent["number"].astype(np.int32).tolist()
#print(stations_id_list)

# Example 2:
# stations in Argentina
df_argentina = df[df["country"]=="AR"]
df_argentina.to_csv("Information_Stations_Available_argentina.csv", sep=";")

# To show the list of stations in df_argentina
#stations_id_list = df_argentina["number"].astype(np.int32).tolist()
#print(stations_id_list)

###############################
# Interactive plot
# Example of how to make interactive plot from a dataframe
interactive_plot("stations_argentina", df_argentina, center = [-40, -70], zoom = 5)
