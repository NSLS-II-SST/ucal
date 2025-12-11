from nbs_bl.beamline import GLOBAL_BEAMLINE as bl
from nbs_bl.plans.plan_stubs import call_obj, sampleholder_move_sample
from nbs_bl.help import add_to_plan_list
from bluesky.plan_stubs import rd, mv

# from ucal.shutters import psh7


@add_to_plan_list
def manipulator_to_loadlock():
    """Moves manipulator up into the loadlock chamber"""
    manipulator = bl["manipulator"]
    yield from mv(
        manipulator.x, 0, manipulator.y, 0, manipulator.r, 0, manipulator.z, 20
    )


@add_to_plan_list
def manipulator_to_main():
    """Moves manipulator down into the measurement chamber"""
    manipulator = bl["manipulator"]
    yield from mv(
        manipulator.x, 0, manipulator.y, 0, manipulator.r, 0, manipulator.z, 250
    )


def update_manipulator_side(side, *args):
    """
    Sides are numbered starting at 1
    """
    manipulator = bl["manipulator"]
    yield from call_obj(manipulator.holder, "update_side", side - 1, *args)


def set_edge(edge):
    yield from sampleholder_move_sample(bl.reference_sampleholder, edge)


'''

@add_to_plan_list
def open_shutter():
    """Opens shutter 7, does not check any other shutters!"""
    yield from psh7.open()


@add_to_plan_list
def close_shutter():
    """Closes shutter 7"""
    yield from psh7.close()

def is_shutter_open():
    state = yield from rd(psh7.state)
    if state == 1:
        return False
    else:
        return True
'''
