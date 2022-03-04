# import sst_hw.motors
#from types import SimpleNamespace
from . import STATION_NAME


#def _motors():
if STATION_NAME == "sst_sim":
    from sst_common_sim.api import manipulator, multimesh

if STATION_NAME == "ucal":
    from ucal_hw.motors import tesz
    from ucal_hw.manipulator import manipulator
    from sst_hw.motors import Exit_Slit as eslit
    from sst_hw.manipulator import multimesh

manipx = manipulator.x
manipy = manipulator.y
manipz = manipulator.z
manipr = manipulator.r

samplex = manipulator.sx
sampley = manipulator.sy
samplez = manipulator.sz
sampler = manipulator.sr

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
