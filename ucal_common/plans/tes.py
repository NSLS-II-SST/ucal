from ucal_common.detectors import tes, basic_dets
from ucal_common.shutters import psh10
from ucal_hw.energy import en
from ucal_common.plans.plan_stubs import call_obj, set_exposure
from ucal_common.scan_exfiltrator import ScanExfiltrator
from ucal_common.sampleholder import sampleholder
from bluesky.plan_stubs import sleep
import bluesky.plans as bp

def tes_take_noise():
    yield from psh10.close()
    yield from call_obj(tes, "take_noise")
    yield from psh10.open()

def _tes_plan_wrapper(plan_function):

    def _inner(motor, *args, extra_dets=[], exposure_time_s=None, md=None, **kwargs):
        scanex = ScanExfiltrator(motor, en.energy.position)
        tes.scanexfiltrator = scanex
        dets = [tes] + basic_dets + extra_dets
        if exposure_time_s is not None:
            yield from set_exposure(dets, exposure_time_s)

        md = md or {}
        _md = {"sample_args": sampleholder.sample.read()}
        _md.update(md)
        yield from plan_function(dets, motor, *args, md=_md, **kwargs)

    d = f"""Modifies {plan_function.__name__} to automatically fill
dets with the TES detector and basic beamline detectors.
Other detectors may be added on the fly via extra_dets
---------------------------------------------------------
"""
    
    _inner.__doc__ = d + plan_function.__doc__
    
    return _inner

for plan_function in [bp.scan, bp.rel_scan, bp.list_scan]:
    globals()[f"tes_{plan_function.__name__}"] = _tes_plan_wrapper(plan_function)


def _make_gscan_points(*args):
    start = args[0]
    points = [start]
    for stop, step in zip(args[1::2], args[2::2]):
        nextpoint = points[-1] + step
        while nextpoint < stop - step/2.0:
            points.append(nextpoint)
            nextpoint += step
        points.append(stop)
    return points

def tes_gscan(motor, *args, extra_dets=[], **kwargs):
    """
    A variable step scan of a motor, the TES detector, and the
    basic beamline detectors. Other detectors may be added on the fly via extra_dets
    
    args : start, stop1, step1, stop2, step2, ...
    """
    points = _make_gscan_points(*args)
    yield from tes_list_scan(motor, points, extra_dets=extra_dets, **kwargs)

def tes_count(*args, extra_dets=[], **kwargs):
    """
    Modifies count to automatically fill
    dets with the TES detector and basic beamline detectors.
    Other detectors may be added on the fly via extra_dets
    ---------------------------------------------------------
    """
    class dummymotor():
        name = "time"
        egu = "index"

    motor = dummymotor()
    scanex = ScanExfiltrator(motor, en.energy.position)
    tes.scanexfiltrator = scanex
    yield from bp.count([tes] + basic_dets + extra_dets, *args, **kwargs)

tes_count.__doc__ += bp.count.__doc__

def tes_fe_xas(**kwargs):
    yield from tes_gscan(en.energy, 690, 700, 1, 704, 0.5, 707, 0.2, 715, 0.1, 719, 0.5, 725, 0.1, 730, 0.5, 760, 1, **kwargs)

def tes_fe_xas_short(**kwargs):
    yield from tes_gscan(en.energy, 700, 705, 1, 720, 0.5, 740, 1, **kwargs)

def tes_c_xas(**kwargs):
    yield from tes_gscan(en.energy, 270, 280, 1, 300, 0.1, 310, 0.2, 350, 1, **kwargs)
    
def tes_calibrate(time):
    yield from mv(tes.cal_flag, True)
    yield from mv(energy, 980)
    yield from sample_move(0, 0, 45, 5)
    yield from set_exposure([tes], 10)
    yield from tes_count(int(time//10))
    yield from mv(tes.cal_flag, False)
