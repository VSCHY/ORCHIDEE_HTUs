import numpy as np
import numpy.ma as ma

def get_str(nom):
    iend = np.where(nom.mask == True)[0][0]
    out = "".join(ma.filled(nom[:iend]).astype("str"))
    return out
