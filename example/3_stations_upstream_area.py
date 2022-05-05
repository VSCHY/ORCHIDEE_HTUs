import sys
sys.path.append("../src")
from environment import routing_upstream, get_params
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt  

####################################################################

routing_file,_,_,_,_,_,_ = get_params()

# open routing
rout = routing_upstream(routing_file)

# extract the mask from 1 stations by its index in routing_file (C index, start from 0)
# here 627: Porto Murtinho
mask = rout.mask(627)
# In case you want to plot the mask
# To plot the figure
fig = plt.figure(figsize= (10,10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.COASTLINE)
ax.set_extent([-90,-30,-60,15])
ax.contourf(rout.lon, rout.lat, mask)
plt.imshow(mask)
plt.show()
plt.close()
    
#
# Test netcdf creation with a list of stations
# Case 1: using list of stations id
rout.netcdf_output("test1.nc", stations = [3679999,3265601,3265300,3264500], reference = 'station_number')

# Case 2: using list of index in the routing_file
rout.netcdf_output("test2.nc", stations = [144,627,74], reference = 'file_index')
    #
