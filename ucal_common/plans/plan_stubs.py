from bluesky import Msg
from ucal_common.motors import manipulator


def call_obj(obj, method, *args, **kwargs):
    yield Msg("call_obj", obj, *args, method=method, **kwargs)


def update_manipulator_side(side, *args):
    yield from call_obj(manipulator.holder, "update_side", side, *args)
