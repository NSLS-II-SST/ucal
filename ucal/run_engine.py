from nbs_bl.run_engine import create_run_engine, generic_cmd
from nbs_bl.globalVars import GLOBAL_SETTINGS as settings
from ucal.suspenders import suspend_current, suspend_shutter1
import redis
from redis_json_dict import RedisJSONDict

# from bluesky.utils import PersistentDict
from . import STATION_NAME

"""
if STATION_NAME == "sst_sim":
    beamline_metadata_dir = "/tmp/ucal_beamline_metadata"
elif STATION_NAME == "ucal":
    beamline_metadata_dir = "/nsls2/data/sst/shared/config/ucal/beamline_metadata"
"""


def load_RE_commands(engine):
    engine.register_command("calibrate", generic_cmd)
    engine.register_command("set_frame_sample_center", generic_cmd)
    engine.register_command("set_frame_sample_edge", generic_cmd)


def turn_on_checks(engine):
    engine.install_suspender(suspend_current)
    engine.install_suspender(suspend_shutter1)


def turn_off_checks(engine):
    engine.remove_suspender(suspend_current)
    engine.remove_suspender(suspend_shutter1)


def setup_run_engine(engine):
    """
    Function that yields a fully set-up and ready-to-go run engine
    """
    load_RE_commands(engine)
    # turn_on_checks(engine)
    return engine


RE = create_run_engine(setup=True)
RE = setup_run_engine(RE)

if redis in settings:
    uri = settings.get("redis").get("host", "localhost")  # "info.sst.nsls2.bnl.gov"
    prefix = settings.get("redis").get("prefix", "")
    RE.md = RedisJSONDict(redis.Redis(uri), prefix=prefix)
