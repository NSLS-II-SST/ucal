from bluesky.plan_stubs import mv, mvr

# from bluesky.utils import Msg
from ucal.hw import manipx, manipy, manipz, manipr, manipulator
from ucal.hw import tesz
from ucal.plans.find_edges import (
    scan_r_coarse,
    scan_r_medium,
    scan_x_coarse,
    scan_x_medium,
    scan_x_fine,
    find_x_offset,
    find_z_offset,
    find_x_adaptive,
    find_x,
    find_z,
)

from ucal.plans.samples import set_side
from nbs_bl.samples import move_sample
from ucal.plans.plan_stubs import update_manipulator_side

# from ucal.configuration import beamline_config
from nbs_bl.queueserver import GLOBAL_USER_STATUS
from nbs_bl.help import add_to_plan_list
from nbs_bl.geometry.linalg import deg_to_rad, rad_to_deg, rotz, vec
from nbs_bl.geometry.frames import Frame
from nbs_bl.printing import boxed_text
from bluesky.plan_stubs import rd
from bluesky.utils import RequestAbort
import numpy as np

# need to fix imports, test, etc, actually hook up the max logic, and do a
# derivative scan version
# figure out if I can use bluesky-live instead? See thread
MANIPULATOR_CONFIG = GLOBAL_USER_STATUS.request_status_dict(
    "MANIPULATOR_CONFIG", use_redis=True
)


def find_min_r(step, npts):
    xlist = []
    rcurr = manipr.position

    rlist = [rcurr + n * step - step * (npts - 1) / 2 for n in range(npts)]
    for r in rlist:
        yield from mv(manipr, r)
        x = yield from find_x()
        xlist.append(x)
    minr = rlist[np.argmax(xlist)]
    return minr


def find_r_offset():
    """
    Works to find angle where bar is square to beam. Maybe want to subtract 0.5 deg
    from result for safety, better not to have exposed 2nd side
    """
    minr = yield from find_min_r(2, 9)
    yield from mv(manipr, minr)
    minr2 = yield from find_min_r(0.5, 9)
    return minr2


def find_beam_x_offset(side=1, rdiff=180):
    tes_pos = yield from rd(tesz)
    if tes_pos < 40:
        print("TES too close, move back to 40 mm to continue")
        raise RequestAbort
    yield from set_side(side)
    # We want to move off the sample
    yield from move_sample(None, x=-1, y=5, r=5)
    x1 = yield from find_x()
    yield from move_sample(None, x=-1, y=5, r=5 + rdiff)
    x2 = yield from find_x(invert=True)
    yield from mv(manipr, 0, manipx, 0)
    return (x1 + x2) * 0.5


@add_to_plan_list
def calibrate_beam_offset(*args, **kwargs):
    x = yield from find_beam_x_offset(*args, **kwargs)
    set_manipulator_origin(x=x)
    return x


def find_corner_x_r():
    """
    finds the rotation that makes a side parallel to the beam, and the
    x-coordinate of the surface
    """
    yield from find_x_offset(refine=False)
    yield from scan_r_coarse()
    yield from scan_x_medium()
    theta = yield from scan_r_medium()
    x = yield from scan_x_fine()
    return x, theta


def find_corner_coordinates(nsides=4):
    # rotation angle to next side
    ra = 360.0 / nsides

    x1, r1 = yield from find_corner_x_r()
    yield from mvr(manipr, ra)
    x2, r2 = yield from find_corner_x_r()

    y1 = calculate_corner_y(x1, r1, x2, r2, nsides)
    print(f"x1: {x1}, y1: {y1}, r1: {r1}")
    return x1, y1, r1, r2


def calculate_corner_y(x1, r1, x2, r2, nsides=4):
    x1 = np.abs(x1)
    x2 = np.abs(x2)

    theta1 = deg_to_rad(r1)
    # interior angle for a regular polygon
    ia = deg_to_rad(180.0 * (nsides - 2) / nsides)
    phi1 = np.arctan(np.sin(ia) / (x2 / x1 + np.cos(ia)))
    y1 = x1 / np.tan(phi1)
    return y1


