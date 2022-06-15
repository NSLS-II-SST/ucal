from ucal.detectors import (tes, GLOBAL_ACTIVE_DETECTORS,
                            activate_detector, deactivate_detector)
from ucal.shutters import psh10
from ucal.energy import en
from ucal.plans.plan_stubs import call_obj, set_exposure, close_shutter, open_shutter
from ucal.scan_exfiltrator import ScanExfiltrator
from ucal.sampleholder import sampleholder
from ucal.motors import manipulator
from ucal.plans.samples import sample_move
from ucal.multimesh import set_edge, refholder
from ucal.configuration import beamline_config
from sst_funcs.configuration import add_to_plan_list, add_to_scan_list
from bluesky.plan_stubs import mv
from bluesky.preprocessors import run_decorator
from sst_funcs.plans.batches import setup_batch
import bluesky.plans as bp
import time
from functools import wraps


def wrap_metadata(param):
    def decorator(func):
        @wraps(func)
        def inner(*args, md=None, **kwargs):
            md = md or {}
            _md = {}
            _md.update(param)
            _md.update(md)
            return func(*args, md=_md, **kwargs)
        return inner
    return decorator


def wrap_xas_setup(element):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            yield from set_edge(element)
            return (yield from func(*args, **kwargs))
        return inner
    return decorator


def wrap_xas(element):
    def decorator(func):
        return add_to_scan_list(wrap_metadata({"edge": element, "scantype": "xas"})(wrap_xas_setup(element)(func)))
    return decorator


@add_to_scan_list
def tes_count(*args, extra_dets=[], exposure_time_s=None, md=None, **kwargs):
    """Count for a specified number of points

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
    for det in extra_dets:
        activate_detector(det)

    if exposure_time_s is not None:
        yield from set_exposure(exposure_time_s)

    md = md or {}
    _md = {"sample_args": sampleholder.sample.read(),
           "ref_args": refholder.sample.read()}
    if 'last_cal' in beamline_config:
        _md['last_cal'] = beamline_config['last_cal']
    if 'last_noise' in beamline_config:
        _md['last_noise'] = beamline_config['last_noise']

    _md.update(md)

    ret = (yield from bp.count(GLOBAL_ACTIVE_DETECTORS, *args, md=_md,
                               **kwargs))

    for det in extra_dets:
        deactivate_detector(det)

    return ret


tes_count.__doc__ += bp.count.__doc__


def _tes_plan_wrapper(plan_function, plan_name):

    def _inner(motor, *args, extra_dets=[], exposure_time_s=None, md=None, **kwargs):
        scanex = ScanExfiltrator(motor, en.energy.position)
        tes.scanexfiltrator = scanex

        for det in extra_dets:
            activate_detector(det)

        if exposure_time_s is not None:
            yield from set_exposure(exposure_time_s)

        md = md or {}
        """
        idea for more simple scheme...
        _md = {"sample_name": sampleholder.sample.sample_name.get(),
               "sample_id": sampleholder.sample.sample_id.get(),
               "sample_side": sampleholder.sample.side.get(),
               "sample_origin": sampleholder.sample.origin.get()}
        """
        _md = {"sample_args": sampleholder.sample.read(),
               "ref_args": refholder.sample.read()}
        if 'last_cal' in beamline_config:
            _md['last_cal'] = beamline_config['last_cal']
        if 'last_noise' in beamline_config:
            _md['last_noise'] = beamline_config['last_noise']

        _md.update(md)
        ret = (yield from plan_function(GLOBAL_ACTIVE_DETECTORS, motor,
                                        *args, md=_md, **kwargs))

        for det in extra_dets:
            deactivate_detector(det)

        return ret
    d = f"""Modifies {plan_function.__name__} to automatically fill
dets with the TES detector and basic beamline detectors.
Other detectors may be added on the fly via extra_dets
---------------------------------------------------------
"""

    _inner.__doc__ = d + plan_function.__doc__
    _inner.__name__ = plan_name
    return _inner


tes_scan = add_to_scan_list(_tes_plan_wrapper(bp.scan, "tes_scan"))
tes_rel_scan = add_to_scan_list(_tes_plan_wrapper(bp.rel_scan, "tes_rel_scan"))
tes_list_scan = add_to_scan_list(_tes_plan_wrapper(bp.list_scan, "tes_list_scan"))


@add_to_scan_list
def tes_take_noise():
    @run_decorator(md={"scantype": "noise"})
    def inner_noise():
        beamline_config['last_cal'] = None
        beamline_config['last_noise'] = None
        yield from close_shutter()
        yield from call_obj(tes, "take_noise")
        yield from open_shutter()
    uid = yield from inner_noise()
    beamline_config['last_noise'] = uid
    return uid


@add_to_plan_list
def tes_take_projectors():
    @run_decorator(md={"scantype": "projectors"})
    def inner_projectors():
        tes.rpc.file_start(tes.path, write_ljh=True, write_off=False, setFilenamePattern=True)
        yield from time.sleep(30)
        tes._file_end()
    return (yield from inner_projectors())


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


@add_to_scan_list
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


@add_to_scan_list
def tes_calibrate(time, sampleid, exposure_time_s=10, energy=980, md=None):
    yield from sample_move(0, 0, 45, sampleid)
    return (yield from tes_calibrate_inplace(time, exposure_time_s, energy=energy, md=md))


@add_to_scan_list
def tes_calibrate_inplace(time, exposure_time_s=10, energy=980, md=None):
    yield from mv(tes.cal_flag, True)
    yield from mv(en.energy, energy)
    pre_cal_exposure = tes.acquire_time.get()
    md = md or {}
    _md = {"scantype": "calibration", "calibration_energy": energy}
    _md.update(md)
    cal_uid = yield from tes_count(int(time//exposure_time_s), exposure_time_s=exposure_time_s, md=_md)
    yield from mv(tes.cal_flag, False)
    beamline_config['last_cal'] = cal_uid
    yield from set_exposure(pre_cal_exposure)
    return cal_uid


def xas_factory(energy_grid, edge):
    @wrap_xas(edge)
    def inner(repeat=1, batch=True, batch_md={}, **kwargs):
        """Parameters
        ----------
        repeat : int
            Number of times to repeat the scan
        batch : bool
            If True, and repeat > 1, group the scans in a batch run
        batch_md : dict
            Metadata that should be saved with the batch run
        **kwargs : 
            Arguments to be passed to tes_gscan

        """
        if repeat > 1 and batch:
            add_to_batch, close_batch = yield from setup_batch(batch_md)
            for i in range(repeat):
                yield from add_to_batch(tes_gscan(en.energy, *energy_grid, **kwargs))
            yield from close_batch()
        else:
            for i in range(repeat):
                yield from tes_gscan(en.energy, *energy_grid, **kwargs)
    d = f"Perform an xas scan for {edge} with energy pattern {energy_grid} \n"
    inner.__doc__ = d + inner.__doc__
    return inner
