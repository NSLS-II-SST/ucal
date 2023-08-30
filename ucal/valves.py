"""
from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.gatevalves import *
"""
from .instantiation import instantiateDevice

gv26 = instantiateDevice("gv26")
gv27 = instantiateDevice("gv27")
gv28 = instantiateDevice("gv28")
