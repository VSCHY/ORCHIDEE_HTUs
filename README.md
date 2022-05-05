# ORCHIDEE_HTUs

<p align="center">
<img src="https://images.unsplash.com/photo-1506355683710-bd071c0a5828?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80" width="50%"/>
</p>

This tool allows to explore the hydrological station that are available in the simulation and permits the extraction of the discharge from the simulation and from the observations in the ORCHIDEE's HTU system.

# I. Discharge in the ORCHIDEE river routing scheme

<p align="center">
<img src="https://github.com/VSCHY/ORCHIDEE_HTUs/blob/main/img/figure01.png" width="70%"/>
</p>

There are 3 files related to the discharge in ORCHIDEE
- **The Observations (GRDC file):** it contains the monthly discharge from more than 10 000 hydrological stations from different sources. 
- **The River Routing description (Routing file):** it is used as an input in the ORCHIDEE/RegIPSL simulations. It contains the information on the different stations available for the simulation, their location in the output file and the reference to find the corresponding station in the observation file.
- **The ORCHIDEE Output (Output file -> HTUDis variable):** This is a file as output from the ORCHIDEE/RegIPSL models. It contains the variable `HTUDis` where all HTU in the simulations are indexed.


## Observation dataset

<p align="center">
<img src="https://github.com/VSCHY/ORCHIDEE_HTUs/blob/main/img/figure02.png" width="200px"/>
</p>

The observation dataset contains different informations about the stations (name, river, next station, longitude, latitude, altitude, country, WMO region and subregion).

The data for each stations may come from the merge of 2 different datasets. Therefore, the variable which should be used as observation is the "mergedhydro" variable.

**NOTE:** This file has to be generated for each institution, with the minimal information. At IPSL we generated this file as mixing multiple difference sources, one of them from the [GRDC](https://www.bafg.de/GRDC/EN/01_GRDC/13_dtbse/database_node.html)

For more details see [RoutingPP wiki page](https://gitlab.in2p3.fr/ipsl/lmd/intro/routingpp/-/wikis/Home/InputFiles/Stationfile).

## River routing file

<p align="center">
<img src="https://github.com/VSCHY/ORCHIDEE_HTUs/blob/main/img/figure03.png" width="200px"/>
</p>

The information about the hydrological stations in the river routing file is located in the variable "st_locations". It has a dimension (5, number of stations) and for each station, the 5 info available are:
- **ID:** index of the stations shared with the observation dataset.
- **i-index:** gives the x-axis index of the stations over the atmospheric grid (**FORTRAN index**, start by 1)
- **j-index:** gives the y-axis index of the stations over the atmospheric grid (**FORTRAN index**, start by 1)
- **HTU-index:** gives the index of the htu over which the stations has been localized (**FORTRAN index**, start by 1)
- **monitoring-index:** gives the location of the station over the nbasmon axis in the output file

The stations from the Observation files are located on the HTUs (subtile hydrological units) over the considered grid by finding an HTU which is in a grid point close to the exact lon/lat of the stations and with the closest upstream area. Some thresholds define the maximal errors in terms of distance / upstream area beyond which we consider that the station cannot be located in a HTU.

## Output file

<p align="center">
<img src="https://github.com/VSCHY/ORCHIDEE_HTUs/blob/main/img/figure04.png" width="200px"/>
</p>

In the output file, the discharge simulated are located in the variable "HTUDis". 

If the atmospheric grid has a dimension (nj,ni), this variable will have for dimension: (**nbasmon**, nj, ni) with **nbasmon** the maximum number of station per grid point

_________________

# II. Setup

_________________

# III. Extraction of the discharge

The process of extraction of the discharge is illustrated in the subfolder `example`. It consists in different step:

1) Copy the example file for your own project in the main ORCHIDEE_HTUs folder.
```bash
cp example my_project
```
2) Fill the run.def file in your project folder (cf. below).
3) Explore the stations available to filter the stations you are interested in (`1_exploration_stations.py`).
You may make some changes on the `1_exploration_stations.py` to customize your station selection. The list of stations is in a Pandas DataFrame format (there are some example of basic expression to filter a DataFrame in the script).
4) Extract the observed and simulated discharge for the stations selected(`2_extraction.py`).
5) Construct the mask of the upstream area for each stations selected (`3_stations_upstream_area.py`).

### III.a. run.def

- `grdc_file` : Location of the Observations file used to construct the routing_file. 
- `routing_file`: Location of the River Routing file used in the simulation. 
- `output_file`: Location of the ORCHIDEE Output file with the HTUDis variable. 
- `simulation_name`: Name of your simulation. 
- `name_output`: Prefix for the output csv with discharge (observed + simulated) that will be generated. 
- `y0`: first year of the simulation. 
- `y1`: last year of the simulation. 

### III.b. 1_exploration_stations.py
The stations available and their metadata will be saved in a csv file as well as the percentage of data available if y0 and y1 are indicated.

All the stations available and their metadata are saved in a csv file (`Information_ALL_Stations_Available.csv`).
You can edit the code where it is indicated to filter the stations available following what you are looking for.

It also shows you how to plot the information from your different DataFrame in an interactive maps (html format) to potentially select manually the stations you are interested in.

/!\ Some stations are represented by multiple element in the database. This due to the different origins of these data and the large discrepancies in terms of longitude / latitude / upstream area between these different source of data.

### III.c. 2_extraction.py

If the user want to compare different simulations **over the same periods**, the **2_extraction.py** can be modified manually through:
- `simus`: the dictionary of simulations, the key is the name of the simulation and the value the directory of the output file.
   - if these simulations use different routing file, the user can define the variable routing_file as a dictionary which keys are the name of the simulation and with the direction of the routing files as values.
- `stations`: The stations from which we want to extract the discharge must be indicated in the dictionary (key:id_station, value:name_station) in the 2_extraction.py file. 

The data will be extracted in `Output/{name_output}_{idstation}.csv` folder, one csv file per station with the name of the simulation as head of the columns.

### III.d. 3_stations_upstream_area.py
This file shows how to:
- extract the mask array of the upstream area of a station
- extract the upstream area of a selection of stations and save it into a NetCDF file
