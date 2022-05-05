import numpy as np
import numpy.ma as ma
import configparser

def get_str(nom):
    iend = np.where(nom.mask == True)[0][0]
    out = "".join(ma.filled(nom[:iend]).astype("str"))
    return out

def get_params():
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