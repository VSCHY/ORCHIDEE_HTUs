from netCDF4 import Dataset, num2date
import numpy as np
import tqdm


class routing:
   def __init__(self, drout):
      self.nc = Dataset(drout, "r")
      self.stations_id = self.nc.variables["st_locations"][0,:]
      self.stations_nbasmon = self.nc.variables["st_locations"] 
      
   def get_stations(self, stid):
      """
      Get the index of the station stid in the output file. 
      stid (int): reference of the station
      """
      try:
         ind = np.where(stid == self.stations_id)[0][0] 
         ii,jj,kk,nbasmon = self.stations_nbasmon[1:,ind]
         return nbasmon,jj,ii
      except:
         return None


