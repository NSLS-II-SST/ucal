from ucal.run_engine import RE
from sst_funcs.printing import boxed_text
from sst_funcs.help import add_to_func_list
from bluesky.utils import PersistentDict
import uuid
from datetime import datetime

from . import STATION_NAME

if STATION_NAME == "sst_sim":
    beamline_config_dir = "/tmp/ucal_beamline_config"
elif STATION_NAME == "ucal":
    beamline_config_dir = "/nsls2/data/sst/shared/config/ucal/beamline_config"

beamline_config = PersistentDict(beamline_config_dir)

def configure_user(users, proposal, cycle, saf):
    RE.md['users'] = users
    RE.md['proposal'] = proposal
    RE.md['saf'] = saf
    RE.md['cycle'] = cycle
    RE.md['scan_id'] = 0
    RE.md['beamtime_start'] = datetime.today().isoformat()
    RE.md['beamtime_uid'] = str(uuid.uuid4())


def configure_beamline(proposal, year, cycle):
    beamline_config['proposal'] = proposal
    beamline_config['year'] = year
    beamline_config['cycle'] = cycle
    beamline_config['directory'] = get_proposal_directory(proposal, year, cycle)
    beamline_config['loadfile'] = None


def get_proposal_directory(proposal, year, cycle):
    return f"/nsls2/data/sst/proposals/{year}-{cycle}/pass-{proposal}"


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
    infolist.append(f"Load file: {beamline_config.get('loadfile', None)}")
    boxed_text(title, infolist, "white")
