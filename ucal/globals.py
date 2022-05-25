GLOBAL_DETECTORS = {}
GLOBAL_DETECTOR_DESCRIPTIONS = {}
GLOBAL_ACTIVE_DETECTORS = []
GLOBAL_MOTORS = {}
GLOBAL_MOTOR_DESCRIPTIONS = {}


def add_detector(det, description="", name=None):
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

    """
    if name is None:
        name = det.name
    GLOBAL_DETECTORS[name] = det
    GLOBAL_DETECTOR_DESCRIPTIONS[name] = description


def add_motor(motor, description="", name=None):
    if name is None:
        name = motor.name
    GLOBAL_MOTORS[name] = motor
    GLOBAL_MOTOR_DESCRIPTIONS[name] = description


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


def activate_detector(name):
    """Activate a detector so that is is measured by default

    Parameters
    ----------
    name : str
        The name of a detector in the global detector buffer

    """
    detector = GLOBAL_DETECTORS[name]
    if detector not in GLOBAL_ACTIVE_DETECTORS:
        GLOBAL_ACTIVE_DETECTORS.append(detector)


def deactivate_detector(name):
    """Deactivate a detector so that it is not measured by default

    Parameters
    ----------
    name : str
        The name of a detector in the global detector buffer

    """

    detector = GLOBAL_DETECTORS[name]
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


def remove_motor(motor_or_name):
    if hasattr(motor_or_name, "name"):
        name = motor_or_name.name
    else:
        name = motor_or_name
    if name not in GLOBAL_MOTORS:
        name = None
        for k, v in GLOBAL_MOTORS.items():
            if v == motor_or_name:
                name = k
                break
    if name is None:
        raise KeyError(f"Motor {motor_or_name} not found in global motors dictionary")

    del GLOBAL_MOTORS[name]
    del GLOBAL_MOTOR_DESCRIPTIONS[name]


def list_motors(describe=False):
    for name, det in GLOBAL_MOTORS.items():
        print(f"{name}: {det.position}")
        if describe:
            print(f"{GLOBAL_MOTOR_DESCRIPTIONS[name]}")
