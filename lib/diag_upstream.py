from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
from numba import jit


###############################


class routing_upstream:
    def __init__(self, GraphFile) :
        #
        self.nc = Dataset(GraphFile, 'r')
        self.nbloc = self.nc.dimensions["locations"].size
        self.gridshape = [
                    self.nc.dimensions["y"].size,
                    self.nc.dimensions["x"].size
                    ]      
        #     
               
        if "st_locations" in self.nc.variables.keys() : 
            locinfo=self.nc.variables["st_locations"][:,:]
        else :
            locinfo=self.nc.variables["locations"][:,:]
        #
        
        self.ids = locinfo[0,:].astype(int).tolist()
        self.Fiindex = locinfo[1,:].astype(int).tolist()
        self.Fjindex = locinfo[2,:].astype(int).tolist()
        self.FHTUindex = locinfo[3,:].astype(int).tolist()
        self.FMONindex = locinfo[4,:].astype(int).tolist()
        self.lonrange = [np.min(self.nc.variables["lon"][:,:]), np.max(self.nc.variables["lon"][:,:])]
        self.latrange = [np.min(self.nc.variables["lat"][:,:]), np.max(self.nc.variables["lat"][:,:])]
        #
        self.lon = self.nc.variables["lon"][:]
        self.lat = self.nc.variables["lat"][:]
        
        # Parameters
        basid = self.nc.variables["basinid"][:,:,:]
        self.nbasmax = basid.shape[0]
        land = self.nc.variables["land"][:,:]
        self.nbpt = int(np.sum(land))
        #
        
        self.lnglat = {varn: self.nc.variables[varn][:] for varn in ["lon", "lat"]} 
        #
        
        # Grid points 
        self.nbpt_glo = self.nc.variables["nbpt_glo"][:]
        a = np.unravel_index(ma.argsort(self.nbpt_glo, axis = None)[:self.nbpt], self.nbpt_glo.shape)
        self.conv_land2ij = [[int(a[0][i]), int(a[1][i])] for i in range(a[0].shape[0])]
        
        # Variables
        self.routetogrid = self.conv_2land("routetogrid")
        self.routetobasin = self.conv_2land("routetobasin")
        self.routenbintobas = self.conv_2land("routenbintobas") 
        self.basin_area = self.conv_2land("basin_area") 
        self.area = self.conv_2land("area") 
        return
        
    def conv_2land(self, varname):
       """
       Convert the variable from nhtu/lat/lon to ig/ib format.
       """
       var = self.nc.variables[varname][:]
       if len(var.shape) == 3:
          return np.array([var[:,j,i] for j,i in self.conv_land2ij], order = "F")
       elif len(var.shape) == 2:
          return np.array([var[j,i] for j,i in self.conv_land2ij], order = "F")
    # 
    
    def upstmask(self, i, j, k):
       """
       Get the upstream area mask from the ig/ib coordinates.
       """
       g0 = self.nbpt_glo[int(j)-1,int(i)-1] # -1 Because F -> C
       b0 = int(k)

       mask = diag_upstmask(
                    self.routetogrid,
                    self.routetobasin,
                    self.routenbintobas,
                    self.basin_area,
                    self.area,
                    g0,b0)
       return mask

    def mask(self, index):
        # Function to compute mask of area upstream of function with information in the GraphFile
       i = self.Fiindex[index]
       j = self.Fjindex[index]
       k = self.FHTUindex[index]
       # 
       mask_raw = self.upstmask(i,j,k)
       mask = np.zeros(self.gridshape)
       for g in range(self.nbpt): 
          jj,ii = self.conv_land2ij[g]
          mask[jj,ii] = min(mask_raw[g],1)
       return mask



    def netcdf_output(self, dir_output, stations = [], reference = ""):
        """
        stations: list of the stations for the output
        reference: values accepted 'file_index' or 'station_number'
            'file_index' if the list contains the index of the stations in the routing file (!!)
            'station_number' if the list contains the number/id of the stations
        """
        
        if reference == "":
            print("Please specify the reference: 'file_index' or 'station_number'.")
            return
        elif len(stations) == 0:
            print("Please specify a stations list.")
            return
        
        if reference == 'station_number': 
            L = []
            ids = np.array(self.ids)
        
        for stid in stations:
            if reference == 'file_index':
                if stid >= len(self.ids):
                    print("Error: 'file_index' mode")
                    print("", "One of the index exceeds the length of stations available")
                    return
            if reference == 'station_number': 
                try:
                    j = np.where(ids == stid)[0][0]
                except:
                    print("Error: 'station_number' mode")
                    print("", "station id not an the available stations")
                    print(f"{stid=}")
                    return
                L.append(j)
        
        if reference == 'station_number': stations = L
        
        with Dataset(dir_output, "w") as foo:
            nj,ni = self.lon.shape
            foo.createDimension("lat", nj)
            foo.createDimension("lon", ni)
            
            lon = foo.createVariable("lon", np.float32, ("lat","lon"), zlib = True)
            lon.setncattr("units","degrees_east")
            lon.setncattr("long_name","longitude")
            lon[:] = self.lon[:]
            
            lat = foo.createVariable("lat", np.float32, ("lat","lon"), zlib = True)
            lat.setncattr("units","degrees_north")
            lat.setncattr("long_name","latitude")
            lat[:] = self.lat[:]
            
            for i in stations:
                mask = self.mask(i)
                mask = ma.masked_where(mask == 0, mask)
                
                var = foo.createVariable(f"st{self.ids[i]}", np.float32, ("lat", "lon"), zlib = True)
                var.setncattr("axis","YX")
                var.setncattr("units","-")
                var.setncattr("long_name",f"Upstream area of station {self.ids[i]}")
                var.setncattr("associate","lat lon")
                var.setncattr("missing_value",1e20)
                var[:] = mask[:]
            
            foo.sync()




#############################################

@jit(nopython=True)
def diag_upstmask(routetogrid,routetobasin,routenbintobas,basin_area,area,g0,b0):
   """
   Attention à l'indexation
   """
   nbpt,nbasmax = routetobasin.shape
   mask = np.zeros((nbpt))
   for ig in range(nbpt):
      nbas = routenbintobas[ig]
      for ib in range(nbas):
         jg = ig
         jb = ib
         while (jb < nbasmax):
           if ((jg == g0-1) and (jb == b0-1)):
             mask[ig] += basin_area[ig,ib]/area[ig]
             jb = nbasmax
           else:
             jt = int(routetogrid[jg,jb]-1)
             jb = int(routetobasin[jg,jb]-1)
             jg = jt
   return mask
       
if __name__ == "__main__":       
    import cartopy
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt       
     
    dirnc = "../../Originals/reduced_AmSud_A_graph_newdivbas_nbasmax55.nc"
    
    # open routing and load stations at the index 627 in this file
    # Porto Murtinho
    rout = routing_upstream(dirnc)
    mask = rout.mask(627)

    #
    # Test mask function with a plot
    fig = plt.figure(figsize= (10,10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cartopy.feature.COASTLINE)
    minlon = -90; maxlon = -30 ; minlat = -60; maxlat = 15
    ax.set_extent([minlon, maxlon, minlat, maxlat])

    ax.contourf(rout.lon, rout.lat, mask)

    plt.imshow(mask)
    plt.show()
    
    #
    # Test netcdf creation
    rout.netcdf_output("test1.nc", stations = [3667060,3299998,3265601], reference = 'station_number')
    rout.netcdf_output("test2.nc", stations = [144,627,74], reference = 'file_index')
    #

