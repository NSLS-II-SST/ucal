# from sst_common.api import *
import pytest
import sst_common
import numpy as np
sst_common.STATION_NAME = "sst_sim"
from sst_common.motors import samplex, sampley, samplez, sampler
from sst_common.detectors import i1, thresholds
from sst_common.plans.find_edges import (scan_z_medium, find_x_offset,
                                         find_r_offset,
                                         scan_r_medium, scan_r_fine,
                                         scan_r_coarse, find_z_adaptive,
                                         find_x_adaptive)
from sst_common.plans.alignment import find_corner_x_r, find_corner_coordinates
from bl_funcs.plans.maximizers import halfmax_adaptive, threshold_adaptive
from bluesky.plan_stubs import mvr


def isclose(a, b, precision):
    return (a >= b - precision) and (a <= b + precision)


def test_scan_z_finds_edge(RE, fresh_manipulator):
    z_offset = RE(scan_z_medium()).plan_result
    assert isclose(z_offset, 0, 0.05)
    samplez.set(-1)
    z_offset2 = RE(scan_z_medium()).plan_result
    assert isclose(z_offset2, 0, 0.05)


def test_find_x_adaptive(RE, fresh_manipulator):
    samplex.set(1)
    x_offset = RE(find_x_adaptive()).plan_result
    assert isclose(x_offset, 5, 0.1)
    samplex.set(3)
    x_offset = RE(find_x_adaptive()).plan_result
    assert isclose(x_offset, 5, 0.1)
    samplex.set(10)
    x_offset = RE(find_x_adaptive()).plan_result
    assert isclose(x_offset, 5, 0.1)


def test_find_x_offset(RE, fresh_manipulator):
    samplex.set(1)
    x_offset = RE(find_x_offset()).plan_result
    assert isclose(x_offset, 5, 0.05)
    samplex.set(3)
    x_offset = RE(find_x_offset()).plan_result
    assert isclose(x_offset, 5, 0.05)
    samplex.set(10)
    x_offset = RE(find_x_offset()).plan_result
    assert isclose(x_offset, 5, 0.05)
    sampler.set(45)
    x_offset = RE(find_x_offset()).plan_result
    # Find diagonal with tolerance of 0.05
    assert isclose(x_offset, np.sqrt(50), 0.05)


def test_find_r_offset(RE, fresh_manipulator):
    samplex.set(3)
    sampler.set(1)
    RE(find_x_offset())
    theta = RE(find_r_offset()).plan_result
    assert isclose(theta, 0, 0.1)
    sampler.set(10)
    theta = RE(find_r_offset()).plan_result
    assert isclose(theta, 0, 0.1)


@pytest.mark.parametrize('n', range(5))
def test_random_offset(RE, random_angle_manipulator, n):
    _, angle = random_angle_manipulator
    samplex.set(3)
    RE(find_x_offset())
    angle2 = RE(find_r_offset()).plan_result
    assert isclose(angle, -1*angle2, 0.1)


@pytest.mark.parametrize('angle', [1, 2, 4, 6, 8])
def test_find_corner_x_r(RE, fresh_manipulator, angle):
    sampler.set(angle)
    x, theta = RE(find_corner_x_r()).plan_result
    assert isclose(x, 5, 0.1)
    assert isclose(theta, 0, 0.1)
    # print(f"theta: {theta}")


def test_corner_coordinates(RE, fresh_manipulator):
    samplex.set(3)
    sampler.set(4)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, 0, 0.1)
    assert isclose(r2, 90, 0.1)
    assert isclose(x1, 5, 0.1)
    assert isclose(y1, 5, 0.1)

    sampler.set(87)
    samplex.set(3)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, 90, 0.1)
    assert isclose(r2, 180, 0.1)
    assert isclose(x1, 5, 0.1)
    assert isclose(y1, 5, 0.1)


def test_random_corner_coordinates(RE, random_angle_manipulator):
    manipulator, angle = random_angle_manipulator
    w = manipulator.bar.width/2.0
    samplex.set(3)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, -1*angle, 0.1)
    assert isclose(r2, 90 - angle, 0.1)
    assert isclose(x1, w, 0.1)
    assert isclose(y1, w, 0.1)

    sampler.set(90)
    samplex.set(3)
    x1, y1, r1, r2 = RE(find_corner_coordinates()).plan_result

    assert isclose(r1, 90 - angle, 0.1)
    assert isclose(r2, 180 - angle, 0.1)
    assert isclose(x1, w, 0.1)
    assert isclose(y1, w, 0.1)


@pytest.mark.parametrize("precision", [1, 0.5, 0.1, 0.01])
def test_halfmax_adaptive(RE, fresh_manipulator, precision):
    samplez.set(4)
    z = RE(halfmax_adaptive([i1], samplez, -5, precision)).plan_result
    assert isclose(z, 0, precision)


def test_threshold_adaptive(RE, fresh_manipulator):
    samplez.set(2)
    z = RE(threshold_adaptive([i1], samplez, thresholds['i1'],
                              step=-2)).plan_result
    assert z == 2
    samplez.set(-4)
    z2 = RE(threshold_adaptive([i1], samplez, thresholds['i1'],
                               step=2)).plan_result
    assert z2 >= 0
    samplez.set(-4)
    with pytest.raises(ValueError):
        RE(threshold_adaptive([i1], samplez, thresholds['i1'], step=-2))


def test_find_z_adaptive(RE, fresh_manipulator):
    samplez.set(2)
    z = RE(find_z_adaptive()).plan_result
    assert isclose(z, 0, 0.1)

    samplez.set(10)
    z = RE(find_z_adaptive()).plan_result
    assert isclose(z, 0, 0.1)

    samplez.set(-10)
    z = RE(find_z_adaptive()).plan_result
    assert isclose(z, 0, 0.1)

# Better random tests
# Test actual alignment
# Test/estimate time taken?
