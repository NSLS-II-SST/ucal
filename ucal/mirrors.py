"""
from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.mirrors import *
elif STATION_NAME == "sst_sim":
    from sst_common_sim.mirrors import mir1, mir3, mir4
"""
from .instantiation import findAndLoadDevice

mir1 = findAndLoadDevice("mir1")
mir3 = findAndLoadDevice("mir3")
mir4 = findAndLoadDevice("mir4")
