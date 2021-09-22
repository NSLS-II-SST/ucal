from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.api import i0, i1, ref, thresholds

dets = [i0, i1, ref]
