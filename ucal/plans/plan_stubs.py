from bluesky import Msg
from ucal.motors import manipulator
from ucal.shutters import psh7
from ucal.detectors import scan_devices
import warnings


def call_obj(obj, method, *args, **kwargs):
    yield Msg("call_obj", obj, *args, method=method, **kwargs)


def update_manipulator_side(side, *args):
    """
    Sides are numbered starting at 1
    """
    yield from call_obj(manipulator.holder, "update_side", side - 1, *args)


def set_exposure(time, extra_dets=[]):
    for d in scan_devices:
        try:
            if hasattr(d, "set_exposure"):
                yield from call_obj(d, "set_exposure", time)
        except RuntimeError as ex:
            warnings.warn(repr(ex), RuntimeWarning)


def open_shutter():
    yield from psh7.open()


def close_shutter():
    yield from psh7.close()
