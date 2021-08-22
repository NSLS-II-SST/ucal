import sst_hw.motors
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    from sst_common_sim.api import samplex, sampley, samplez, sampler
    from sst_common_sim.api import manipulator, sample_holder

motors = [samplex, sampley, samplez, sampler]