def find_corner_known_rotation(r1, r2, nsides=4):
    yield from mv(manipr, r1)
    x1 = yield from find_x()
    yield from mv(manipr, r2)
    x2 = yield from find_x()
    y1 = calculate_corner_y(x1, r1, x2, r2, nsides)
    print(f"Corners known rotation x1: {x1}, y1: {y1}")
    return x1, y1


def find_side_basis(nsides=4, x1=None, r1=None, x3=None, z=None, find_angle=False):
    """
    Efficiently finds the side basis and leaves manipulator ready for
    the next side
    """
    ra = 360.0 / nsides
    z_bump = 5
    if z is None:
        z = yield from find_z()
    z2 = z + 90
    x0 = manipulator.origin[0]
    z0 = manipulator.origin[2]
    next_side = {}
    yield from mv(manipz, z + z_bump)
    if x1 is None or r1 is None:
        if find_angle:
            print("Finding x1, r1")
            x1, r1 = yield from find_corner_x_r()
        else:
            print("Finding x1 only")
            x1 = yield from find_x()
            r1 = manipr.position
        x1 -= x0
        x1 = np.abs(x1)
    yield from mv(manipz, z2 + z_bump)
    if x3 is None:
        print("Finding x3")
        yield from mv(manipr, r1)
        x3 = yield from find_x()
        x3 -= x0
        x3 = np.abs(x3)
    yield from mv(manipr, r1 + ra)
    if find_angle:
        print("Finding x4, r2")
        x4, r2 = yield from find_corner_x_r()
    else:
        print("Finding x4 only")
        x4 = yield from find_x()
        r2 = r1 + ra
    next_side["r1"] = r2
    x4 -= x0
    x4 = np.abs(x4)
    next_side["x3"] = x4
    yield from mv(manipz, z + z_bump)
    yield from mv(manipr, r2)
    print("Finding x2")
    x2 = yield from find_x()
    x2 -= x0
    x2 = np.abs(x2)
    next_side["x1"] = x2

    y1 = calculate_corner_y(x1, r1, x2, r2, nsides)
    y3 = calculate_corner_y(x3, r1, x4, r2, nsides)

    # Move manipulator back into place
    yield from mv(manipz, z)
    # Note, assumes a certain side to calibrate on!
    yield from mvr(manipx, 2)
    try:
        boxed_text(
            "Raw positions",
            map(
                lambda x: "{x[0]}: {x[1]}".format(x=x),
                [
                    ("x1", x1),
                    ("y1", y1),
                    ("x3", x3),
                    ("y3", y3),
                    ("z", z),
                    ("z2", z2),
                    ("r1", r1),
                    ("z0", z0),
                ],
            ),
            "white",
        )
    except:
        print(x1, y1, x3, y3, z, z2, r1, z0)
    points = find_side_points(x1, y1, x3, y3, z, z2, r1, vec(0, 0, z0))
    # Points we can plug into the basis for the next side
    next_side = {"x1": x2, "r1": r2, "x3": x4}
    return points, next_side


def find_side_points(x1, y1, x3, y3, z1, z3, r1, origin=0):
    p1 = origin + vec(x1, y1, -z1)
    p2 = origin + vec(x3, y3, -z3)
    p3 = origin + vec(x1, y1 - 1, -z1)

    theta1 = deg_to_rad(r1)
    p1r = rotz(theta1, p1)
    p2r = rotz(theta1, p2)
    p3r = rotz(theta1, p3)
    return p1r, p2r, p3r


def calibrate_side(side_num, nsides=4):
    p1, p2, p3 = yield from find_side_basis(nsides)
    yield from update_manipulator_side(side_num, p1, p2, p3)
    # yield Msg("calibrate", sample_holder, side_num, p1, p2, p3)


@add_to_plan_list
def calibrate_sides(side_start, side_end, nsides=4):
    yield from mv(manipr, 0, manipx, 0)
    z = yield from find_z()
    previous_side = {}
    for side in range(side_start, side_end + 1):
        yield from set_side(side)
        yield from move_sample(None, 0, 0, 0)
        points, previous_side = yield from find_side_basis(nsides, **previous_side, z=z)
        yield from update_manipulator_side(side, *points)


