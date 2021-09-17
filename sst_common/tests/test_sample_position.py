import pytest

import sst_common
import numpy as np
sst_common.STATION_NAME = "sst_sim"
from sst_common.motors import (samplex, sampley, samplez, sampler,
                               sample_holder, manipulator)
from sst_common.plans.samples import move_to_sample_edge, move_to_sample_center


@pytest.fixture()
def loaded_manipulator(fresh_manipulator):
    samples = [(1, 'sample1', (1, 1, 9, 7), 1),
               (2, 'sample2', (1, 9, 2, 10), 1),
               (3, 'sample3', (1, 17, 9, 23), 1),
               (4, 'sample4', (1, 1, 9, 7), 2),
               (5, 'sample5', (1, 9, 9, 15), 2),
               (6, 'sample6', (1, 1, 9, 7), 3)]
    for s in samples:
        sample_holder.add_sample(*s)
    return manipulator


def test_sample_edge_position(RE, loaded_manipulator):
    RE(move_to_sample_edge(1))
    assert np.isclose(manipulator.sample_distance_to_beam(), 0)
    RE(move_to_sample_edge(1, x=-1, y=-1))
    assert manipulator.sample_distance_to_beam() > 0
    RE(move_to_sample_edge(1, x=1, y=-1))
    assert manipulator.sample_distance_to_beam() > 0
    RE(move_to_sample_edge(1, 1, 1))
    assert manipulator.sample_distance_to_beam() < 0


@pytest.mark.parametrize("sampleid", [1, 2, 3, 4, 5, 6])
def test_sample_center_position(RE, loaded_manipulator, sampleid):
    RE(move_to_sample_center(sampleid))
    assert manipulator.sample_distance_to_beam() < 0
