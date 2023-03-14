from bluesky import Msg
from bluesky.plan_stubs import rd
from ucal.motors import manipulator
from ucal.shutters import psh7
from ucal.detectors import GLOBAL_ACTIVE_DETECTORS
from sst_funcs.configuration import add_to_plan_list
import warnings


def call_obj(obj, method, *args, **kwargs):
    ret = yield Msg("call_obj", obj, *args, method=method, **kwargs)
    return ret


def update_manipulator_side(side, *args):
    """
    Sides are numbered starting at 1
    """
    yield from call_obj(manipulator.holder, "update_side", side - 1, *args)


@add_to_plan_list
def set_exposure(time, extra_dets=[]):
    for d in GLOBAL_ACTIVE_DETECTORS:
        try:
            if hasattr(d, "set_exposure"):
                yield from call_obj(d, "set_exposure", time)
        except RuntimeError as ex:
            warnings.warn(repr(ex), RuntimeWarning)


@add_to_plan_list
def open_shutter():
    yield from psh7.open()


@add_to_plan_list
def close_shutter():
    yield from psh7.close()

def is_shutter_open():
    state = yield from rd(psh7.state)
    if state == 1:
        return False
    else:
        return True
