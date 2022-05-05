from environment import routing, ORCHIDEE, GRDC
import pandas as pd
import tqdm
import numpy as np

################################################################
#                  _                                      _    #
#                 (_)                                    | |   #
#   ___ _ ____   ___ _ __ ___  _ __  _ __ ___   ___ _ __ | |_  #
#  / _ \ '_ \ \ / / | '__/ _ \| '_ \| '_ ` _ \ / _ \ '_ \| __| #
# |  __/ | | \ V /| | | | (_) | | | | | | | | |  __/ | | | |_  #
#  \___|_| |_|\_/ |_|_|  \___/|_| |_|_| |_| |_|\___|_| |_|\__| #
#                                                              #
################################################################                                                                                                                  

class environment:
   """
   Main environment.
   """
   def __init__(self, stations: dict, simus: dict, dobs: str, drout):
      """
      stations (dict): key is the station reference, value is the station name.
      simus (dict): key is name of simulation, value is the location of the HTUDis file 
      dobs (str): location of the Observation file
      drout (str or dict): location of the routing file.........
      .........OR dict (key: name simulation, value:location routing file)
      """
      # Load observations
      self.obs = GRDC(dobs)
      
      # Handling if one routing file or one per simulation
      if isinstance(drout, str):
         self.rout = routing(drout)
      else:
         # list of drout element
         dr = np.unique([drout[d] for d in drout.keys()])
         # Load each one
         self.Drout = {d:routing(d) for d in dr}
         simu0 = list(simus.keys())[0]
         self.rout = self.Drout[drout[simu0]]
      self.stations = stations

      # Use first simulation for start/end date (assuming they are all the same)
      simu0 = simus[list(simus.keys())[0]]
      s = ORCHIDEE(simu0, self.rout,"setup")
      self.d0 = s.dt0; self.d1 = s.dt1
      #
      # tlimits for obs
      self.obs.get_tlimits(self.d0,self.d1)

      # Load simulations
      self.Dsimu ={}
      if isinstance(drout, dict):
         for sim in simus.keys():
            print(sim)
            s = ORCHIDEE(simus[sim], self.Drout[drout[sim]], sim)
            s.get_time()
            self.Dsimu[s.sname] = s
      else:
         for sim in simus.keys():
            print(sim)
            s = ORCHIDEE(simus[sim], self.rout, sim)
            s.get_time()
            self.Dsimu[s.sname] = s

   def get_df_station(self, namefile, stid):
      """
      Load the data for station stid in a csv file (simulations + obs).
      namefile (str): define the name of the output
      stid (int): reference of the station
      """
      Lst = [self.obs.get_stations(stid)] # Voir si mergedhydro ou hydrographs 
      for k in tqdm.tqdm(self.Dsimu.keys()):
         A = self.Dsimu[k].get_stations(stid)
         if A is not None:
            Lst.append(self.Dsimu[k].get_stations(stid))
         else:
            print(k, "error for index", stid)
      if len(Lst) >1:
         df = pd.concat(Lst, axis = 1)
         df.to_csv("Output/"+namefile+"_"+str(stid)+".csv", sep = ";")


   def csv_main_stations(self, namefile):
      """
      Export the output+obs for all the stations.
      """
      print("Export to csv:")
      for station_id in self.stations.keys():
         print(self.stations[station_id])
         self.get_df_station(namefile, station_id)

   def get_diag_station(self, simu_name): 
      """
      Get basic diagnostic for the stations of interest for a simulation.
      (return area, lon, lat, rmse, nrmse, pbias, corr)
      simu_name: name of the simulation
      """
      # Create from a nested dictionnary
      D = {}
      print(simu_name)
      for st_num in tqdm.tqdm(self.Dst.keys()): 
         # Obs
         hydro_obs = self.obs.get_stations(st_num, varn = self.Dst[st_num]) # "Obs."
         hydro = self.Dsimu[simu_name].get_stations(st_num) # self.sname (self = Dsimu[k])
         hydro_obs = hydro_obs["Obs."].to_numpy()
         hydro = hydro[simu_name].to_numpy()
         if np.max(hydro) > 0:
            # get - lon, lat
            lon, lat, area = self.obs.get_meta(st_num) 
            corr = np.corrcoef(hydro, hydro_obs)[0,1]
            rmse = np.sqrt(np.sum(np.power(hydro-hydro_obs,2))/hydro.shape[0])
            nrmse = rmse / np.mean(hydro_obs)
            pbias = np.sum(hydro-hydro_obs)/np.sum(hydro_obs)*100
            D[st_num] = {"area":area,"lon":lon, "lat":lat, "rmse": rmse,"nrmse":nrmse, "pbias":pbias,"corr":corr} 
      df = pd.DataFrame(D).transpose()
      df.to_csv("Output/"+simu_name+".csv", sep = ";")


