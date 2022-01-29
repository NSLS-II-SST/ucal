from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.api import sc, i0, i1, ref, thresholds
    basic_dets = [sc, i0, i1, ref]
if STATION_NAME == "ucal":
    from ucal_hw.detectors import *
    

