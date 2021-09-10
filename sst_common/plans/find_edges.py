import numpy as np
from sst_common.motors import samplex, sampley, samplez, sampler
from sst_common.detectors import i1
from sst_base.maximizers import find_max_deriv, find_max
from bluesky.plan_stubs import mv, mvr
from bluesky.plans import rel_scan


def scan_z_offset(zstart, zstop, step_size):
    nsteps = int(np.abs(zstop - zstart)/step_size) + 1
    ret = yield from find_max_deriv(rel_scan, [i1], samplez, zstart, zstop,
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
    ret = yield from find_max(rel_scan, [i1], sampler, rstart, rstop, nsteps)
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
    ret = yield from find_max_deriv(rel_scan, [i1], samplex, xstart, xstop,
                                    nsteps)
    _, xoffset = ret[0]
    print(xoffset)
    return xoffset


def scan_x_coarse():
    """
    Initial misalignment can be +- 10 degrees
    """
    return (yield from scan_x_offset(-10, 10, 0.5))


def scan_x_medium():
    """
    Initial misalignment can be +- 2 degrees
    """
    return (yield from scan_x_offset(-2, 2, 0.2))


def scan_x_fine():
    return (yield from scan_x_offset(-0.5, 0.5, 0.05))


def find_x_offset():
    yield from scan_x_medium()
    ret = yield from scan_x_fine()
    print(f"Found edge at {ret}")
    return ret


def find_z_offset():
    yield from scan_z_medium()
    zoffset = yield from scan_z_fine()
    print(f"Found edge at {zoffset}")
    return zoffset


def find_r_offset():
    yield from scan_r_offset(-10, 10, 1)
    ret = yield from scan_r_offset(-1, 1, 0.1)
    print(f"Found angle at {ret}")
    return ret
