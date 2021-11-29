import numpy as np
from bluesky.plans import list_scan
from ucal_common.detectors import base_dets

def make_gscan_list(e1, *args):
    if len(args) < 2:
        raise TypeError("make_gscan_list() requires at least estart, estop, and delta")
    if len(args)%2 == 1:
        raise TypeError("make_gscan_list() received an even number of arguments. Either a step or a step-size is missing")
    estart = e1
    positions = []
    for estop, delta in zip(args[::2], args[1::2]):
        n = 0
        while n*delta + estart < estop - delta/10.0:
            positions.append(n*delta + estart)
            n += 1
        estart = estop
    positions.append(estop)
    return positions

def gscan_base(dets, motor, estart, estop, delta, *args):
    position_list = make_gscan_list(estart, estop, delta, *args)
    yield from list_scan(dets, motor, position_list)

def gscan(motor, estart, estop, delta, *args):
    yield from gscan_base(base_dets, motor, estart, estop, delta, *args)
