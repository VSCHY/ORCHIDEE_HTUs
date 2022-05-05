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

# SAVE THE MASKS IN A NETCDF FILE
# You can give a (1) custom list of stations or (2) use a dataframe saved in a csv file (cf. script 1_exploration_stations.py) : 

##############
### LIST of STATIONS ID

"""
name_output = "test.nc"
list_stations_id = [3679999,3265601,3265300,3264500]
rout.netcdf_output(name_output, stations = list_stations_id, reference = 'station_number')
"""

##############
### CSV FILE 
# Load the csv

"""
name_output = "argentina__stations_mask.nc"
stations_argentina = load_stations_from_csv("Information_Stations_Available_argentina.csv", output_format = "id")
rout.netcdf_output(name_output, stations = stations_argentina, reference = 'station_number')
"""