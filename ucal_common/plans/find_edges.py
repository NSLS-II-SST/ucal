import numpy as np
from ucal_common.motors import manipx, manipy, manipz, manipr
from ucal_common.detectors import sc, thresholds
from bl_funcs.plans.maximizers import find_max_deriv, find_max, halfmax_adaptive, threshold_adaptive
from bluesky.plan_stubs import mv, mvr
from bluesky.plans import rel_scan

# This should go into a beamline config file at some point
alignment_detector = [sc]
# If we have a drain current detector on the manipulator,
# as opposed to a detector that the manipulator shadows,
# we will need to invert some of the maximum finding routines
detector_on_manip = True

def scan_z_offset(zstart, zstop, step_size):
    nsteps = int(np.abs(zstop - zstart)/step_size) + 1
    ret = yield from find_max_deriv(rel_scan, alignment_detector, manipz, zstart, zstop,
                                    nsteps)
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
    ret = yield from find_max(rel_scan, alignment_detector, manipr, rstart, rstop, nsteps,
                              invert=detector_on_manip)
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
    ret = yield from find_max_deriv(rel_scan, alignment_detector, manipx, xstart, xstop,
                                    nsteps)
    _, xoffset = ret[0]
    print(xoffset)
    return xoffset


def scan_x_coarse():
    """
    Find x to within 1 mm, initial misalignment can be +- 10 mm
    """
    return (yield from scan_x_offset(-10, 10, 1))


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


def find_x_offset():
    yield from find_x_adaptive(precision=0.25)
    ret = yield from scan_x_fine()
    print(f"Found edge at {ret}")
    return ret


def find_z_offset():
    yield from find_z_adaptive(precision=0.25)
    zoffset = yield from scan_z_fine()
    print(f"Found edge at {zoffset}")
    return zoffset


def find_r_offset():
    yield from scan_r_offset(-10, 10, 1)
    ret = yield from scan_r_offset(-1, 1, 0.1)
    print(f"Found angle at {ret}")
    return ret


def find_edge_adaptive(dets, motor, step, precision):
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
    main_det = dets[0]
    if main_det.name not in thresholds:
        raise KeyError(f"{main_det.name} has no threshold value and cannot be"
                       "used with an adaptive plan")
    thres_pos = yield from threshold_adaptive(dets, motor,
                                              thresholds[main_det.name],
                                              step=step)
    yield from mvr(motor, step)
    return (yield from halfmax_adaptive(dets, motor, -1*step,
                                        precision=precision))


def find_z_adaptive(precision=0.1):
    return (yield from find_edge_adaptive(alignment_detector, manipz, 2, precision))


def find_x_adaptive(precision=0.1):
    return (yield from find_edge_adaptive(alignment_detector, manipx, 2, precision))
