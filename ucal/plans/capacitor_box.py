from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from bluesky.plans import mv
import bluesky.plan_stubs as bps


def charge_capacitor_box():
    yield from mv(bl["capacitor_box"], 5)
    yield from bps.sleep(60 * 5)
    yield from mv(bl["capacitor_box"], 0)
    yield from bps.sleep(60 * 2)
