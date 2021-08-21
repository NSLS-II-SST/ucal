import sst_hw.detectors 
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.startup import i0, i1, ref


