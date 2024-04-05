from ucal.run_engine import RE
from sst_funcs.printing import boxed_text
from sst_funcs.help import add_to_func_list
from bluesky.utils import PersistentDict
import uuid
from datetime import datetime
from os.path import join, exists
from os import mkdir, chdir
from sst_funcs.status import StatusDict
from sst_funcs.queueserver import add_status
from . import STATION_NAME

if STATION_NAME == "sst_sim":
    beamline_config_dir = "/tmp/ucal_beamline_config"
    beamline_dir = "/tmp/{}_beamtime"
    proposal_dir = "/tmp/proposals/{year}-{cycle}/pass-{proposal}"
elif STATION_NAME == "ucal":
    beamline_config_dir = "/nsls2/data/sst/shared/config/ucal/beamline_config"
    beamline_dir = "/home/xf07id1/Documents/{}_beamtime"
    proposal_dir = "/nsls2/data/sst/proposals/{year}-{cycle}/pass-{proposal}"

beamline_config = PersistentDict(beamline_config_dir)

GLOBAL_USER_MD = StatusDict()
add_status("USER_MD", GLOBAL_USER_MD)

def load_saved_configuration():
    proposal = RE.md.get('proposal', "")
    cycle = RE.md.get('cycle', "")
    users = RE.md.get('users', [])
    saf = RE.md.get('saf', "")
    beamtime_start = RE.md.get('beamtime_start', '')
    beamtime_uid = RE.md.get('beamtime_uid', '')
    GLOBAL_USER_MD['users'] = users
    GLOBAL_USER_MD['proposal'] = proposal
    GLOBAL_USER_MD['saf'] = saf
    GLOBAL_USER_MD['cycle'] = cycle
    GLOBAL_USER_MD['beamtime_start'] = beamtime_start
    GLOBAL_USER_MD['beamtime_uid'] = beamtime_uid
    

def configure_user(users, proposal, cycle, saf):
    RE.md['users'] = users
    RE.md['proposal'] = proposal
    RE.md['saf'] = saf
    RE.md['cycle'] = cycle
    RE.md['scan_id'] = 0
    RE.md['beamtime_start'] = datetime.today().isoformat()
    RE.md['beamtime_uid'] = str(uuid.uuid4())
    GLOBAL_USER_MD['users'] = users
    GLOBAL_USER_MD['proposal'] = proposal
    GLOBAL_USER_MD['saf'] = saf
    GLOBAL_USER_MD['cycle'] = cycle
    GLOBAL_USER_MD['beamtime_start'] = datetime.today().isoformat()
    GLOBAL_USER_MD['beamtime_uid'] = str(uuid.uuid4())


def configure_beamline(proposal, year, cycle):
    beamline_config['proposal'] = proposal
    beamline_config['year'] = year
    beamline_config['cycle'] = cycle
    beamline_config['directory'] = get_proposal_directory(proposal, year, cycle)
    GLOBAL_USER_MD['directory'] = beamline_config['directory']
    beamline_config['loadfile'] = None
    bdir = join(beamline_dir.format(datetime.today().strftime("%Y%m%d")))
    if not exists(bdir):
        mkdir(bdir)
    beamline_config['beamtime_directory'] = bdir
    chdir(bdir)

@add_to_func_list
def get_proposal_directory(proposal, year, cycle):
    # return f"/nsls2/data/sst/proposals/{year}-{cycle}/pass-{proposal}"
    return proposal_dir.format(proposal=proposal, year=year, cycle=cycle)


@add_to_func_list
def new_proposal(users, proposal, year, cycle, saf):
    """Start a new proposal with new metadata and a reset scan counter"""
    configure_user(users, proposal, cycle, saf)
    configure_beamline(proposal, year, cycle)


@add_to_func_list
def print_config_info():
    """Print basic info about the current beamline setup"""
    title = "Currently configured information"
    infolist = []
    infolist.append("User(s): " + ", ".join(RE.md.get('users', [])))
    infolist.append(f"Proposal ID: {RE.md.get('proposal', 'None')}")
    infolist.append(f"SAF: {RE.md.get('saf', 'None')}")
    infolist.append(f"Configuration directory: " + beamline_config_dir)
    infolist.append(f"Data directory: {beamline_config.get('directory', None)}")
    infolist.append(f"Beamtime directory: {beamline_config.get('beamtime_directory', None)}")
    infolist.append(f"Load file: {beamline_config.get('loadfile', None)}")
    boxed_text(title, infolist, "white")
