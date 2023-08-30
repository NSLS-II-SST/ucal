"""
from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.mirrors import *
elif STATION_NAME == "sst_sim":
    from sst_common_sim.mirrors import mir1, mir3, mir4
"""
from .instantiation import instantiateDevice

mir1 = instantiateDevice("mir1")
mir3 = instantiateDevice("mir3")
mir4 = instantiateDevice("mir4")
