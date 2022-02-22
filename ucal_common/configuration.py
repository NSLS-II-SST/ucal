from ucal_common.run_engine import RE
from bluesky.utils import PersistentDict

from . import STATION_NAME


if STATION_NAME == "sst_sim":
    beamline_config_dir = "/tmp/ucal_beamline_config"
elif STATION_NAME == "ucal":
    beamline_config_dir = "/nsls2/data/sst1/shared/config/ucal/beamline_config"

beamline_config = PersistentDict(beamline_config_dir)


def configure_user(users, proposal, cycle, saf):
    RE.md['users'] = users
    RE.md['proposal'] = proposal
    RE.md['saf'] = saf
    RE.md['cycle'] = cycle


def configure_beamline(proposal, year, cycle):
    beamline_config['proposal'] = proposal
    beamline_config['year'] = year
    beamline_config['cycle'] = cycle
    beamline_config['directory'] = get_proposal_directory(proposal, year, cycle)
    beamline_config['loadfile'] = ""


def get_proposal_directory(proposal, year, cycle):
    return f"/nsls2/data/sst1/proposals/{year}-{cycle}/pass-{proposal}"


def new_proposal(users, proposal, year, cycle, saf):
    configure_user(users, proposal, cycle, saf)
    configure_beamline(proposal, year, cycle)


def print_config_info():
    print("Currently configured information:")
    print("User(s): ", RE.md.get('users', "None"))
    print("Proposal ID: ", RE.md.get('proposal', "None"))
    print("SAF: ", RE.md.get('saf', "None"))
    print("Configuration directory: ", beamline_config_dir)
    print("Data directory: ", beamline_config.get('directory', "None"))
    print("Load file: ", beamline_config.get('loadfile', "None"))
