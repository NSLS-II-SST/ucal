from nbs_bl.run_engine import create_run_engine, generic_cmd
from nbs_bl.beamline import GLOBAL_BEAMLINE
from ucal.suspenders import suspend_current, suspend_shutter1


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


#RE = create_run_engine(setup=True)
#RE = setup_run_engine(RE)
"""
if "redis" in GLOBAL_BEAMLINE.settings:
    import redis
    from nbs_bl.status import RedisStatusDict
    from nbs_bl.queueserver import GLOBAL_USER_STATUS

    redis_settings = GLOBAL_BEAMLINE.settings.get("redis").get("md")
    uri = redis_settings.get("host", "localhost")  # "info.sst.nsls2.bnl.gov"
    prefix = redis_settings.get("prefix", "")
    md = RedisStatusDict(redis.Redis(uri), prefix=prefix)
    GLOBAL_USER_STATUS.add_status("USER_MD", md)
    RE.md = md
"""