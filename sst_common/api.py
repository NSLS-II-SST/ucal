#from .shims import *
import sst_hw
#from alignment import find_z_offset, find_x_offset, find_radius_theta, find_max
#from alignment import find_corner_coordinates, find_corner_x_theta

# Common imports
from bluesky.plans import scan, count, list_scan, rel_scan
from bluesky.plan_stubs import mv, mvr, abs_set
from bluesky.callbacks import LiveTable

import numpy as np
import matplotlib.pyplot as plt

plt.ion()

from . import STATION_NAME

"""
from importlib import metadata
not using entry points for now?
eps = metadata.entry_points()["sst_common"]
endstation = None
if STATION_NAME is not None:
    for ep in eps:
        if ep.name == STATION_NAME:
            endstation = ep.load()
if endstation is None:
    raise ImportError(f"No sst_common entrypoint called {STATION_NAME} found or loaded")
"""

############################################################
#                      imports                             #
############################################################
# from .plans import *

# def _startup():
#     from .detectors import *


# from sst_base.users import new_experiment
