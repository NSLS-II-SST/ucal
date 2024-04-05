# from ucal.detectors import tes
from ucal.hw import tes, eslit as energy_slit, en
from sst_funcs.globalVars import GLOBAL_ACTIVE_DETECTORS, GLOBAL_PLOT_DETECTORS
from sst_funcs.detectors import activate_detector, deactivate_detector

# from ucal.energy import en
from sst_funcs.plans.plan_stubs import call_obj, set_exposure
from sst_funcs.plans.scan_decorators import sst_base_scan_decorator
from sst_funcs.shutters import (
    close_shutter,
    open_shutter,
    is_shutter_open,
)
from ucal.scan_exfiltrator import ScanExfiltrator
from ucal.plans.samples import sample_move, GLOBAL_SELECTED
from ucal.multimesh import set_edge
from ucal.configuration import beamline_config
from sst_funcs.help import add_to_plan_list, add_to_scan_list
from bluesky.plan_stubs import mv
from bluesky.preprocessors import run_decorator, subs_decorator
from bluesky_live.bluesky_run import BlueskyRun, DocumentCache
from sst_funcs.plans.preprocessors import wrap_metadata
from sst_funcs.plans.groups import repeat
import bluesky.plans as bp
from sst_funcs.utils import merge_func


def beamline_setup(func):
    @merge_func(func)
    def inner(*args, sample=None, eslit=None, energy=None, **kwargs):
        """
        Parameters
        ----------
        sample : int or str, optional
            The sample id. If not None, the sample is moved into the beam at a 45 degree angle.
        eslit : float, optional
            If not None, will change the beamline exit slit. Note that currently, eslit values are given as -2* the desired exit slit size in mm.
        """
        if sample is not None:
            yield from sample_move(0, 0, 45, sample)
        if eslit is not None:
            yield from mv(energy_slit, eslit)
        if energy is not None:
            yield from mv(en.energy, energy)
        return (yield from func(*args, **kwargs))

    return inner


def wrap_xas_setup(element):
    def decorator(func):
        @merge_func(func)
        def inner(*args, auto_setup_xas=True, **kwargs):
            if auto_setup_xas:
                yield from set_edge(element)
            return (yield from func(*args, **kwargs))

        return inner

    return decorator


def wrap_xas(element):
    def decorator(func):
        return add_to_scan_list(
            wrap_metadata({"edge": element, "scantype": "xas"})(
                wrap_xas_setup(element)(func)
            )
        )

    return decorator


def wrap_xes(func):
    return wrap_metadata({"scantype": "xes"})(func)


def get_detector_plot_hints():
    plot_y_md = []
    plot_array_md = []
    plot_image_md = []
    style_hints = {}
    for detector in GLOBAL_PLOT_DETECTORS:
        if hasattr(detector, "plot_hints"):
            h = detector.plot_hints()
            plot_y_md += h.get("y", [])
            plot_array_md += h.get("array", [])
            plot_image_md += h.get("image", [])
            style_hints.update(h.get("style_hints", {}))
        else:
            plot_y_md += detector.hints.get("fields", [])
    return plot_y_md, plot_array_md, plot_image_md, style_hints


def _ucal_add_processing_md(func):
    @merge_func(func)
    def _inner(*args, md=None, **kwargs):
        md = md or {}
        _md = {}
        if "last_cal" in beamline_config:
            _md["last_cal"] = beamline_config["last_cal"]
        if "last_noise" in beamline_config:
            _md["last_noise"] = beamline_config["last_noise"]
        _md.update(md)
        return (yield from func(*args, md=_md, **kwargs))

    return _inner


@add_to_scan_list
@beamline_setup
def tes_count_old(
    *args,
    **kwargs,
):
    """Count for a specified number of points

    Modifies count to automatically fill
    dets with the TES detector and basic beamline detectors.
    Other detectors may be added on the fly via extra_dets
    ---------------------------------------------------------
    """

    class dummymotor:
        name = "time"
        egu = "index"

    motor = dummymotor()
    scanex = ScanExfiltrator(motor, en.energy.position)
    tes.scanexfiltrator = scanex

    @_ucal_add_processing_md
    @sst_base_scan_decorator
    @wrap_xes
    @merge_func(bp.count)
    def _inner(*args, **kwargs):
        yield from bp.count(*args, **kwargs)

    ret = yield from _inner(*args, **kwargs)

    return ret


def _tes_count_plan_wrapper(plan_function, plan_name):
    class dummymotor:
        name = "time"
        egu = "index"

    @beamline_setup
    @_ucal_add_processing_md
    @sst_base_scan_decorator
    @merge_func(plan_function)
    def _inner(*args, **kwargs):
        motor = dummymotor()
        scanex = ScanExfiltrator(motor, en.energy.position)
        tes.scanexfiltrator = scanex
        ret = yield from plan_function(*args, **kwargs)

        return ret

    d = f"""Modifies {plan_function.__name__} to automatically fill
dets with the TES detector and basic beamline detectors.
Other detectors may be added on the fly via extra_dets
---------------------------------------------------------
"""

    _inner.__doc__ = d + _inner.__doc__
    _inner.__name__ = plan_name
    return _inner


