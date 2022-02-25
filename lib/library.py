from netCDF4 import Dataset, num2date
import numpy as np
import numpy.ma as ma
import datetime
import pandas as pd
import tqdm
from functions import get_str

##################################
#   _____ _____  _____   _____ 
#  / ____|  __ \|  __ \ / ____|
# | |  __| |__) | |  | | |     
# | | |_ |  _  /| |  | | |     
# | |__| | | \ \| |__| | |____ 
#  \_____|_|  \_\_____/ \_____|                                

class GRDC:
   """
   Handle the Observation data.
   """
   def __init__(self, dobs):
      self.nc = Dataset(dobs, "r")
      self.number = self.nc.variables["number"][:]

   # TIME
   def get_time(self):
      """
      Get the time variable.
      """
      time = self.nc.variables["time"]
      dtime = num2date(time[:], time.units)
      self.dtime = np.array([datetime.date(dt.year,dt.month,15) for dt in dtime])

   def get_tlimits(self, d1, d2):
      """
      Get the index within the time variable for d1 and d2.
      d1 (datetime): start time
      d2 (datetime): end time
      """
      self.get_time()
      d = datetime.date(d1.year,d1.month,15)
      self.t0 = np.where(self.dtime == d1)[0][0]
      d = datetime.date(d2.year,d2.month,15)
      self.t1 = np.where(self.dtime == d2)[0][0]+1

   # STATIONS
   def get_stations(self, stid, varn = "auto"):
      """
      Get the data for station stid.
      stid (int): reference of the station
      varn ("auto"/"hydrographs"/"mergedhydro"): select the variable...
      .....with the most data available 
      """
      if varn == "auto":
         varn = self.get_varname(stid) 
         if varn is None:
            print("Error - no data observations available")
      ind = np.where(self.number == stid)[0][0]
      hydro = self.nc.variables[varn][self.t0:self.t1:,ind]
      dtindex = pd.DatetimeIndex(self.dtime[self.t0:self.t1])
      df = pd.DataFrame(hydro,index = dtindex, columns = ["Obs."])
      return df

   def get_meta(self, index):
      """
      Get the metadata of the stations at index ind.
      ind (int): index of the station.
      """
      ind = np.where(self.number == index)[0][0]
      lon = float(self.nc.variables["lon"][ind])
      lat = float(self.nc.variables["lat"][ind])
      area = int(self.nc.variables["area"][ind])
      return lon, lat, area

   def get_varname(self, stid):
      """
      Get the varname with most data available for station stid.
      stid (int): reference of the station.
      Usually it will be mergedhydro.
      """
      df = self.get_stations(stid, varn = "hydrographs")
      numh = int(df.count(axis = 0))/len(df.index)
      if numh == 1:
         return "hydrographs"
      else:
         df = self.get_stations(stid, varn = "mergedhydro")
         numm = int(df.count(axis = 0))/len(df.index)
         if (numm == 0) * (numh == 0):
            return None
         elif numm>numh:
            return "mergedhydro"
         else:
            return "hydrographs"

            
   ##########
   # EXPLORATION
   
   def get_data_stations_available(self, stids,y0=None,y1=None):
        """
        Get the metadata for the station available in the routing file.
        y0/y1 are used to evaluate the percentage of data available over this period for each stations
        stids (list of int): list of the stid available in the routing file
        y0 (int): year start of the simulation
        y1 (int): year end of the simulation        
        """
        grdc_num = self.nc.variables["number"][:]
        index_stations = [np.where(grdc_num == i)[0][0] for i in stids]
        
        Dvar = {}
        Dvar["index"] = index_stations
        for varn in ["number", "name", "river","WMOreg", "WMOsubreg","country","next","lon", "lat", "altitude"]:
            if varn in ["name", "river","country"]:
                Dvar[varn] = [get_str(self.nc.variables[varn][i,:]) for i in index_stations]
            else:
                Dvar[varn] = [self.nc.variables[varn][i] for i in index_stations]
        if (y0 is not None) and (y1 is not None):
            self.get_time()
            dtime = pd.DatetimeIndex(self.dtime)

            values = []
            for i in range(len(index_stations)):
                ind = index_stations[i]
                d = self.nc.variables["mergedhydro"][:,ind]
                

                df = pd.DataFrame(data = d, index = dtime)
                df.set_index(dtime)    
                df = df[(df.index.year<=y1) & (df.index.year>=y0)]

                summ = len(df)-df.isna().sum().values[0]
                
                d2 = self.nc.variables["hydrographs"][:,ind]
                df2 = pd.DataFrame(data = d2, index = dtime)
                df2.set_index(dtime)    
                df2 = df2[(df2.index.year<=y1) & (df2.index.year>=y0)]

                summ2 = len(df)-df2.isna().sum().values[0]
                if summ < summ2: print(summ, summ2)
                
                values.append((summ)/len(df)*100)
            values = np.array(values)
            Dvar["data_available"] = values        
        return Dvar

###################################################
#                  _   _             
#                 | | (_)            
#  _ __ ___  _   _| |_ _ _ __   __ _ 
# | '__/ _ \| | | | __| | '_ \ / _` |
# | | | (_) | |_| | |_| | | | | (_| |
# |_|  \___/ \__,_|\__|_|_| |_|\__, |
#                               __/ |
#                              |___/                               
#
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

###################################################
#                 _     _     _           
#                | |   (_)   | |          
#   ___  _ __ ___| |__  _  __| | ___  ___ 
#  / _ \| '__/ __| '_ \| |/ _` |/ _ \/ _ \
# | (_) | | | (__| | | | | (_| |  __/  __/
#  \___/|_|  \___|_| |_|_|\__,_|\___|\___|
#                                         
class ORCHIDEE:
   def __init__(self, dsimu, rout, sname):
      self.sname = sname
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
      try:
         nbasmon,jj,ii = self.rout.get_stations(stid)

         dtindex = pd.DatetimeIndex(self.dtime)
         df = pd.DataFrame(self.Dis[self.t0:self.t1,nbasmon-1, jj-1, ii-1],index = dtindex[self.t0:self.t1], columns = [self.sname])
         monthly=df.resample('M').mean()
         monthly.index = monthly.index.map(lambda dt: dt.replace(day=15)) 
         return monthly
      except:
         return None

