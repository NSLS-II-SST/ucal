from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
import bluesky.plan_stubs as bps
from nbs_bl.help import add_to_plan_list

@add_to_plan_list
def charge_capacitor_box():
    """Charge PEY Capacitor box for 2 minutes, and then wait 3 minutes for settling
    """
    yield from bps.mv(bl["capacitor_box"], 5)
    yield from bps.sleep(60 * 2)
    yield from bps.mv(bl["capacitor_box"], 0)
    yield from bps.sleep(60 * 3)
