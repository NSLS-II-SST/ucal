#from .instantiation import findAndLoadDevice
from sst_funcs.motors import add_motor
from sst_funcs import manipulator
# manipulator = findAndLoadDevice("manipulator")

manipx = manipulator.x
manipy = manipulator.y
manipz = manipulator.z
manipr = manipulator.r

samplex = manipulator.sx
sampley = manipulator.sy
samplez = manipulator.sz
sampler = manipulator.sr

#tesz = findAndLoadDevice("tesz")
#eslit = findAndLoadDevice("Exit_Slit")
#i0upAu = findAndLoadDevice("i0upAu")

add_motor(manipx, "Manipulator X", "manipx")
add_motor(manipy, "Manipulator Y", "manipy")
add_motor(manipz, "Manipulator Z", "manipz")
add_motor(manipr, "Manipulator R", "manipr")
#add_motor(tesz, "TES Position", "tesz")
#add_motor(eslit, "Exit Slit", "eslit")
#add_motor(i0upAu, "I0 gold mesh", "i0upAu")
