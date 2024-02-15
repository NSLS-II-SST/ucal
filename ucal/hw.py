from sst_funcs.hw import manipulator, en, Exit_Slit as eslit
from sst_funcs.hw import *
from sst_funcs.motors import add_motor

manipx = manipulator.x
manipy = manipulator.y
manipz = manipulator.z
manipr = manipulator.r

samplex = manipulator.sx
sampley = manipulator.sy
samplez = manipulator.sz
sampler = manipulator.sr

add_motor(manipx, "Manipulator X", "manipx")
add_motor(manipy, "Manipulator Y", "manipy")
add_motor(manipz, "Manipulator Z", "manipz")
add_motor(manipr, "Manipulator R", "manipr")

ip = get_ipython()

ip.user_ns['manipx'] = manipx
ip.user_ns['manipy'] = manipy
ip.user_ns['manipz'] = manipz
ip.user_ns['manipr'] = manipr
ip.user_ns['samplex'] = samplex
ip.user_ns['sampley'] = sampley
ip.user_ns['samplez'] = samplez
ip.user_ns['sampler'] = sampler

en.rotation_motor = manipr
energy = en.energy

ip.user_ns['energy'] = energy
