import sst_hw.motors
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.startup import samplex, sampley, samplez, sampler
    from sst_common_sim.startup import manipulator, sample_holder


