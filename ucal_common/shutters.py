from . import STATION_NAME

if STATION_NAME == "ucal":
    from sst_hw.shutters import *
else:
    from sst_common_sim.api import *
