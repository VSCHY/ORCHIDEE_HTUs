import sys
sys.path.append("../src")
from environment import routing_upstream, get_params, load_stations_from_csv

####################################################################
###############          DO NOT EDIT THIS PART          ############
####################################################################

routing_file,_,_,_,_,_,_ = get_params()

# open routing
rout = routing_upstream(routing_file)

####################################################################
####################################################################
###############                EDIT BELOW               ############
####################################################################
####################################################################

# SAVE the masks in a netCDF file

#To create the mask of a list of stations id
#> rout.netcdf_output("test1.nc", stations = [3679999,3265601,3265300,3264500], reference = 'station_number')

# You can give a custom list in stations or use a dataframe saved in a csv file (cf. script 1_exploration_stations.py) : 

# Load the csv
stations_argentina = load_stations_from_csv("Information_Stations_Available_argentina.csv", output_format = "id")
# Construct the mask file
rout.netcdf_output("argentina__stations_mask.nc", stations = stations_argentina, reference = 'station_number')
