# ORCHIDEE_HTUs

<p align="center">
<img src="https://images.unsplash.com/photo-1506355683710-bd071c0a5828?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80" width="60%"/>
</p>

This tool allows to explore the hydrological station that are available in the simulation and permits the extraction of the discharge from the simulation and from the observations in the ORCHIDEE's HTU system.

# Discharge in the ORCHIDEE river routing scheme

There are 3 files related to the discharge in ORCHIDEE
- **the observation dataset:** it contains the monthly discharge from more than 10 000 hydrological stations from different sources. 
- **the river routing file:** it is used as an input in the ORCHIDEE/RegIPSL simulations. It contains the information on the different stations available for the simulation, their location in the output file and the reference to find the corresponding station in the observation file.
- **HTUDis file:** This is a file as output from the ORCHIDEE/RegIPSL models. It contains the variable HTUDis where all HTU in the simulations are indexed.


## Observation dataset
The observation dataset contains different informations about the stations (name, river, next station, longitude, latitude, altitude, country, WMO region and subregion).

The data for each stations may come from the merge of 2 different datasets. Therefore, the variable which should be used as observation is the "mergedhydro" variable.

**NOTE:** This file has to be generated for each institution, with the minimal information. At IPSL we generated this file as mixing multiple difference sources, one of them from the [GRDC](https://www.bafg.de/GRDC/EN/01_GRDC/13_dtbse/database_node.html)

For more details see [RoutingPP wiki page](https://gitlab.in2p3.fr/ipsl/lmd/intro/routingpp/-/wikis/Home/InputFiles/Stationfile).

## River routing file

The information about the hydrological stations in the river routing file is located in the variable "st_locations". It has a dimension (5, number of stations) and for each station, the 5 info available are:
- **ID:** index of the stations shared with the observation dataset.
- **i-index:** gives the x-axis index of the stations over the atmospheric grid (**FORTRAN index**, start by 1)
- **j-index:** gives the y-axis index of the stations over the atmospheric grid (**FORTRAN index**, start by 1)
- **HTU-index:** gives the index of the htu over which the stations has been localized (**FORTRAN index**, start by 1)
- **monitoring-index:** gives the location of the station over the nbasmon axis in the output file

The stations from the Observation files are located on the HTUs (subtile hydrological units) over the considered grid by finding an HTU which is in a grid point close to the exact lon/lat of the stations and with the closest upstream area. Some thresholds define the maximal errors in terms of distance / upstream area beyond which we consider that the station cannot be located in a HTU.

## Output file

In the output file, the discharge simulated are located in the variable "HTUDis". 

If the atmospheric grid has a dimension (nj,ni), this variable will have for dimension: (**nbasmon**, nj, ni) with **nbasmon** the maximum number of station per grid point

# Extraction of the discharge

To use the tool to extract and explore the discharge from the ORCHIDEE simulation, one should create a repository following the structure of the "example" folder which contains: 
1) `1_exploration_stations.py` : to explore the stations available
2) `2_extraction.py` : to extract the discharge
3) `run.def` : with the information required
4) an "OUTPUT" subfolder

## 1_exploration_stations.py
To run it, it will be necessary to fill the direction of the routing file `routing_file` and of the observation file `grdc_file` in the `run.def` file. The user can also indicates y0 and y1 the year of start and end of the simulations. In this case the percentage of monthly data available will be calculated for each station.
 
The stations available and their metadata will be saved in a csv file as well as the percentage of data available if y0 and y1 are indicated.

User can make a filtering of the available stations throughout an additional parameter inside `1_exploration_stations.py` called `df_filter`, with the following semantync:

Two different files are generated:
* `Information_Stations_Available.csv`: List of all the stations available from the simulations
* `Information_Stations_Available_filtered.csv`: List of all the stations available from the simulations following `df_filter`

Some stations are represented by multiple element in the database. This due to the different origins of these data and the large discrepancies in terms of longitude / latitude / upstream area between these different source of data.


## 2_extraction.py 
The user will need to indicate the direction of the routing file `routing_file` and of the observation file `grdc_file` as well as the name of the simulation `simulation_name` and the direction of the output file `output_file`. The user can also indicate the name for the output in the OUTPUT folder with `name_output`.

If the user want to compare different simulations **over the same periods**, the **2_extraction.py** can be modified manually through:
- `simus`: the dictionary of simulations, the key is the name of the simulation and the value the directory of the output file.
   - if these simulations use different routing file, the user can define the variable routing_file as a dictionary which keys are the name of the simulation and with the direction of the routing files as values.
- `stations`: The stations from which we want to extract the discharge must be indicated in the dictionary (key:id_station, value:name_station) in the 2_extraction.py file. 

The data will be extracted in `Output/{name_output}_{idstation}.csv` folder, one csv file per station with the name of the simulation as head of the columns.
