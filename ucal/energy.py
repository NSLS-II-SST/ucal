from .instantiation import findAndLoadDevice
from .motors import manipr

en = findAndLoadDevice("energy")
en.rotation_motor = manipr

"""
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.api import en
else:
    from ucal_hw.energy import en
"""
