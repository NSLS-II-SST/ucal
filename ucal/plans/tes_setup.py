from ucal.hw import tes, adr
from nbs_bl.detectors import deactivate_detector, activate_detector
from nbs_bl.plans.plan_stubs import call_obj, wait_for_signal_equals
from nbs_bl.shutters import close_shutter
from nbs_bl.help import add_to_plan_list
from bluesky.plan_stubs import sleep


@add_to_plan_list
def tes_start_file():
    yield from call_obj(tes, "_file_start")


@add_to_plan_list
def tes_end_file():
    yield from call_obj(tes, "_file_end")


@add_to_plan_list
def tes_shutoff(should_close_shutter=True):
    if should_close_shutter:
        yield from close_shutter()
    yield from tes_end_file()
    deactivate_detector("tes")


@add_to_plan_list
def tes_cycle_cryostat(wait=False):
    yield from call_obj(adr, "start_cycle")
    # Needs a minute to switch from control to going to mag up
    yield from sleep(60)
    if wait:
        yield from tes_wait_for_cycle()


@add_to_plan_list
def tes_wait_for_cycle(timeout=None, sleep_time=10):
    yield from wait_for_signal_equals(adr.state, "control", timeout, sleep_time)
