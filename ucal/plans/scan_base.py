from ucal.detectors import (tes, GLOBAL_ACTIVE_DETECTORS,
                            GLOBAL_PLOT_DETECTORS,
                            activate_detector, deactivate_detector)
from ucal.shutters import psh10
from ucal.energy import en
from ucal.plans.plan_stubs import call_obj, set_exposure, close_shutter, open_shutter, is_shutter_open
from ucal.scan_exfiltrator import ScanExfiltrator
from ucal.sampleholder import sampleholder
from ucal.motors import manipulator
from ucal.plans.samples import sample_move
from ucal.multimesh import set_edge, refholder
from ucal.configuration import beamline_config
from sst_funcs.help import add_to_plan_list, add_to_scan_list
from bluesky.plan_stubs import mv, sleep
from bluesky.preprocessors import run_decorator, inject_md_wrapper, subs_decorator
from bluesky_live.bluesky_run import BlueskyRun, DocumentCache
from sst_funcs.plans.preprocessors import wrap_metadata
from sst_funcs.plans.groups import repeat
import bluesky.plans as bp
from functools import wraps


def wrap_xas_setup(element):
    def decorator(func):
        @wraps(func)
        def inner(*args, auto_setup_xas=True, **kwargs):
            if auto_setup_xas:
                yield from set_edge(element)
            return (yield from func(*args, **kwargs))
        return inner
    return decorator


def wrap_xas(element):
    def decorator(func):
        return add_to_scan_list(wrap_metadata({"edge": element, "scantype": "xas"})(wrap_xas_setup(element)(func)))
    return decorator


def get_detector_plot_hints():
    plot_y_md = []
    plot_mca_md = []
    style_hints = {}
    for detector in GLOBAL_PLOT_DETECTORS:
        if hasattr(detector, "plot_hints"):
            h = detector.plot_hints()
            plot_y_md += h.get('y', [])
            plot_mca_md += h.get('mca', [])
            style_hints.update(h.get('style_hints', {}))
        else:
            plot_y_md += detector.hints.get('fields', [])
    return plot_y_md, plot_mca_md, style_hints


@add_to_scan_list
def tes_count(*args, extra_dets=[], exposure_time_s=None, md=None, plot_hints=None, **kwargs):
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
        activate_detector(det, plot=True)

    yield from set_exposure(exposure_time_s)

    md = md or {}
    plot_hints = plot_hints or {}
    _md = {"sample_args": sampleholder.sample.read(),
           "ref_args": refholder.sample.read(),
           "sample_md": sampleholder.current_sample_md()}
    if 'last_cal' in beamline_config:
        _md['last_cal'] = beamline_config['last_cal']
    if 'last_noise' in beamline_config:
        _md['last_noise'] = beamline_config['last_noise']
    yhints, mcahints, stylehints = get_detector_plot_hints()
    _plot_hints = {'x': ['time'], 'y': yhints, 'mca': mcahints, 'style': stylehints}
    _plot_hints.update(plot_hints)
    _md['plot_hints'] = _plot_hints

    _md.update(md)

    ret = (yield from bp.count(GLOBAL_ACTIVE_DETECTORS, *args, md=_md,
                               **kwargs))

    for det in extra_dets:
        deactivate_detector(det)

    return ret


tes_count.__doc__ += bp.count.__doc__


def _tes_plan_wrapper(plan_function, plan_name):

    def _inner(motor, *args, extra_dets=[], exposure_time_s=None, md=None, plot_hints=None, **kwargs):
        scanex = ScanExfiltrator(motor, en.energy.position)
        tes.scanexfiltrator = scanex

        for det in extra_dets:
            activate_detector(det, plot=True)

        yield from set_exposure(exposure_time_s)

        md = md or {}
        plot_hints = plot_hints or {}
        """
        idea for more simple scheme...
        _md = {"sample_name": sampleholder.sample.sample_name.get(),
               "sample_id": sampleholder.sample.sample_id.get(),
               "sample_side": sampleholder.sample.side.get(),
               "sample_origin": sampleholder.sample.origin.get()}
        """
        _md = {"sample_args": sampleholder.sample.read(),
               "ref_args": refholder.sample.read(),
               "sample_md": sampleholder.current_sample_md()}
        if 'last_cal' in beamline_config:
            _md['last_cal'] = beamline_config['last_cal']
        if 'last_noise' in beamline_config:
            _md['last_noise'] = beamline_config['last_noise']
        yhints, mcahints, stylehints = get_detector_plot_hints()
        _plot_hints = {'x': motor.hints.get('fields', []),
                       'y': yhints, 'mca': mcahints, 'style': stylehints}
        _plot_hints.update(plot_hints)
        _md['plot_hints'] = _plot_hints
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
def take_dark_counts():
    """Take dark counts to zero current-amplifiers"""
    dc = DocumentCache()

    @subs_decorator(dc)
    def inner():
        shutter_open = yield from is_shutter_open()
        if shutter_open:
            yield from close_shutter()

        # Clear offsets first
        for det in GLOBAL_ACTIVE_DETECTORS:
            detname = det.name
            if hasattr(det, 'offset'):
                det.offset.set(0)

        yield from bp.count(GLOBAL_ACTIVE_DETECTORS, 10, md={"scantype": "darkcounts"})
        run = BlueskyRun(dc)
        table = run.primary.read()
        for det in GLOBAL_ACTIVE_DETECTORS:
            detname = det.name
            if hasattr(det, 'offset'):
                dark_value = float(table[detname].mean().values)
                det.offset.set(dark_value)
        if shutter_open:
            yield from open_shutter()
    return (yield from inner())

