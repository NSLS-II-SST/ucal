#from . import STATION_NAME

from sst_funcs.help import add_to_func_list
from sst_funcs.printing import boxed_text
from .instantiation import findAndLoadDevice
from .status import StatusDict
from .queueserver import add_status

GLOBAL_MOTORS = StatusDict()
GLOBAL_MOTOR_DESCRIPTIONS = StatusDict()

add_status("MOTORS", GLOBAL_MOTORS)
add_status("MOTOR_DESCRIPTIONS", GLOBAL_MOTOR_DESCRIPTIONS)


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


@add_to_func_list
def list_motors(describe=False):
    """List the most important motors and their current positions"""

    title = "Motors"
    text = []
    for name, det in GLOBAL_MOTORS.items():
        text.append(f"{name}: {det.position}")
        if describe:
            text.append(f"    {GLOBAL_MOTOR_DESCRIPTIONS[name]}")
    boxed_text(title, text, "white")


manipulator = findAndLoadDevice("manipulator")

manipx = manipulator.x
manipy = manipulator.y
manipz = manipulator.z
manipr = manipulator.r

samplex = manipulator.sx
sampley = manipulator.sy
samplez = manipulator.sz
sampler = manipulator.sr

tesz = findAndLoadDevice("tesz")
eslit = findAndLoadDevice("Exit_Slit")
i0upAu = findAndLoadDevice("i0upAu")

add_motor(manipx, "Manipulator X", "manipx")
add_motor(manipy, "Manipulator Y", "manipy")
add_motor(manipz, "Manipulator Z", "manipz")
add_motor(manipr, "Manipulator R", "manipr")
add_motor(tesz, "TES Position", "tesz")
add_motor(eslit, "Exit Slit", "eslit")
add_motor(i0upAu, "I0 gold mesh", "i0upAu")
