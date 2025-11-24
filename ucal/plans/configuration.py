# from ucal.mirrors import mir4, mir3
from ucal.hw import mir1, mir3, mir4, i0upAu
from ucal.hw import manipz, en
from bluesky.plan_stubs import mv, rd
from nbs_bl.help import add_to_plan_list


@add_to_plan_list
def setup_ucal():
    """Set mirrors, i0upAu, and mono to default parameters"""
    yield from setup_mirrors()
    yield from setup_manipulators()
    yield from setup_mono()

@add_to_plan_list
def setup_mirrors():
    # Set mir4 consistently, ask Cherno what these values are and why

    m3x = 24.2
    m3y = 18
    m3z = 0
    m3yaw = 0
    m3pitch = 7.78
    m3roll = 0

    m1pitch = 0.57
    m1x = -0.5

    m4x = 27.5
    m4y = 0
    m4z = 0 
    m4yaw = 2.504
    m4pitch = -0.65
    m4roll = 0
    
    pairs = [(mir4.x, m4x), (mir4.y, m4y), (mir4.z, m4z), (mir4.yaw, m4yaw),
             (mir4.pitch, m4pitch), (mir4.roll, m4roll), (mir3.x, m3x),
             (mir3.y, m3y), (mir3.z, m3z), (mir3.pitch, m3pitch), (mir3.roll, m3roll),
             (mir3.yaw, m3yaw), (mir1.pitch, m1pitch), (mir1.x, m1x)]
    for pair in pairs:
        yield from mv(pair[0], pair[1], timeout=60)
    

def setup_manipulators():
    yield from mv(i0upAu, 78)


def setup_mono():
    """
    Sane default mono parameters
    """

    grating = yield from rd(en.monoen.gratingx.readback)
    mono = en.monoen
    if "1200l/mm" in grating:
        yield from mv(mono.cff, 2.05)
        yield from mv(mono.grating.user_offset, -54.2895)
        yield from mv(mono.mirror2.user_offset, 37.1176)
    elif "250l/mm" in grating:
        yield from mv(mono.cff, 1.5)
        yield from mv(mono.grating.user_offset, -54.3276)
        yield from mv(mono.mirror2.user_offset, 37.0976)


# Eventually need a cleanup ucal function that moves manipulator out of the way but this is
# too dangerous without any interlocks
