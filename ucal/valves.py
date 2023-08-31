"""
from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.gatevalves import *
"""
from .instantiation import findAndLoadDevice

gv26 = findAndLoadDevice("gv26")
gv27 = findAndLoadDevice("gv27")
gv28 = findAndLoadDevice("gv28")
