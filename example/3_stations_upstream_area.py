import sys
sys.path.append("../lib")
from diag_upstream import routing_upstream

import configparser
import argparse
ConfigFile="run.def"
config = configparser.ConfigParser()
config.read(ConfigFile)

# In case you want to plot the mask
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt  
   
####################################################################

routing_file    = config.get("OverAll","routing_file",fallback=None)

    
# open routing
rout = routing_upstream(routing_file)

# extract the mask from 1 stations by its index in routing_file (C index, start from 0)
# here 627: Porto Murtinho
mask = rout.mask(627)

#
# To plot the figure
fig = plt.figure(figsize= (10,10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.COASTLINE)
ax.set_extent([minlon, maxlon, minlat, maxlat])
ax.contourf(rout.lon, rout.lat, mask)
plt.imshow(mask)
plt.show()
    
#
# Test netcdf creation with a list of stations
# Case 1: using list of stations id
rout.netcdf_output("test1.nc", stations = [3667060,3299998,3265601], reference = 'station_number')

# Case 2: using list of index in the routing_file
rout.netcdf_output("test2.nc", stations = [144,627,74], reference = 'file_index')
    #
