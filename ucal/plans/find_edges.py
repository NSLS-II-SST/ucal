import numpy as np
from ucal.motors import manipx, manipy, manipz, manipr
from ucal.detectors import det_devices, sc, thresholds
from sst_funcs.plans.maximizers import find_max_deriv, find_max, halfmax_adaptive, threshold_adaptive, find_halfmax
from bluesky.plan_stubs import mv, mvr
from bluesky.plans import rel_scan

# This should go into a beamline config file at some point
max_channel = sc.name
# If we have a drain current detector on the manipulator,
# as opposed to a detector that the manipulator shadows,
# we will need to invert some of the maximum finding routines
detector_on_manip = True


def scan_z_offset(zstart, zstop, step_size):
    nsteps = int(np.abs(zstop - zstart)/step_size) + 1
    ret = yield from find_max_deriv(rel_scan, det_devices, manipz, zstart, zstop,
                                    nsteps, max_channel=max_channel)
    _, zoffset = ret[0]
    print(zoffset)
    return zoffset


def scan_z_coarse():
    return (yield from scan_z_offset(-10, 10, 1))


def scan_z_medium():
    return (yield from scan_z_offset(-2, 2, 0.2))


def scan_z_fine():
    return (yield from scan_z_offset(-0.5, 0.5, 0.05))


def scan_r_offset(rstart, rstop, step_size):
    """
    Relative scan, find r that maximizes signal
    """
    nsteps = int(np.abs(rstop - rstart)/step_size) + 1
    ret = yield from find_max(rel_scan, det_devices, manipr, rstart, rstop, nsteps,
                              invert=detector_on_manip, max_channel=max_channel)
    _, roffset = ret[0]
    print(roffset)
    return roffset


def scan_r_coarse():
    return (yield from scan_r_offset(-10, 10, 1))


def scan_r_medium():
    return (yield from scan_r_offset(-2, 2, 0.1))


def scan_r_fine():
    return (yield from scan_r_offset(-0.5, 0.5, 0.05))


def scan_x_offset(xstart, xstop, step_size):
    nsteps = int(np.abs(xstop - xstart)/step_size) + 1
    ret = yield from find_max_deriv(rel_scan, det_devices, manipx, xstart, xstop,
                                    nsteps, max_channel=max_channel)
    _, xoffset = ret[0]
    print(xoffset)
    return xoffset


def scan_x_coarse():
    """
    Find x to within 1 mm, initial misalignment can be +- 7 mm
    """
    return (yield from scan_x_offset(-7, 7, 1))


def scan_x_medium():
    """
    Find x to within 0.25 mm, Initial misalignment can be +- 2 mm
    """
    return (yield from scan_x_offset(-2, 2, 0.25))


def scan_x_fine():
    """
    Find x to within 0.05 mm, Initial misalignment can be +- 0.5 mm
    """
    return (yield from scan_x_offset(-0.5, 0.5, 0.05))


def find_x_offset(precision=0.25, refine=False):
    ret = yield from find_x_adaptive(precision=precision)
    if refine:
        ret = yield from scan_x_fine()
    print(f"Found edge at {ret}")
    return ret


def find_z_offset(precision=0.25, refine=True):
    """
    Find z-offset of manipulator. Manipulator should start
    out of the beam
    """
    zoffset = yield from find_z_adaptive(precision=precision)
    if refine:
        zoffset = yield from scan_z_fine()
    print(f"Found edge at {zoffset}")
    return zoffset


def find_r_offset():
    yield from scan_r_offset(-10, 10, 1)
    ret = yield from scan_r_offset(-1, 1, 0.1)
    print(f"Found angle at {ret}")
    return ret


def find_edge_adaptive(dets, motor, step, precision, max_channel=None):
    """
    Parameters
    -----------
    dets : list
    motor : Ophyd device
    step : float
        step size to move motor that will make det go from low to high signal
    precision : float
        desired precision of edge position
    """
    if max_channel is None:
        detname = dets[0].name
    else:
        detname = max_channel
    if detname not in thresholds:
        raise KeyError(f"{detname} has no threshold value and cannot be"
                       "used with an adaptive plan")
    thres_pos = yield from threshold_adaptive(dets, motor,
                                              thresholds[detname],
                                              step=step, max_channel=max_channel)
    yield from mvr(motor, step)
    return (yield from halfmax_adaptive(dets, motor, -1*step,
                                        precision=precision, max_channel=max_channel))



def find_z_adaptive(precision=0.1, step=2):
    """
    detector should start low
    step : float
        step size to move motor that will make det go from low to high signal
    precision : float
        desired precision of edge position
    """

    return (yield from find_edge_adaptive(det_devices, manipz, step, precision,
                                          max_channel=max_channel))


def find_x_adaptive(precision=0.1, step=2):
    """
    detector should start low
    step : float
        step size to move motor that will make det go from low to high signal
    precision : float
        desired precision of edge position
    """
    return (yield from find_edge_adaptive(det_devices, manipx, step, precision,
                                          max_channel=max_channel))


def find_edge(dets, motor, step, start, stop, points, max_channel=None):
    """
    Parameters
    -----------
    dets : list
    motor : Ophyd device
    step : float
        step size to move motor that will make det go from low to high signal
    precision : float
        desired precision of edge position
    """
    if max_channel is None:
        detname = dets[0].name
    else:
        detname = max_channel
    if detname not in thresholds:
        raise KeyError(f"{detname} has no threshold value and cannot be"
                       "used with an adaptive plan")
    thres_pos = yield from threshold_adaptive(dets, motor,
                                              thresholds[detname],
                                              step=step, max_channel=max_channel)
    yield from mv(motor, thres_pos)
    ret = (yield from find_halfmax(rel_scan, dets, motor, start, stop, points,
                                    max_channel=max_channel))
    return ret[0][1]

def find_x(invert=False, precision=0.1):
    print("Finding x edge position")
    if invert:
        step = -1
        start = 2
        stop = -2
    else:
        step = 1
        start = -2
        stop = 2
    points = int(np.abs(start - stop)/precision) + 1
    return (yield from find_edge(det_devices, manipx, step, start, stop, points, max_channel=max_channel))

def find_z(invert=False, precision=0.1):
    print("Finding z edge position")
    if invert:
        step = -1
        start = -2
        stop = 2
    else:
        step = 1
        start = -2
        stop = 2
    points = int(np.abs(start - stop)/precision) + 1
    return (yield from find_edge(det_devices, manipz, step, start, stop, points, max_channel=max_channel))

