from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.api import sc, i0, i1, ref, thresholds, tes
    basic_dets = [sc, i0, i1, ref]
    det_devices = basic_dets
if STATION_NAME == "ucal":
    from ucal_hw.detectors import *
