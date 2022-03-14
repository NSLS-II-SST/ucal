from ucal_common.detectors import tes, det_devices
from ucal_common.shutters import psh10
from ucal_hw.energy import en
from ucal_common.plans.plan_stubs import call_obj, set_exposure
from ucal_common.scan_exfiltrator import ScanExfiltrator
from ucal_common.sampleholder import sampleholder
from ucal_common.motors import manipulator
from ucal_common.plans.samples import sample_move
from ucal_common.configuration import beamline_config
from bluesky.plan_stubs import mv
from bluesky.preprocessors import run_decorator
import bluesky.plans as bp


def wrap_metadata(param):
    def decorator(func):
        def inner(*args, md=None, **kwargs):
            md = md or {}
            _md = {}
            _md.update(param)
            _md.update(md)
            return func(*args, md=_md, **kwargs)
        return inner
    return decorator


def wrap_xas(element):
    return wrap_metadata({"edge": element, "scantype": "xas"})


def _tes_plan_wrapper(plan_function):

    def _inner(motor, *args, extra_dets=[], exposure_time_s=None, md=None, **kwargs):
        scanex = ScanExfiltrator(motor, en.energy.position)
        tes.scanexfiltrator = scanex
        dets = [tes] + det_devices + extra_dets
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


tes_scan = _tes_plan_wrapper(bp.scan)
tes_rel_scan = _tes_plan_wrapper(bp.rel_scan)
tes_list_scan = _tes_plan_wrapper(bp.list_scan)


def tes_take_noise():
    @run_decorator(md={"scantype": "noise"})
    def inner_noise():
        beamline_config['last_cal'] = None
        yield from psh10.close()
        yield from call_obj(tes, "take_noise")
        yield from psh10.open()

    return (yield from inner_noise())


def tes_count(*args, extra_dets=[], exposure_time_s=None, md=None, **kwargs):
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
    dets = [tes] + det_devices + extra_dets
    if exposure_time_s is not None:
        yield from set_exposure(dets, exposure_time_s)

    md = md or {}
    _md = {"sample_args": sampleholder.sample.read()}
    if 'last_cal' in beamline_config:
        _md['last_cal'] = beamline_config['last_cal']
    _md.update(md)

    return (yield from bp.count(dets, *args, md=_md, **kwargs))


tes_count.__doc__ += bp.count.__doc__


def _make_gscan_points(*args):
    if len(args) < 3:
        raise TypeError(f"gscan requires at least estart, estop, and delta, recieved {args}")
    if len(args) % 2 == 0:
        raise TypeError("gscan received an even number of arguments. Either a step or a step-size is missing")
    start = float(args[0])
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
    basic beamline detectors. Other detectors may be added on the fly via
    extra_dets

    args : start, stop1, step1, stop2, step2, ...
    """
    points = _make_gscan_points(*args)
    # Move motor to start position first
    yield from mv(motor, points[0])
    return (yield from tes_list_scan(motor, points, extra_dets=extra_dets, **kwargs))


def tes_calibrate(time, sampleid, exposure_time_s=10):
    yield from sample_move(0, 0, 45, sampleid)
    return (yield from tes_calibrate_inplace(time, exposure_time_s))


def tes_calibrate_inplace(time, exposure_time_s=10):
    yield from mv(tes.cal_flag, True)
    yield from mv(en.energy, 980)
    yield from set_exposure(exposure_time_s)
    cal_uid = yield from tes_count(int(time//exposure_time_s), md={"scantype": "calibration"})
    yield from mv(tes.cal_flag, False)
    beamline_config['last_cal'] = cal_uid
    return cal_uid
