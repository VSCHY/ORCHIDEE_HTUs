import sys
sys.path.append("../src")
from environment import get_params, environment
import time

####################################################################
###############          DO NOT EDIT THIS PART          ############
####################################################################

routing_file, grdc_file, y0, y1,\
        simulation_name, output_file, name_output = get_params()

# Listes des simulations (name:output_direction)
simus = {simulation_name:output_file}

####################################################################
####################################################################
###############                EDIT BELOW               ############
####################################################################
####################################################################

# List of stations with their name

# Manual list: 
stations = {3679999:"Porto Murtinho", 3299998:"Porto Murtinho", 3651807:"Morpara", 3649901:"Maraba",3649900:"Itupiranga", 3620000:"Santo Antonio Do Ica", 3666050:"Caceres", 3659994:"Corrientes", 3264500:"Posadas", 3265601:"Timbues"}

# Read it from a csv file:
stations = load_stations_from_csv("Information_Stations_Available_argentina.csv", output_format = "dict")

####################################################################
###############          DO NOT EDIT THIS PART          ############
####################################################################

# Launch the environment
env = environment(stations, simus, grdc_file, routing_file)

# To save the dataframe of main stations
# will be saved in Output/{name_output}_{idstation}.csv
env.csv_main_stations(name_output)


