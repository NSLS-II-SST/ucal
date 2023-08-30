"""
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_sim.controllers import adr
elif STATION_NAME == "ucal":
    from ucal_hw.controllers import adr
"""
from .instantiation import instantiateDevice

adr = instantiateDevice("adr")
