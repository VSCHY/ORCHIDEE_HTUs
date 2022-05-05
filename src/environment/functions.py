import numpy as np
import numpy.ma as ma
import configparser
import pandas as pd

def get_str(nom):
    """
    Convert text from netCDF format (60 char) into string.
    """
    iend = np.where(nom.mask == True)[0][0]
    out = "".join(ma.filled(nom[:iend]).astype("str"))
    return out

def get_params():
    """
    Get parameters from the run.def file.
    """
    ConfigFile="run.def"
    config = configparser.ConfigParser()
    config.read(ConfigFile)

    routing_file = config.get("OverAll","routing_file",fallback=None)
    grdc_file    = config.get("OverAll","grdc_file",fallback=None)
    y0           = config.getint("OverAll","y0",fallback=None)
    y1           = config.getint("OverAll","y1",fallback=None)
    simulation_name = config.get("OverAll","simulation_name",fallback=None)
    output_file     = config.get("OverAll","output_file",fallback=None)
    name_output     = config.get("OverAll","name_output",fallback="OUTPUT")

    return routing_file, grdc_file, y0, y1, simulation_name, output_file, name_output

def interactive_plot(namefile: str, df: pd.DataFrame, center = [-40, -70], zoom:int = 5):
    """
    Plot the interactive map with the stations in a df file.
    
    Parameters:
    -----------
    namefile (str): name of the output file.
    df (pandas DataFrame): DataFrame with the stations.
    center (list of 2 number, [lat,lon]): initial center of the map.
    zoom (int): initial zoom of the map
    
    Returns:
    --------
    lm (LogonManager object)
    conn (Connection object)
    ----------------------------------------------------
    """
    if namefile[-5:]!=".html": namefile += ".html"

    import folium
    m = folium.Map(center, zoom_start=zoom)
    lat = df["lat"].values
    lon = df["lon"].values
    name = df["name"].values
    country = df["country"].values
    river = df["river"].values
    altitude = df["altitude"].values
    altitude[altitude == -999] = np.nan
    area = df["area"].values
    available = df["data_available"].values

    nst = df.shape[0]
    for ind in range(nst):
        loc = [lat[ind],lon[ind]]
        #
        unit = " m"
        if np.isnan(altitude[ind]): unit = ""

        descr = f"NAME: {name[ind]}, COUNTRY: {country[ind]}, "+\
                f"RIVER: {river[ind]}, ALTITUDE: {altitude[ind]:.0f}{unit}, "+\
                f"UP. AREA: {area[ind]:.0f} km2, AVAILABLE: {available[ind]:.0f}%"
        
        popup = folium.Popup(descr, max_width=500,min_width=100, fontsize= 50)
        icon = folium.Icon(color='red', icon='info-sign') 
        folium.Marker(loc, popup=popup, icon=icon).add_to(m)

    folium.Map.save(m, namefile)
    return 

def load_stations_from_csv(csv_file: str, output_format: str = "dict"):
    """
    Load the stations and their metadata from a csv file.
    
    Parameters:
    -----------
    csv_file (str): name of the csv file.
    output_format (str): values that can be used are:
                "dict" if we want a dictionnary with (key:id, value:name)
                "id" if we want a list with the id
    
    Returns:
    --------
    stations (dict or list): dictionary or list of stations
    ----------------------------------------------------
    """
    df = pd.read_csv(csv_file, sep=";")
    number = df["number"].astype(np.int32).tolist()
    name = df["name"].tolist()
    if output_format == "dict":
        return {num:n for num, n in zip(number, name)}
    if output_format == "id":
        return number