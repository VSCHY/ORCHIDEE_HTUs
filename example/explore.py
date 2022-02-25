import pandas as pd
import folium
import numpy as np


dire = "/media/anthony/Seagate Expansion Drive1/ORCHIDEE_HTUs/ORCHIDEE_HTUs1/example/Information_Stations_Available.csv"

df = pd.read_csv(dire, sep = ";", index_col = 0)
df = df[df["data_available"]>50]

print(df.columns)
n = len(df)
name = df["name"].to_numpy()
lon = df["lon"].to_numpy()
lat = df["lat"].to_numpy()
da = df["data_available"].to_numpy()
da = da.astype(np.int32)
area = df["area"].to_numpy()
area = area.astype(np.int32)
number = df["number"].to_numpy()


m = folium.Map([-40, -70], zoom_start=5)
for i in range(n):
   loc = [lat[i],lon[i]]
   #
   popup = folium.Popup(f"{number[i]}: {name[i]} / {da[i]}% / {area[i]} km^2 ", max_width=300,min_width=100, fontsize= 50)
   icon = folium.Icon(color='red', icon='info-sign') 
   folium.Marker(loc, popup=popup, icon=folium.Icon(color="red", icon='info-sign')).add_to(m)

folium.Map.save(m, "./stations_of_interest.html")

