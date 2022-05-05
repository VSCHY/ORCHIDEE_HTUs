from netCDF4 import Dataset, num2date
import numpy as np
import datetime
import pandas as pd
import xarray as xr
import tqdm
                            
class ORCHIDEE:
   def __init__(self, dsimu, rout, sname):
      self.sname = sname
      self.dsimu = dsimu
      self.nc = Dataset(dsimu, "r")
      self.get_time()
      self.rout = rout
      self.Dis = self.nc.variables["HTUDis"]

   def get_time(self, d1=None, d2=None):
      """
      Get the time reference between d1 and d2
      d1 (datetime): start date
      d2 (datetime): end date
      """
      time = self.nc.variables["time_counter"]
      dtime = num2date(time[:], time.units)
      self.dtime = np.array([datetime.date(dt.year,dt.month,15) for dt in dtime])
      if d1 is not None:
        self.t0 = np.where(self.dtime == d1)[0][0]
        try:
           self.t1 = np.where(self.dtime == d2)[0][0]+1
        except:
           self.t1 = len(self.dtime)
        self.dt0 = self.dtime[self.t0];self.dt1 = self.dtime[self.t1-1]
      else:
        self.t0 = 0 
        self.t1 = len(self.dtime)
        self.dt0 = self.dtime[0];self.dt1 = self.dtime[-1]

   def get_stations(self,stid):
      """
      Get the monthly discharge from the station stid.
      stid (int): reference of the station
      """
      print("entering function")
      try:
         nbasmon,jj,ii = self.rout.get_stations(stid)
         print(nbasmon,jj,ii)
         dtindex = pd.DatetimeIndex(self.dtime)
         dis = self.Dis[self.t0:self.t1,nbasmon-1, jj-1, ii-1]
         df = pd.DataFrame(dis, index = dtindex[self.t0:self.t1], columns = [self.sname])
         monthly=df.resample('M').mean()
         monthly.index = monthly.index.map(lambda dt: dt.replace(day=15)) 
         return monthly
      except:
         print("An error occured in ORCHIDEE.get_stations")
         return None