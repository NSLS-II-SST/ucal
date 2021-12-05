import pytest

import ucal_common
import numpy as np
ucal_common.STATION_NAME = "sst_sim"
from ucal_common.motors import (samplex, sampley, samplez, sampler,
                                manipulator)
from ucal_common.sampleholder import sampleholder
from ucal_common.plans.samples import sample_move, set_sample, set_sample_edge


@pytest.fixture()
def loaded_manipulator(fresh_manipulator):
    samples = [(1, 'sample1', (1, 1, 9, 7), 1),
               (2, 'sample2', (1, 9, 2, 10), 1),
               (3, 'sample3', (1, 17, 9, 23), 1),
               (4, 'sample4', (1, 1, 9, 7), 2),
               (5, 'sample5', (1, 9, 9, 15), 2),
               (6, 'sample6', (1, 1, 9, 7), 3)]
    for s in samples:
        sampleholder.add_sample(*s)
    return manipulator


def test_sample_edge_position(RE, loaded_manipulator):
    RE(set_sample_edge(1))
    RE(sample_move(0, 0, 90))
    assert np.isclose(manipulator.sample_distance_to_beam(), 0)
    RE(sample_move(-1, -1, 90))
    assert manipulator.sample_distance_to_beam() > 0
    RE(sample_move(1, -1, 90))
    assert manipulator.sample_distance_to_beam() > 0
    RE(sample_move(1, 1, 90))
    assert manipulator.sample_distance_to_beam() < 0


@pytest.mark.parametrize("sampleid", [1, 2, 3, 4, 5, 6])
def test_sample_center_position(RE, loaded_manipulator, sampleid):

    # Hitting sample dead center should be "negative" distance
    RE(sample_move(0, 0, 90, sampleid, origin='center'))
    d = manipulator.sample_distance_to_beam()
    assert d < 0

    # Hitting sample at 45 degrees should be smaller or equal
    # distance to the sample edges
    RE(sample_move(0, 0, 45))
    d2 = manipulator.sample_distance_to_beam()
    assert d2 >= d

    # None of the samples are larger than 20 mm, so this should
    # put us off the sample
    RE(sample_move(0, -20, 90))
    d3 = manipulator.sample_distance_to_beam()
    assert d3 > 0
