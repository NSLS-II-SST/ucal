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
from ucal.detectors import (ucal_i400, dm7_i400, tes,
                            add_detector, list_detectors,
                            activate_detector, deactivate_detector,
                            remove_detector)
from ucal.motors import (manipx, manipy, manipz, manipr, tesz,
                         manipulator, eslit, i0upAu, add_motor, list_motors,
                         remove_motor)
from ucal.energy import en
from ucal.sampleholder import sampleholder
from ucal.plans.find_edges import find_z_offset, find_x_offset, find_x, find_z
from ucal.plans.alignment import calibrate_beam_offset, calibrate_sides
from ucal.multimesh import set_edge
from ucal.plans.plan_stubs import set_exposure, open_shutter, close_shutter
from ucal.plans.samples import (set_side, set_sample,
                                set_sample_center, set_sample_edge,
                                sample_move, load_standard_two_sided_bar,
                                load_standard_four_sided_bar,
                                load_sample_dict, list_samples)
from ucal.plans.scans import *
from ucal.plans.scan_base import (tes_calibrate, tes_take_noise, tes_gscan,
                                  tes_count, tes_scan, tes_rel_scan,
                                  tes_take_projectors)
from ucal.run_engine import RE
from ucal.configuration import print_config_info, beamline_config, new_proposal
from sst_funcs.configuration import print_builtins

# Motor aliases
energy = en.energy

RE(set_exposure(1.0))

sd = SupplementalData(baseline=[manipulator, eslit, i0upAu, tesz])
RE.preprocessors.append(sd)
