# from sst_common.api import *
import pytest
import ucal
import numpy as np
ucal.STATION_NAME = "sst_sim"
from ucal.motors import manipx, manipy, manipz, manipr
from ucal.detectors import i1, sc, thresholds
from ucal.plans.find_edges import (scan_z_medium, find_x_offset,
                                   find_r_offset,
                                   scan_r_medium, scan_r_fine,
                                   scan_r_coarse, find_z_adaptive,
                                   find_x_adaptive)
from ucal.plans.alignment import (find_corner_x_r,
                                         find_corner_coordinates,
                                         efficient_find_side_basis,
                                         find_beam_x_offset)
from sst_funcs.plans.maximizers import halfmax_adaptive, threshold_adaptive
from sst_funcs.geometry.frames import Frame
from bluesky.plan_stubs import mvr


def isclose(a, b, precision):
    return (a >= b - precision) & (a <= b + precision)


def test_scan_z_finds_edge(RE, fresh_manipulator):
    z_origin = fresh_manipulator.forward(0, 0, 0, 0).z
    z_offset = RE(scan_z_medium()).plan_result
    assert isclose(z_offset, z_origin, 0.05)
    manipz.set(z_origin + 1)
    z_offset2 = RE(scan_z_medium()).plan_result
    assert isclose(z_offset2, z_origin, 0.05)


def test_find_x_adaptive(RE, fresh_manipulator):
    manipx.set(-1)
    x_offset = RE(find_x_adaptive()).plan_result
    assert isclose(x_offset, -5, 0.1)
    manipx.set(-3)
    x_offset = RE(find_x_adaptive()).plan_result
    assert isclose(x_offset, -5, 0.1)
    manipx.set(-10)
    x_offset = RE(find_x_adaptive()).plan_result
    assert isclose(x_offset, -5, 0.1)


def test_find_x_offset(RE, fresh_manipulator):
    manipx.set(-1)
    x_offset = RE(find_x_offset()).plan_result
    assert isclose(x_offset, -5, 0.05)
    manipx.set(-3)
    x_offset = RE(find_x_offset()).plan_result
    assert isclose(x_offset, -5, 0.05)
    manipx.set(-10)
    x_offset = RE(find_x_offset()).plan_result
    assert isclose(x_offset, -5, 0.05)
    manipr.set(45)
    x_offset = RE(find_x_offset()).plan_result
    # Find diagonal with tolerance of 0.05
    assert isclose(x_offset, -np.sqrt(50), 0.05)


def test_find_r_offset(RE, fresh_manipulator):
    manipx.set(-3)
    manipr.set(1)
    RE(find_x_offset())
    theta = RE(find_r_offset()).plan_result
    assert isclose(theta, 0, 0.1)
    manipr.set(10)
    theta = RE(find_r_offset()).plan_result
    assert isclose(theta, 0, 0.1)


@pytest.mark.parametrize('n', range(5))
def test_random_offset(RE, random_angle_manipulator, n):
    _, angle = random_angle_manipulator
    manipx.set(-3)
    RE(find_x_offset())
    angle2 = RE(find_r_offset()).plan_result
    assert isclose(angle, angle2, 0.1)


@pytest.mark.parametrize('angle', [1, 2, 4, 6, 8])
def test_find_corner_x_r(RE, fresh_manipulator, angle):
    manipr.set(angle)
    x, theta = RE(find_corner_x_r()).plan_result
    assert isclose(np.abs(x), 5, 0.1)
    assert isclose(theta, 0, 0.1)
    # print(f"theta: {theta}")


def test_corner_coordinates(RE, fresh_manipulator):
    manipx.set(-3)
    manipr.set(4)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, 0, 0.1)
    assert isclose(r2, 90, 0.1)
    assert isclose(np.abs(x1), 5, 0.1)
    assert isclose(y1, 5, 0.1)

    manipr.set(87)
    manipx.set(-3)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, 90, 0.1)
    assert isclose(r2, 180, 0.1)
    assert isclose(np.abs(x1), 5, 0.1)
    assert isclose(y1, 5, 0.1)


