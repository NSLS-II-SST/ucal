from nbs_bl.hw import manipulator, en, Exit_Slit as eslit
from nbs_bl.hw import *
from nbs_bl.motors import add_motor

add_motor(manipx, "Manipulator X", "manipx")
add_motor(manipy, "Manipulator Y", "manipy")
add_motor(manipz, "Manipulator Z", "manipz")
add_motor(manipr, "Manipulator R", "manipr")

en.rotation_motor = manipulator.r
