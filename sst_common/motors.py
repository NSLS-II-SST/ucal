# import sst_hw.motors
from types import SimpleNamespace
from . import STATION_NAME


def _motors():
    if STATION_NAME == "sst_sim":
        from sst_common_sim.api import samplex, sampley, samplez, sampler
        from sst_common_sim.api import manipulator, sample_holder

    motors = [samplex, sampley, samplez, sampler]
    return SimpleNamespace(samplex=samplex,
                           sampley=sampley,
                           samplez=samplez,
                           sampler=sampler,
                           manipulator=manipulator,
                           sample_holder=sample_holder,
                           motors=motors)


globals().update(_motors().__dict__)
