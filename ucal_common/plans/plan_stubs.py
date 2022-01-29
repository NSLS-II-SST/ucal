from bluesky import Msg
from ucal_common.motors import manipulator
from ucal_common.detectors import det_devices, tes
import warnings

def call_obj(obj, method, *args, **kwargs):
    yield Msg("call_obj", obj, *args, method=method, **kwargs)

def update_manipulator_side(side, *args):
    yield from call_obj(manipulator.holder, "update_side", side, *args)

def set_exposure(time, extra_dets=[]):
    dets = det_devices + [tes] + extra_dets
    for d in dets:
        try:
            yield from call_obj(d, "set_exposure", time)
        except RuntimeError as ex:
            warnings.warn(repr(ex), RuntimeWarning)