def _tes_plan_wrapper(plan_function, plan_name):
    @beamline_setup
    @_ucal_add_processing_md
    @sst_base_scan_decorator
    @merge_func(plan_function, ["motor"])
    def _inner(detectors, motor, *args, **kwargs):
        scanex = ScanExfiltrator(motor, en.energy.position)
        tes.scanexfiltrator = scanex
        ret = yield from plan_function(detectors, motor, *args, **kwargs)

        return ret

    d = f"""Modifies {plan_function.__name__} to automatically fill
dets with the TES detector and basic beamline detectors.
Other detectors may be added on the fly via extra_dets
---------------------------------------------------------
"""

    _inner.__doc__ = d + _inner.__doc__
    _inner.__name__ = plan_name
    return _inner


tes_count = add_to_scan_list(_tes_count_plan_wrapper(bp.count, "tes_count"))
tes_xes = add_to_scan_list(wrap_metadata({"plan_name": "tes_xes"})(wrap_xes(tes_count)))
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
            if hasattr(det, "offset"):
                det.offset.set(0)

        yield from bp.count(GLOBAL_ACTIVE_DETECTORS, 10, md={"scantype": "darkcounts"})
        run = BlueskyRun(dc)
        table = run.primary.read()
        for det in GLOBAL_ACTIVE_DETECTORS:
            detname = det.name
            if hasattr(det, "offset"):
                dark_value = float(table[detname].mean().values)
                det.offset.set(dark_value)
        if shutter_open:
            yield from open_shutter()

    return (yield from inner())


def tes_take_noise():
    """Close the shutter and take TES noise. Run after cryostat cycle"""

    @run_decorator(md={"scantype": "noise"})
    def inner_noise():
        beamline_config["last_cal"] = None
        beamline_config["last_noise"] = None
        shutter_open = yield from is_shutter_open()
        if shutter_open:
            yield from close_shutter()
        yield from call_obj(tes, "take_noise")
        if shutter_open:
            yield from open_shutter()

    uid = yield from inner_noise()
    beamline_config["last_noise"] = uid
    return uid


def tes_take_projectors():
    """Take projector data for TES. Run with pulses from cal sample"""

    @run_decorator(md={"scantype": "projectors"})
    def inner_projectors():
        # tes.rpc.file_start(tes.path, write_ljh=True, write_off=False,
        #                   setFilenamePattern=tes.setFilenamePattern)
        # yield from sleep(30)
        # tes._file_end()
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
        deactivate_detector("tes")
        yield from take_dark_counts()
    activate_detector("tes")
    yield from tes_take_noise()
    yield from tes_take_projectors()
    yield from call_obj(tes, "make_projectors")
    return (yield from call_obj(tes, "set_projectors"))


def _make_gscan_points(*args, shift=0):
    if len(args) < 3:
        raise TypeError(
            f"gscan requires at least estart, estop, and delta, received {args}"
        )
    if len(args) % 2 == 0:
        raise TypeError(
            "gscan received an even number of arguments. Either a step or a step-size is missing"
        )
    start = float(args[0])
    points = [start + shift]
    for stop, step in zip(args[1::2], args[2::2]):
        nextpoint = points[-1] + step
        while nextpoint < stop - step / 2.0 + shift:
            points.append(nextpoint)
            nextpoint += step
        points.append(stop + shift)
    return points


@add_to_scan_list
@merge_func(tes_list_scan, omit_params=["points"], exclude_wrapper_args=False)
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
def tes_calibrate_old(time, sampleid, exposure_time_s=10, energy=980, md=None):
    """Take energy calibration for TES. Moves to specified sample"""
    yield from sample_move(0, 0, 45, sampleid)
    return (
        yield from tes_calibrate_inplace(time, exposure_time_s, energy=energy, md=md)
    )


@add_to_scan_list
@merge_func(tes_count, ["num", "delay"])
def tes_calibrate(time, dwell=10, energy=980, md=None, **kwargs):
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
    yield from mv(tes.cal_flag, True)
    yield from set_edge("blank")
    yield from mv(en.energy, energy)
    pre_cal_exposure = tes.acquire_time.get()
    md = md or {}
    _md = {"scantype": "calibration", "calibration_energy": energy}
    _md.update(md)
    cal_uid = yield from tes_count(int(time // dwell), dwell=dwell, md=_md, **kwargs)
    yield from mv(tes.cal_flag, False)
    beamline_config["last_cal"] = cal_uid
    yield from set_exposure(pre_cal_exposure)
    return cal_uid


def xas_factory(energy_grid, edge, name):
    @repeat
    @wrap_xas(edge)
    @wrap_metadata({"plan_name": name})
    @merge_func(tes_gscan, omit_params=["motor", "args"])
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
