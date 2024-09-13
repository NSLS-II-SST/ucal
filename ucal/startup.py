from bluesky.plan_stubs import mv, mvr, abs_set
from bluesky.plan_stubs import mv as move

# startup sequence for beamline
# import ucal.motors as ucal_motors
# import ucal.mirrors as ucal_mirrors
# import ucal.shutters as ucal_shutters
# import ucal.valves as ucal_valves

# convenience imports
# from ucal.shutters import psh10, psh7
# from ucal.mirrors import mir3, mir4
# from ucal import mir1
# from ucal.detectors import (sc, i0, ref, tes)
# from ucal.controllers import adr
# from ucal.energy import en
# from ucal.motors import (manipx, manipy, manipz, manipr, tesz,
#                         manipulator, eslit, i0upAu)

import nbs_bl
from ucal.hw import *
from nbs_bl.detectors import (
    list_detectors,
    activate_detector,
    deactivate_detector,
    activate_detector_set,
)
from nbs_bl.motors import list_motors
import ucal.plans

from ucal.plans.find_edges import find_z_offset, find_x_offset, find_x, find_z
from ucal.plans.alignment import (
    calibrate_beam_offset,
    calibrate_sides,
    new_calibrate_sides,
)
from ucal.plans.samples import (
    set_side,
    set_sample,
    set_sample_center,
    set_sample_edge,
    sample_move,
    load_standard_two_sided_bar,
    load_standard_four_sided_bar,
    load_sample_dict,
)
from ucal.plans.scan_base import (
    tes_calibrate,
    tes_take_noise,
    tes_gscan,
    tes_rel_scan,
    tes_take_projectors,
    tes_make_and_load_projectors,
)
import ucal.plans.scans
from ucal.plans.plan_stubs import *
import nbs_bl.plans.scans
from ucal.plans.tes_setup import *
from ucal.plans.configuration import setup_ucal
from ucal.plans.energy import tune_grating, change_grating
from ucal.run_engine import RE
from ucal.configuration import beamline_config, new_proposal, load_saved_configuration
from nbs_bl.help import GLOBAL_IMPORT_DICTIONARY
from nbs_bl.plans.groups import group
from nbs_bl.queueserver import request_update, get_status
from nbs_bl.samples import list_samples

for key in GLOBAL_IMPORT_DICTIONARY:
    if key not in globals():
        globals()[key] = GLOBAL_IMPORT_DICTIONARY[key]


def main():
    print("UCAL Startup")
    RE(set_exposure(1.0))
    tes.setFilenamePattern = False
    tes.path = "/data/raw"
    load_saved_configuration()
    activate_detector_set("default")


# ucal_sd.baseline = [manipulator, eslit, i0upAu, tesz, mir3, mir4, mir5, multimesh]