def test_random_corner_coordinates(RE, random_angle_manipulator):
    manipulator, angle = random_angle_manipulator
    w = manipulator.holder.sides[0].width/2.0
    manipx.set(-3)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, angle, 0.1)
    assert isclose(r2, 90 + angle, 0.1)
    assert isclose(np.abs(x1), w, 0.1)
    assert isclose(y1, w, 0.1)

    manipr.set(90)
    manipx.set(-3)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, 90 + angle, 0.1)
    assert isclose(r2, 180 + angle, 0.1)
    assert isclose(np.abs(x1), w, 0.1)
    assert isclose(y1, w, 0.1)


@pytest.mark.parametrize("precision", [1, 0.5, 0.1, 0.01])
def test_halfmax_adaptive(RE, fresh_manipulator, precision):
    z_origin = fresh_manipulator.forward(0, 0, 0, 0).z
    manipz.set(z_origin + 4)
    z = RE(halfmax_adaptive([sc], manipz, -5, precision)).plan_result
    assert isclose(z, z_origin, precision)


def test_threshold_adaptive(RE, fresh_manipulator):
    z_origin = fresh_manipulator.forward(0, 0, 0, 0).z
    manipz.set(z_origin - 2)
    z = RE(threshold_adaptive([sc], manipz, thresholds['sc'],
                              step=2)).plan_result
    assert z == z_origin
    manipz.set(z_origin+4)
    z2 = RE(threshold_adaptive([sc], manipz, thresholds['sc'],
                               step=-2)).plan_result
    assert z2 >= z_origin
    manipz.set(z_origin-2)
    with pytest.raises(ValueError):
        RE(threshold_adaptive([sc], manipz, thresholds['sc'], step=-2))


def test_find_z_adaptive(RE, fresh_manipulator):
    z_origin = fresh_manipulator.forward(0, 0, 0, 0).z
    manipz.set(z_origin - 2)
    z = RE(find_z_adaptive()).plan_result
    assert isclose(z, z_origin, 0.1)

    manipz.set(z_origin - 10)
    z = RE(find_z_adaptive()).plan_result
    assert isclose(z, z_origin, 0.1)

    manipz.set(z_origin+10)
    z = RE(find_z_adaptive()).plan_result
    assert isclose(z, z_origin, 0.1)


@pytest.mark.parametrize('angle', [1, 2, 4, 6])
def test_one_side_alignment(RE, fresh_manipulator, angle):
    z_origin = fresh_manipulator.forward(0, 0, 0, 0).z
    manipz.set(z_origin - 2)
    manipr.set(angle)
    next_side = {}
    for n, s in enumerate(fresh_manipulator.holder.sides):
        points, next_side = RE(efficient_find_side_basis(**next_side)).plan_result
        f = Frame(*points)
        print(f"Checking side {n}")
        for fb, sb in zip(f._basis, s._basis):
            print(f"Does {fb} equal {sb}")
            assert np.all(isclose(fb, sb, 0.1))


@pytest.mark.parametrize('offset', [1, 2, 4])
def test_find_beam_offset(RE, fresh_manipulator, offset):
    z_origin = fresh_manipulator.forward(0, 0, 0, 0).z
    manipz.set(z_origin - 2)
    fresh_manipulator.origin[0] = offset
    x = RE(find_beam_x_offset()).plan_result
    assert isclose(x, offset, 0.1)


def test_crazy_alignment(RE, crazy_manipulator):
    z_origin = crazy_manipulator.forward(0, 0, 0, 0).z
    manipz.set(z_origin - 2)
    manipx.set(-3)
    crazy_manipulator.origin[0] = -2
    next_side = {}
    for n, s in enumerate(crazy_manipulator.holder.sides):
        points, next_side = RE(efficient_find_side_basis(**next_side)).plan_result
        f = Frame(*points)
        print(f"Checking side {n}")
        for fb, sb in zip(f._basis, s._basis):
            print(f"Does {fb} equal {sb}")
            assert np.all(isclose(fb, sb, 0.1))
