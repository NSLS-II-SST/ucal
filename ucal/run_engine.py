from sst_funcs.re_commands import generic_cmd, call_obj
from bluesky import RunEngine
from bluesky.preprocessors import SupplementalData
from bluesky.utils import PersistentDict
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    beamline_metadata_dir = "/tmp/ucal_beamline_metadata"
elif STATION_NAME == "ucal":
    beamline_metadata_dir = "/nsls2/data/sst/shared/config/ucal/beamline_metadata"


def load_RE_commands(engine):
    engine.register_command("calibrate", generic_cmd)
    engine.register_command("set_frame_sample_center", generic_cmd)
    engine.register_command("set_frame_sample_edge", generic_cmd)
    engine.register_command("call_obj", call_obj)


def setup_run_engine(engine):
    """
    Function that yields a fully set-up and ready-to-go run engine
    """
    load_RE_commands(engine)
    return engine


RE = RunEngine(call_returns_result=True)
RE = setup_run_engine(RE)
RE.md = PersistentDict(beamline_metadata_dir)
ucal_sd = SupplementalData()
RE.preprocessors.append(ucal_sd)
