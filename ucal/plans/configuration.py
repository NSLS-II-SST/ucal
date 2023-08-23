from ucal.mirrors import mir4
from ucal.motors import manipz, i0upAu
from bluesky.plan_stubs import mv

def setup_ucal():
    # Set mir4 consistently, ask Cherno what these values are and why
    # x: 30
    # y: 0
    # z: 0.00017
    # yaw: 2.504
    # pitch: -0.625
    # roll: 1.44e-5
    yield from mv(mir4.x, 30)
    yield from mv(i0upAu, 78)

# Eventually need a cleanup ucal function that moves manipulator out of the way but this is
# too dangerous without any interlocks
    
