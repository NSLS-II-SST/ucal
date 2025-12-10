from ucal.hw import tes, adr
from nbs_bl.detectors import deactivate_detector, activate_detector
from nbs_bl.plans.plan_stubs import call_obj, wait_for_signal_equals, set_exposure
from nbs_bl.plans.scans import nbs_count
from nbs_bl.shutters import (
    close_shutter,
    open_shutter,
    is_shutter_open,
)
from nbs_bl.utils import merge_func
from nbs_bl.help import add_to_plan_list, add_to_scan_list
from nbs_bl.samples import move_sample
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from .scan_base import take_dark_counts
from .plan_stubs import set_edge
from bluesky.plan_stubs import sleep, rd, mv, abs_set
import bluesky.plans as bp


@add_to_plan_list
def tes_start_file():
    tes = bl["tes"]
    yield from call_obj(tes, "_file_start")


@add_to_plan_list
def tes_end_file():
    tes = bl["tes"]
    tes_state = yield from rd(tes.state)
    if tes_state != "no_file":
        yield from call_obj(tes, "_file_end")


@add_to_plan_list
def tes_shutoff(should_close_shutter=True):
    if should_close_shutter:
        yield from close_shutter()
    yield from tes_end_file()
    deactivate_detector("tes")


@add_to_plan_list
def tes_cycle_cryostat(wait=False, should_close_shutter=False):
    tes = bl["tes"]
    adr = bl["adr"]
    yield from call_obj(adr, "start_cycle")
    yield from abs_set(tes.noise_uid, "")
    yield from abs_set(tes.projector_uid, "")
    yield from abs_set(tes.calibration_uid, "")
    yield from tes_shutoff(should_close_shutter)
    # Needs a minute to switch from control to going to mag up
    if wait:
        yield from sleep(60)
        yield from tes_wait_for_cycle()
        yield from sleep(60*5) # Wait for autosetup to be done -- autotune takes a few minutes


@add_to_plan_list
def tes_wait_for_cycle(timeout=None, sleep_time=10):
    adr = bl["adr"]
    yield from wait_for_signal_equals(adr.state, "control", timeout, sleep_time)


@add_to_plan_list
def tes_cycle_and_setup(
    sample=None,
    should_close_shutter=False,
    setup=True,
    calibrate=False,
    calibration_time=1600,
    fridge_threshold=None,
    **cal_args,
):
    adr = bl["adr"]
    if fridge_threshold is not None:
        heater_out = yield from rd(adr.heater)
        if heater_out > fridge_threshold:
            print(f"Fridge Magnet still at {heater_out}%, will not cycle yet")
            return

    yield from tes_cycle_cryostat(wait=True, should_close_shutter=should_close_shutter)
    if setup:
        if sample is not None:
            yield from move_sample(sample)
        yield from tes_setup()
        if calibrate:
            yield from tes_calibrate(calibration_time, sample=sample, **cal_args)


def tes_take_noise():
    """Close the shutter and take TES noise. Run after cryostat cycle"""
    tes = bl["tes"]
    yield from abs_set(tes.noise_uid, "")
    yield from abs_set(tes.projector_uid, "")
    shutter_open = yield from is_shutter_open()
    if shutter_open:
        yield from close_shutter()
    yield from call_obj(tes, "take_noise")
    uid = yield from bp.count([tes], 5, md={"scantype": "noise"})
    yield from call_obj(tes, "_file_end")
    yield from call_obj(tes, "_set_pulse_triggers")
    yield from abs_set(tes.noise_uid, uid)
    if shutter_open:
        yield from open_shutter()
    return uid


def tes_take_projectors():
    """Take projector data for TES. Run with pulses from cal sample"""
    tes = bl["tes"]
    yield from open_shutter()
    yield from call_obj(tes, "take_projectors")
    uid = yield from bp.count([tes], 30, md={"scantype": "projectors"})
    yield from call_obj(tes, "_file_end")
    yield from abs_set(tes.projector_uid, uid)

    return uid


def tes_make_and_load_projectors():
    tes = bl["tes"]
    yield from call_obj(tes, "make_projectors")
    return (yield from call_obj(tes, "set_projectors"))


@add_to_plan_list
def tes_setup(
    should_take_dark_counts=True,
):
    """Set up TES after cryostat cycle. Must have counts from cal sample.

    should_take_dark_counts: if True, take dark counts for the other
    detectors at the same time.
    """
    if should_take_dark_counts:
        yield from close_shutter()
        deactivate_detector("tes")
        yield from take_dark_counts()
    activate_detector("tes")
    yield from tes_take_noise()
    yield from tes_take_projectors()
    yield from tes_make_and_load_projectors()


@add_to_scan_list
@merge_func(nbs_count, ["num", "delay"], use_func_name=False)
def tes_calibrate(time, dwell=10, energy=980, md=None, autosetup=True, **kwargs):
    """
    Perform an in-place energy calibration for the TES detector.

    Parameters
    ----------
    time : float
        The total length of time to perform the calibration for.
    dwell : float, optional
        The time per point during calibration, by default 10.
    energy : float, optional
        The beamline monochromator position to set for the calibration, by default 980.
    md : dict, optional
        Extra metadata to pass to the RunEngine, by default None.
    **kwargs : dict
        Additional keyword arguments to pass to the underlying `tes_count` function.

    Returns
    -------
    cal_uid : str
        The unique identifier for the calibration run.
    """
    tes = bl["tes"]
    yield from set_edge("blank")
    yield from mv(bl.energy, energy)
    if autosetup:
        tes_status = yield from rd(tes.status)
        if tes_status < 4:
            yield from tes_setup()
    yield from mv(tes.cal_flag, True)
    pre_cal_exposure = yield from rd(tes.acquire_time)
    md = md or {}
    _md = {"scantype": "calibration", "calibration_energy": energy}
    _md.update(md)
    yield from mv(tes.mca.make_cal, time * 600)
    cal_uid = yield from nbs_count(int(time // dwell), dwell=dwell, md=_md, **kwargs)
    yield from mv(tes.cal_flag, False)
    yield from abs_set(tes.calibration_uid, cal_uid)
    yield from set_exposure(pre_cal_exposure)
    return cal_uid
