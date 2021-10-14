# import sst_hw.motors
#from types import SimpleNamespace
from . import STATION_NAME


#def _motors():
if STATION_NAME == "sst_sim":
    from sst_common_sim.api import samplex, sampley, samplez, sampler
    from sst_common_sim.api import framex, framey, framez, framer
    from sst_common_sim.api import manipulator, sample_holder

if STATION_NAME == "ucal":
    from ucal_hw.motors import *
    from sst_hw.motors import *

"""
Disabled 20211013, too complex for testing, unnecessary
    motors = [samplex, sampley, samplez, sampler]

    return SimpleNamespace(samplex=samplex,
                           sampley=sampley,
                           samplez=samplez,
                           sampler=sampler,
                           framex=framex,
                           framey=framey,
                           framez=framez,
                           framer=framer,
                           manipulator=manipulator,
                           sample_holder=sample_holder,
                           motors=motors)


globals().update(_motors().__dict__)
"""
