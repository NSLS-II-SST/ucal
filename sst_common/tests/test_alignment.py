# from sst_common.api import *
import pytest
import sst_common
import numpy as np
sst_common.STATION_NAME = "sst_sim"
from sst_common.motors import (samplex, sampley, samplez, sampler,
                               sample_holder, manipulator)
from sst_common.plans.find_edges import (scan_z_medium, find_x_offset,
                                         find_r_offset,
                                         scan_r_medium, scan_r_fine,
                                         scan_r_coarse)
from sst_common.plans.alignment import find_corner_x_r


@pytest.fixture()
def fresh_manipulator():
    from sst_base.linalg import vec
    points = [vec(5, -5, 0), vec(5, -5, 1), vec(5, 5, 0)]
    sample_holder.load_geometry(10, 100, 4, points)
    samplex.set(0)
    sampley.set(0)
    # Sink samplez so that we are blocking beam
    samplez.set(-1)
    samplex.set(0)
    yield manipulator
    sample_holder._reset()


@pytest.fixture()
def random_angle_manipulator():
    from sst_base.linalg import vec, deg_to_rad
    angle = 5*np.random.rand()
    theta = deg_to_rad(angle)
    points = [vec(5, -5, 0), vec(5, -5, 1), vec(5 - 10*np.tan(theta), 5, 0)]
    sample_holder.load_geometry(10, 100, 4, points)
    samplex.set(0)
    sampley.set(0)
    # Sink samplez so that we are blocking beam
    samplez.set(-1)
    sampler.set(0)
    yield manipulator, angle
    sample_holder._reset()


# need to directly set hardware in fixtures
def test_scan_z_finds_edge(RE, fresh_manipulator):
    z_offset = RE(scan_z_medium()).plan_result
    assert np.isclose(z_offset, 0, 0.05)
    samplez.set(-1)
    z_offset2 = RE(scan_z_medium()).plan_result
    assert np.isclose(z_offset2, 0, 0.05)


def test_find_x_offset(RE, fresh_manipulator):
    samplex.set(3)
    x_offset = RE(find_x_offset()).plan_result
    assert np.isclose(x_offset, 5, 0.05)
    sampler.set(45)
    x_offset = RE(find_x_offset()).plan_result
    # Find diagonal with tolerance of 0.05
    assert np.isclose(x_offset, np.sqrt(50), 0.05)


def test_find_r_offset(RE, fresh_manipulator):
    samplex.set(3)
    sampler.set(1)
    RE(find_x_offset())
    theta = RE(find_r_offset()).plan_result
    assert np.isclose(theta, 0, 0.1)
    sampler.set(10)
    theta = RE(find_r_offset()).plan_result
    assert np.isclose(theta, 0, 0.1)


@pytest.mark.parametrize('n', range(5))
def test_random_offset(RE, random_angle_manipulator, n):
    _, angle = random_angle_manipulator
    samplex.set(3)
    RE(find_x_offset())
    angle2 = RE(find_r_offset()).plan_result
    assert np.isclose(angle, -1*angle2, 0.1)


@pytest.mark.parametrize('angle', [1, 2, 4, 6, 8])
def test_find_corner_x_r(RE, fresh_manipulator, angle):
    sampler.set(angle)
    x, theta = RE(find_corner_x_r()).plan_result
    assert np.isclose(x, 5, 0.1)
    assert np.isclose(theta, 0, 0.1)
    # print(f"theta: {theta}")

# Better random tests
# Test actual alignment
# Test/estimate time taken?

