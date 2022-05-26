from . import STATION_NAME

from ophyd import Device

GLOBAL_DETECTORS = {}
GLOBAL_DETECTOR_DESCRIPTIONS = {}
GLOBAL_ACTIVE_DETECTORS = []
SCAN_ACTIVE_DETECTORS = []


def add_detector(det, description="", name=None, activate=True):
    """Add a detector to the global detector buffer

    with an optional description, and an optional name to substitute
    for the detector's built-in name

    Parameters
    ----------
    det : Ophyd device
        A detector to add to the buffer
    description : str
        An optional string that identifies the detector
    name : str
        a string to use as a key, instead of det.name
    activate : bool
        Whether to add the detector to the active detectors list

    Returns
    -------
    name : str
        The key used to insert the detector into the detector list
    """
    if name is None:
        name = det.name
    GLOBAL_DETECTORS[name] = det
    GLOBAL_DETECTOR_DESCRIPTIONS[name] = description
    if activate:
        activate_detector(name)
    return name


def list_detectors(describe=False):
    """List all global detectors, optionally provide text descriptions

    Parameters
    ----------
    describe : Bool
        If True, print the text description of each detector

    """
    for name, det in GLOBAL_DETECTORS.items():
        if det in GLOBAL_ACTIVE_DETECTORS:
            status = "active"
        else:
            status = "inactive"
        print(f"{name}: {status}")
        if describe:
            print(f"{GLOBAL_DETECTOR_DESCRIPTIONS[name]}")


def get_detector(det_or_name):
    """

    Given either a name, or a detector instance, return a detector
    instance. If given a name, return the corresponding detector from
    GLOBAL_DETECTORS.

    Parameters
    ----------
    det_or_name : str or Device
        A name of a detector in GLOBAL_DETECTORS, or a detector
        instance

    Raises
    ------
    KeyError
        If a name is passed that is not in GLOBAL_DETECTORS

    Returns
    -------
    A detector instance

    """
    if isinstance(det_or_name, Device):
        return det_or_name
    elif det_or_name in GLOBAL_DETECTORS:
        return GLOBAL_DETECTORS[det_or_name]
    else:
        raise KeyError(f"Detector {det_or_name} not found in GLOBAL_DETECTORS")


def activate_detector(det_or_name):
    """Activate a detector so that is is measured by default

    Parameters
    ----------
    det_or_name : device or str
        Either a device, or the name of a device in the global
        detector buffer

    """
    detector = get_detector(det_or_name)
    if detector not in GLOBAL_ACTIVE_DETECTORS:
        GLOBAL_ACTIVE_DETECTORS.append(detector)


def deactivate_detector(det_or_name):
    """Deactivate a detector so that it is not measured by default

    Parameters
    ----------
    det_or_name : device or str
        Either a device, or the name of a device in the global
        detector buffer

    """

    detector = get_detector(det_or_name)
    if detector in GLOBAL_ACTIVE_DETECTORS:
        idx = GLOBAL_ACTIVE_DETECTORS.index(detector)
        GLOBAL_ACTIVE_DETECTORS.pop(idx)


def remove_detector(det_or_name):
    """Remove a detector from the global detector buffer entirely

    Parameters
    ----------
    det_or_name : device or str
        Either a device, or the name of a device in the global
        detector buffer

    Raises
    ------
    KeyError
        Detector not found in the global buffer

    """
    if hasattr(det_or_name, "name"):
        name = det_or_name.name
    else:
        name = det_or_name
    if name not in GLOBAL_DETECTORS:
        name = None
        for k, v in GLOBAL_DETECTORS.items():
            if v == det_or_name:
                name = k
                break
    if name is None:
        raise KeyError(f"Detector {det_or_name} not found in global counters dictionary")

    del GLOBAL_DETECTORS[name]
    del GLOBAL_DETECTOR_DESCRIPTIONS[name]


if STATION_NAME == "sst_sim":
    from sst_common_sim.api import sc, i0, i1, ref, thresholds, tes
    basic_dets = [sc, i0, i1, ref]
    add_detector(sc)
    add_detector(i0)
    add_detector(i1)
    add_detector(ref)
    add_detector(tes)

if STATION_NAME == "ucal":
    from ucal_hw.detectors import ucal_i400, dm7_i400, tes

    add_detector(ucal_i400, "Small electric signals on ucal")
    add_detector(dm7_i400, "Large electric signals on ucal")
    add_detector(tes, "Transition-edge Sensor")