def tes_take_noise():
    """Close the shutter and take TES noise. Run after cryostat cycle"""
    @run_decorator(md={"scantype": "noise"})
    def inner_noise():
        beamline_config['last_cal'] = None
        beamline_config['last_noise'] = None
        shutter_open = yield from is_shutter_open()
        if shutter_open:
            yield from close_shutter()
        yield from call_obj(tes, "take_noise")
        if shutter_open:
            yield from open_shutter()
    uid = yield from inner_noise()
    beamline_config['last_noise'] = uid
    return uid



def tes_take_projectors():
    """Take projector data for TES. Run with pulses from cal sample"""
    @run_decorator(md={"scantype": "projectors"})
    def inner_projectors():
        #tes.rpc.file_start(tes.path, write_ljh=True, write_off=False,
        #                   setFilenamePattern=tes.setFilenamePattern)
        #yield from sleep(30)
        #tes._file_end()
        yield from open_shutter()
        yield from call_obj(tes, "take_projectors", time=30)
    return (yield from inner_projectors())

@add_to_plan_list
def tes_setup(should_take_dark_counts=True):
    """Set up TES after cryostat cycle. Must have counts from cal sample.

    should_take_dark_counts: if True, take dark counts for the other
    detectors at the same time.
    """
    if should_take_dark_counts:
        yield from close_shutter()
        deactivate_detector('tes')
        yield from take_dark_counts()
    activate_detector('tes', plot=True)
    yield from tes_take_noise()
    yield from tes_take_projectors()
    yield from call_obj(tes, "make_projectors")
    return (yield from call_obj(tes, "set_projectors"))


def _make_gscan_points(*args, shift=0):
    if len(args) < 3:
        raise TypeError(f"gscan requires at least estart, estop, and delta, received {args}")
    if len(args) % 2 == 0:
        raise TypeError("gscan received an even number of arguments. Either a step or a step-size is missing")
    start = float(args[0])
    points = [start + shift]
    for stop, step in zip(args[1::2], args[2::2]):
        nextpoint = points[-1] + step
        while nextpoint < stop - step/2.0 + shift:
            points.append(nextpoint)
            nextpoint += step
        points.append(stop + shift)
    return points


@add_to_scan_list
def tes_gscan(motor, *args, extra_dets=[], shift=0, **kwargs):
    """A variable step scan of a motor, the TES detector, and the basic beamline detectors. 

    Other detectors may be added via extra_dets

    motor : The motor object to scan
    args : start, stop1, step1, stop2, step2, ...
    extra_dets : A list of detectors to add for just this scan
    """
    points = _make_gscan_points(*args, shift=shift)
    # Move motor to start position first
    yield from mv(motor, points[0])
    return (yield from tes_list_scan(motor, points, extra_dets=extra_dets, **kwargs))


@add_to_scan_list
def tes_calibrate(time, sampleid, exposure_time_s=10, energy=980, md=None):
    """Take energy calibration for TES. Moves to specified sample"""
    yield from sample_move(0, 0, 45, sampleid)
    return (yield from tes_calibrate_inplace(time, exposure_time_s, energy=energy, md=md))


@add_to_scan_list
def tes_calibrate_inplace(time, exposure_time_s=10, energy=980, md=None):
    """Take energy calibration for TES. Does not move sample"""
    yield from mv(tes.cal_flag, True)
    yield from set_edge("blank")
    yield from mv(en.energy, energy)
    pre_cal_exposure = tes.acquire_time.get()
    md = md or {}
    _md = {"scantype": "calibration", "calibration_energy": energy}
    _md.update(md)
    cal_uid = yield from tes_count(int(time//exposure_time_s),
                                   exposure_time_s=exposure_time_s, md=_md)
    yield from mv(tes.cal_flag, False)
    beamline_config['last_cal'] = cal_uid
    yield from set_exposure(pre_cal_exposure)
    return cal_uid


def xas_factory(energy_grid, edge, name):
    @repeat
    @wrap_xas(edge)
    def inner(**kwargs):
        """Parameters
        ----------
        repeat : int
            Number of times to repeat the scan
        **kwargs :
            Arguments to be passed to tes_gscan

        """
        yield from tes_gscan(en.energy, *energy_grid, **kwargs)
    d = f"Perform an in-place xas scan for {edge} with energy pattern {energy_grid} \n"
    inner.__doc__ = d + inner.__doc__

    inner.__qualname__ = name
    inner.__name__ = name
    inner._edge = edge
    inner._short_doc = f"Do XAS for {edge} from {energy_grid[0]} to {energy_grid[-2]}"
    return inner
