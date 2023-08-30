from .instantiation import instantiateDevice
"""
from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.shutters import *
else:
    from sst_common_sim.api import psh7, psh10
"""
psh7 = instantiateDevice("psh7")
psh10 = instantiateDevice("psh10")
