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


def setup_mirrors():
    # Set mir4 consistently, ask Cherno what these values are and why
    # x: 30
    # y: 0
    # z: 0.00017
    # yaw: 2.504
    # pitch: -0.625
    # roll: 1.44e-5

    yield from mv(mir4.x, 27.5)
    yield from mv(mir4.y, 0)
    yield from mv(mir4.z, 0.00199)
    yield from mv(mir4.yaw, 2.504)
    yield from mv(mir4.pitch, -0.625)
    yield from mv(mir4.roll, -0.00)
    yield from mv(mir3.x, 26.7)
    yield from mv(mir3.y, 18)
    yield from mv(mir3.z, 0)
    yield from mv(mir3.pitch, 7.89)
    yield from mv(mir3.yaw, 0)
    yield from mv(mir3.roll, 0)
    yield from mv(mir1.pitch, 0.68)


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
