from sst_funcs.hw import manipulator, en, Exit_Slit as eslit
from sst_funcs.hw import *
from sst_funcs.motors import add_motor

add_motor(manipx, "Manipulator X", "manipx")
add_motor(manipy, "Manipulator Y", "manipy")
add_motor(manipz, "Manipulator Z", "manipz")
add_motor(manipr, "Manipulator R", "manipr")

en.rotation_motor = manipulator.r