def set_manipulator_origin(*, x=None, y=None, z=None, r=None):
    """Set the manipulator origin coordinates"""
    updates = [x, y, z, r]
    if np.any(updates) is None and "origin" in MANIPULATOR_CONFIG:
        print("No updates")
        manipulator.origin = np.array(MANIPULATOR_CONFIG["origin"])
    else:
        for i, val in enumerate([x, y, z, r]):
            if val is not None:
                print(f"Setting origin {i} to {val}")
                manipulator.origin[i] = val
        MANIPULATOR_CONFIG["origin"] = list(manipulator.origin)


def new_calibrate_sides(side_start, side_end, nsides=4, findz=True, preserve=False):
    """Calibrate multiple manipulator sides"""
    if not preserve:
        MANIPULATOR_CONFIG["calibration"] = {}

    if findz:
        yield from mv(manipr, 0, manipx, 0)
        z = yield from find_z()
    else:
        z = manipz.position
    z0 = manipulator.origin[2]
    x0 = manipulator.origin[0]
    bump = 5
    z1 = z + bump
    z2 = z1 + 100
    xr1 = yield from find_sides_one_z(z1, side_start, side_end, nsides)
    xr2 = yield from find_sides_one_z(z2, side_start, side_end, nsides)
    for n, side in enumerate(range(side_start, side_end + 1)):
        x1, r1 = xr1[n]
        x2, r2 = xr1[n + 1]
        x3, _ = xr2[n]
        x4, _ = xr2[n + 1]
        y1 = calculate_corner_y(x1, r1, x2, r2, nsides)
        y3 = calculate_corner_y(x3, r1, x4, r2, nsides)
        try:
            boxed_text(
                "Raw positions",
                map(
                    lambda x: "{x[0]}: {x[1]}".format(x=x),
                    [
                        ("x1", x1),
                        ("y1", y1),
                        ("x3", x3),
                        ("y3", y3),
                        ("z", z),
                        ("z2", z2),
                        ("r1", r1),
                        ("z0", z0),
                    ],
                ),
                "white",
            )
        except:
            print(x1, y1, x3, y3, z, z2, r1, z0)
        points = find_side_points(x1, y1, x3, y3, z, z2, r1, vec(0, 0, z0))
        if "calibration" not in MANIPULATOR_CONFIG:
            MANIPULATOR_CONFIG["calibration"] = {}
        MANIPULATOR_CONFIG["calibration"][f"{side}"] = points
        yield from update_manipulator_side(side, *points)


def load_saved_manipulator_calibration():
    """Load saved manipulator calibration from Redis"""
    if "calibration" in MANIPULATOR_CONFIG:
        for side, points in MANIPULATOR_CONFIG["calibration"].items():
            yield from update_manipulator_side(int(side), *points)
    if "origin" in MANIPULATOR_CONFIG:
        set_manipulator_origin()


def find_sides_one_z(z, side_start, side_end, nsides):
    xr_list = []
    x0 = manipulator.origin[0]
    for side in range(side_start, side_end + 1):
        yield from set_side(side)
        yield from mv(manipz, z)
        y = manipulator.sy.position
        yield from move_sample(None, 0, y, 0)
        x = yield from find_x()
        r = manipr.position
        x -= x0
        x = np.abs(x)
        xr_list.append((x, r))
    if side == nsides:
        if side_start == 1:
            xr_list.append(xr_list[0])
        else:
            yield from mvr(manipr, 90)
            yield from set_side(1)
            y = manipulator.sy.position
            yield from move_sample(None, 0, y, 0)
            x = yield from find_x()
            r = manipr.position
            x -= x0
            x = np.abs(x)
            xr_list.append((x, r))
    else:
        yield from set_side(side + 1)
        yield from mv(manipz, z)
        y = manipulator.sy.position
        yield from move_sample(None, 0, y, 0)
        x = yield from find_x()
        r = manipr.position
        x -= x0
        x = np.abs(x)
        xr_list.append((x, r))
    return xr_list


def get_manual_sample_frame(x, y, z, r):
    rmod = r % 90
    rdiv = r - rmod
    z0 = manipulator.origin[2]
    x0 = manipulator.origin[0]
    pr = rotz(np.pi * rmod / 180.0, vec(-(x - x0), -y, z))
    points = find_side_points(pr[0], pr[1], pr[0], pr[1], z, z + 1, rdiv, vec(0, 0, z0))
    frame = Frame(points[0], points[1], points[2])
    return frame
