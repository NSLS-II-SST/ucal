from . import STATION_NAME
GLOBAL_MOTORS = {}
GLOBAL_MOTOR_DESCRIPTIONS = {}


def add_motor(motor, description="", name=None):
    if name is None:
        name = motor.name
    GLOBAL_MOTORS[name] = motor
    GLOBAL_MOTOR_DESCRIPTIONS[name] = description


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


if STATION_NAME == "sst_sim":
    from sst_common_sim.api import manipulator, multimesh

if STATION_NAME == "ucal":
    from ucal_hw.motors import tesz
    from ucal_hw.manipulator import (manipulator,
                                     manipx, manipy, manipz, manipr,
                                     samplex, sampley, samplez, sampler)
    from sst_hw.motors import Exit_Slit as eslit
    from sst_hw.manipulator import multimesh

    eslit.name = "eslit"

    add_motor(manipx, "Manipulator X", "manipx")
    add_motor(manipy, "Manipulator Y", "manipy")
    add_motor(manipz, "Manipulator Z", "manipz")
    add_motor(manipr, "Manipulator R", "manipr")
    add_motor(tesz, "TES Position", "tesz")
    add_motor(eslit, "Exit Slit", "eslit")

"""
Disabled 20211013, too complex for testing, unnecessary
    motors = [samplex, sampley, samplez, sampler]

    return SimpleNamespace(samplex=samplex,
                           sampley=sampley,
                           samplez=samplez,
                           sampler=sampler,
                           framex=framex,
                           framey=framey,
                           framez=framez,
                           framer=framer,
                           manipulator=manipulator,
                           sample_holder=sample_holder,
                           motors=motors)


globals().update(_motors().__dict__)
"""
