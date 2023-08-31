from .instantiation import findAndLoadDevice
"""
from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.shutters import *
else:
    from sst_common_sim.api import psh7, psh10
"""
psh7 = findAndLoadDevice("psh7")
psh10 = findAndLoadDevice("psh10")
