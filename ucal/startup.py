
from bluesky.utils import PersistentDict
from bluesky.plan_stubs import mv, mvr, abs_set
from bluesky.preprocessors import SupplementalData
# startup sequence for beamline
import ucal.motors as ucal_motors
import ucal.mirrors as ucal_mirrors
import ucal.shutters as ucal_shutters
import ucal.valves as ucal_valves

# convenience imports
from ucal.shutters import psh10, psh7
from ucal.mirrors import mir1, mir3, mir4
from ucal.detectors import (ucal_i400, dm7_i400, tes, i0, sc,
                            ref, basic_dets, det_devices)
from ucal.motors import (manipx, manipy, manipz, manipr, tesz,
                         manipulator, eslit)
from ucal_hw.energy import en
from ucal.sampleholder import sampleholder
from ucal.plans.find_edges import find_z_offset, find_x_offset, find_x, find_z
from ucal.plans.multimesh import set_edge
from ucal.plans.plan_stubs import set_exposure
from ucal.plans.samples import (load_samples, set_side, set_sample,
                                set_sample_center, set_sample_edge,
                                sample_move, load_standard_two_sided_bar,
                                load_standard_four_sided_bar,
                                load_sample_dict)
from ucal.plans.scans import *
from ucal.plans.scan_base import tes_calibrate, tes_take_noise, tes_gscan, tes_count, tes_scan
from ucal.run_engine import RE
from ucal.configuration import print_config_info, beamline_config

# Motor aliases
energy = en.energy

print_config_info()
RE(set_exposure(1.0))

sd = SupplementalData(baseline=[manipulator, eslit, tesz])
RE.preprocessors.append(sd)
