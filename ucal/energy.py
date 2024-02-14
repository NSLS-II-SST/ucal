#from .instantiation import findAndLoadDevice
#from .motors import manipr

#en = findAndLoadDevice("energy")
from sst_funcs import en
from .motors import manipr

en.rotation_motor = manipr
energy = en.energy

"""
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.api import en
else:
    from ucal_hw.energy import en
"""
