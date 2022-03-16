from bluesky.run_engine import RunEngine, TransitionError
import numpy as np
import os
import pytest
from sst_funcs.geometry.linalg import vec, deg_to_rad, rotz
from sst_base.sampleholder import make_regular_polygon
import ucal_common
ucal_common.STATION_NAME = "sst_sim"
from ucal_common.motors import (manipx, manipy, manipz, manipr,
                                manipulator)
from ucal_common.detectors import i1, sc, thresholds
from ucal_common.plans.find_edges import (scan_z_medium, find_x_offset,
                                         find_r_offset,
                                         scan_r_medium, scan_r_fine,
                                         scan_r_coarse, find_z_adaptive,
                                         find_x_adaptive)
from ucal_common.plans.samples import set_sample_edge, set_sample, sample_move
from ucal_common.sampleholder import sampleholder
from ucal_common.run_engine import setup_run_engine

h = 100
w = 10
# points = [vec(w/2, w/2, 0), vec(w/2, w/2, 1), vec(w/2, -w/2, 0)]
geometry = make_regular_polygon(w, h, 4)
sampleholder.add_geometry(geometry)


RE = RunEngine({}, call_returns_result=True)
RE = setup_run_engine(RE)
RE(set_sample_edge("side1"))

x, y, _, _ = manipulator.origin
z = manipulator.forward(0, 0, 0, 0).z
manipx.set(x)
manipy.set(y)
# Sink manipz so that we are blocking beam
manipz.set(z + 1)
manipr.set(0)
