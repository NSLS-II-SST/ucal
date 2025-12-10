# from ucal.hw import tes, eslit as energy_slit, en
from nbs_bl.beamline import (
    # GLOBAL_ACTIVE_DETECTORS,
    GLOBAL_BEAMLINE,
)
from nbs_bl.detectors import activate_detector, deactivate_detector

# from ucal.energy import en
from nbs_bl.plans.plan_stubs import call_obj, set_exposure
from nbs_bl.plans.scan_decorators import nbs_base_scan_decorator
from nbs_bl.shutters import (
    close_shutter,
    open_shutter,
    is_shutter_open,
)
from nbs_bl.plans.flyscan_base import fly_scan
from ucal.scan_exfiltrator import ScanExfiltrator
from nbs_bl.samples import move_sample
from ucal.plans.plan_stubs import set_edge

# from ucal.configuration import beamline_config
from nbs_bl.help import add_to_plan_list, add_to_scan_list
from bluesky.plan_stubs import mv, abs_set
from bluesky.preprocessors import run_decorator, subs_decorator
from bluesky_live.bluesky_run import BlueskyRun, DocumentCache
from nbs_bl.plans.preprocessors import wrap_metadata
import bluesky.plans as bp
from nbs_bl.utils import merge_func
import numpy as np


@add_to_scan_list
def take_dark_counts():
    """Take dark counts to zero current-amplifiers"""
    dc = DocumentCache()

    @subs_decorator(dc)
    def inner():
        yield from set_exposure(1.0)
        shutter_open = yield from is_shutter_open()
        if shutter_open:
            yield from close_shutter()

        # Clear offsets first
        for det in GLOBAL_BEAMLINE.detectors.active:
            detname = det.name
            if hasattr(det, "offset"):
                det.offset.set(0).wait()

        yield from bp.count(
            GLOBAL_BEAMLINE.detectors.active, 10, md={"scantype": "darkcounts"}
        )
        run = BlueskyRun(dc)
        table = run.primary.read()
        for det in GLOBAL_BEAMLINE.detectors.active:
            detname = det.name
            if hasattr(det, "offset"):
                dark_value = float(table[detname].mean().values)
                if np.isfinite(dark_value):
                    det.offset.set(dark_value).wait()
        if shutter_open:
            yield from open_shutter()

    return (yield from inner())


@add_to_scan_list
@nbs_base_scan_decorator
@merge_func(fly_scan, ["detectors", "motor"], use_func_name=False)
def en_flyscan(detectors, *args, **kwargs):
    yield from fly_scan(detectors, GLOBAL_BEAMLINE.energy, *args, **kwargs)


