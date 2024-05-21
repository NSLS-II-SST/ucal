import numpy as np
from ucal.hw import manipx, manipy, manipz, manipr
from nbs_bl.globalVars import GLOBAL_ACTIVE_DETECTORS, GLOBAL_DETECTOR_THRESHOLDS, GLOBAL_ALIGNMENT_DETECTOR
from nbs_bl.plans.maximizers import (
    find_max_deriv,
    find_max,
    halfmax_adaptive,
    threshold_adaptive,
    find_halfmax,
)
from bluesky.plan_stubs import mv, mvr
from bluesky.plans import rel_scan
from nbs_bl.plans.flyscan_base import fly_scan

# This should go into a beamline config file at some point
# max_channel = i1.name
# If we have a drain current detector on the manipulator,
# as opposed to a detector that the manipulator shadows,
# we will need to invert some of the maximum finding routines
# detector_on_manip = False


def get_alignment_det():
    """
    Returns detector to use for alignment
    """
    if 'indirect' in GLOBAL_ALIGNMENT_DETECTOR:
        return GLOBAL_ALIGNMENT_DETECTOR['indirect'].name
    elif 'direct' in GLOBAL_ALIGNMENT_DETECTOR:
        return GLOBAL_ALIGNMENT_DETECTOR['direct'].name
    else:
        raise KeyError("Neither indirect nor direct Alignment Detector Found, not guessing!")


def invert_alignment():
    """
    Returns True if the detector maximum occurs when the sample is in the beam
    """
    if 'indirect' in GLOBAL_ALIGNMENT_DETECTOR:
        return False
    elif 'direct' in GLOBAL_ALIGNMENT_DETECTOR:
        return True
    else:
        raise KeyError("Neither indirect nor direct Alignment Detector Found, not guessing!")


def scan_z_offset(zstart, zstop, step_size):
    nsteps = int(np.abs(zstop - zstart) / step_size) + 1
    max_channel = get_alignment_det()
    ret = yield from find_max_deriv(
        rel_scan,
        GLOBAL_ACTIVE_DETECTORS,
        manipz,
        zstart,
        zstop,
        nsteps,
        max_channel=max_channel,
    )
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
    nsteps = int(np.abs(rstop - rstart) / step_size) + 1
    max_channel = get_alignment_det()
    invert = invert_alignment()
    ret = yield from find_max(
        rel_scan,
        GLOBAL_ACTIVE_DETECTORS,
        manipr,
        rstart,
        rstop,
        nsteps,
        invert=invert,
        max_channel=max_channel,
    )
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
    nsteps = int(np.abs(xstop - xstart) / step_size) + 1
    max_channel = get_alignment_det()

    ret = yield from find_max_deriv(
        rel_scan,
        GLOBAL_ACTIVE_DETECTORS,
        manipx,
        xstart,
        xstop,
        nsteps,
        max_channel=max_channel,
    )
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
    if detname not in GLOBAL_DETECTOR_THRESHOLDS:
        raise KeyError(
            f"{detname} has no threshold value and cannot be"
            "used with an adaptive plan"
        )
    thres_pos = yield from threshold_adaptive(
        dets,
        motor,
        GLOBAL_DETECTOR_THRESHOLDS[detname],
        step=step,
        max_channel=max_channel,
    )
    yield from mvr(motor, step)
    return (
        yield from halfmax_adaptive(
            dets, motor, -1 * step, precision=precision, max_channel=max_channel
        )
    )


def find_z_adaptive(precision=0.1, step=2):
    """
    detector should start low
    step : float
        step size to move motor that will make det go from low to high signal
    precision : float
        desired precision of edge position
    """
    max_channel = get_alignment_det()
    return (
        yield from find_edge_adaptive(
            GLOBAL_ACTIVE_DETECTORS, manipz, step, precision, max_channel=max_channel
        )
    )


def find_x_adaptive(precision=0.1, step=2):
    """
    detector should start low
    step : float
        step size to move motor that will make det go from low to high signal
    precision : float
        desired precision of edge position
    """
    max_channel = get_alignment_det()
    return (
        yield from find_edge_adaptive(
            GLOBAL_ACTIVE_DETECTORS, manipx, step, precision, max_channel=max_channel
        )
    )


def find_edge(dets, motor, step, start, stop, points, max_channel=None, fly=True):
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
    if detname not in GLOBAL_DETECTOR_THRESHOLDS:
        raise KeyError(
            f"{detname} has no threshold value and cannot be"
            "used with an adaptive plan"
        )
    thres_pos = yield from threshold_adaptive(
        dets,
        motor,
        GLOBAL_DETECTOR_THRESHOLDS[detname],
        step=step,
        max_channel=max_channel,
    )
    print(f"Found Threshold {thres_pos} for {motor.name}, moving to {thres_pos + start}")
    yield from mv(motor, thres_pos + start)
    if fly:
        ret = yield from find_halfmax(
            fly_scan,
            dets,
            motor,
            thres_pos + start,
            thres_pos + stop,
            max_channel=max_channel,
            period=0.2,
        )
    else:
        ret = yield from find_halfmax(
            rel_scan, dets, motor, 0, stop - start, points, max_channel=max_channel
        )
    print(f"Found halfmax {ret[0][1]} for {motor.name}")
    return ret[0][1]


def find_x(invert=False, precision=0.1):
    print("Finding x edge position")
    max_channel = get_alignment_det()

    # What an awful piece of historical code
    if not invert_alignment():
        invert = not invert

    if invert:
        step = -1
        start = 2
        stop = -2
    else:
        step = 1
        start = -2
        stop = 2
    points = int(np.abs(start - stop) / precision) + 1
    return (
        yield from find_edge(
            GLOBAL_ACTIVE_DETECTORS,
            manipx,
            step,
            start,
            stop,
            points,
            max_channel=max_channel,
        )
    )


def find_z(invert=False, precision=0.1):
    """Find the z edge position"""
    print("Finding z edge position")
    if not invert_alignment():
        invert = not invert

    if invert:
        step = -1
        start = 2
        stop = -2
    else:
        step = 1
        start = -2
        stop = 2
    points = int(np.abs(start - stop) / precision) + 1
    return (
        yield from find_edge(
            GLOBAL_ACTIVE_DETECTORS,
            manipz,
            step,
            start,
            stop,
            points,
            max_channel=max_channel,
        )
    )
