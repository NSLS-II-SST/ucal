from bluesky.plan_stubs import mv, mvr
# from bluesky.utils import Msg
from sst_common.motors import samplex, samplez, sampler
from sst_common.plans.find_edges import (scan_r_coarse, scan_r_medium,
                                   scan_x_coarse, scan_x_medium, scan_x_fine,
                                   find_x_offset, find_z_offset)
from sst_base.linalg import deg_to_rad, rad_to_deg, rotz, vec
import numpy as np

# need to fix imports, test, etc, actually hook up the max logic, and do a
# derivative scan version
# figure out if I can use bluesky-live instead? See thread


def find_corner_x_r():
    """
    finds the rotation that makes a side parallel to the beam, and the
    x-coordinate of the surface
    """
    yield from scan_x_coarse()
    yield from scan_r_coarse()
    yield from scan_x_medium()
    theta = yield from scan_r_medium()
    x = yield from scan_x_fine()
    return np.abs(x), theta


def find_corner_coordinates(nsides=4):
    # rotation angle to next side
    ra = 360.0/nsides

    x1, r1 = yield from find_corner_x_r()
    yield from mvr(sampler, ra)
    x2, r2 = yield from find_corner_x_r()

    y1 = calculate_corner_y(x1, r1, x2, r2, nsides)
    print(f"x1: {x1}, y1: {y1}, r1: {r1}")
    return x1, y1, r1, r2


def calculate_corner_y(x1, r1, x2, r2, nsides=4):
    x1 = np.abs(x1)
    x2 = np.abs(x2)
    theta1 = deg_to_rad(r1)
    # interior angle for a regular polygon
    ia = deg_to_rad(180.0*(nsides - 2)/nsides)
    phi1 = np.arctan(np.sin(ia)/(x2/x1 + np.cos(ia)))
    y1 = x1/np.tan(phi1)
    return y1


def find_corner_known_rotation(r1, r2, nsides=4):
    yield from mv(sampler, r2)
    x2 = yield from find_x_offset()
    yield from mv(sampler, r1)
    x1 = yield from find_x_offset()
    y1 = calculate_corner_y(x1, r1, x2, r2, nsides)
    x2 = np.abs(x2)
    x1 = np.abs(x1)
    y1 = np.abs(y1)
    print(f"Corners known rotation x1: {x1}, y1: {y1}")
    return x1, y1


def find_side_basis(nsides=4):
    z = yield from find_z_offset()
    yield from mvr(samplez, -5)
    x1, y1, r1, r2 = yield from find_corner_coordinates(nsides)
    yield from mvr(samplez, -90)
    (x3, y3) = yield from find_corner_known_rotation(r1, r2, nsides)
    yield from mv(samplez, z)
    # fudging origin a bit so that it is z, not z + 5
    p1 = vec(x1, -y1, z)
    # still want correct height difference between points
    p2 = vec(x3, -y3, z + 95)
    p3 = vec(x1, -y1 + 10, z)

    theta1 = -1*deg_to_rad(r1)
    p1r = rotz(theta1, p1)
    p2r = rotz(theta1, p2)
    p3r = rotz(theta1, p3)
    print("Points ", p1, p2, p3)
    print("Rotated points ", p1r, p2r, p3r)
    return p1r, p2r, p3r


def calibrate_side(side_num, nsides=4):
    p1, p2, p3 = yield from find_side_basis(nsides)
    raise NotImplementedError
    # yield Msg("calibrate", sample_holder, side_num, p1, p2, p3)
