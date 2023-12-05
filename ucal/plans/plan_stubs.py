from bluesky import Msg
from bluesky.plan_stubs import rd, mv
from ucal.motors import manipulator
from ucal.shutters import psh7
from ucal.detectors import GLOBAL_ACTIVE_DETECTORS
from sst_funcs.help import add_to_plan_list
import warnings

GLOBAL_EXPOSURE_TIME = 1.0

def call_obj(obj, method, *args, **kwargs):
    ret = yield Msg("call_obj", obj, *args, method=method, **kwargs)
    return ret

@add_to_plan_list
def manipulator_to_loadlock():
    """Moves manipulator up into the loadlock chamber"""
    yield from mv(manipulator.x, 0, manipulator.y, 0, manipulator.r, 0, manipulator.z, 20)

@add_to_plan_list
def manipulator_to_main():
    """Moves manipulator down into the measurement chamber"""
    yield from mv(manipulator.x, 0, manipulator.y, 0, manipulator.r, 0, manipulator.z, 250)

def update_manipulator_side(side, *args):
    """
    Sides are numbered starting at 1
    """
    yield from call_obj(manipulator.holder, "update_side", side - 1, *args)


@add_to_plan_list
def set_exposure(time=None, extra_dets=[]):
    """Sets the exposure time for all active detectors"""
    global GLOBAL_EXPOSURE_TIME
    if time is not None:
        GLOBAL_EXPOSURE_TIME = time
    for d in GLOBAL_ACTIVE_DETECTORS:
        try:
            if hasattr(d, "set_exposure"):
                yield from call_obj(d, "set_exposure", GLOBAL_EXPOSURE_TIME)
        except RuntimeError as ex:
            warnings.warn(repr(ex), RuntimeWarning)


@add_to_plan_list
def open_shutter():
    """Opens shutter 7, does not check any other shutters!"""
    yield from psh7.open()


@add_to_plan_list
def close_shutter():
    """Closes shutter 7"""
    yield from psh7.close()

def is_shutter_open():
    state = yield from rd(psh7.state)
    if state == 1:
        return False
    else:
        return True
