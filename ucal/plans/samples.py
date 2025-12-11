from nbs_bl.help import add_to_func_list, add_to_plan_list
from bluesky.plan_stubs import mv
from nbs_bl.samples import set_sample
from nbs_bl.beamline import GLOBAL_BEAMLINE as bl


@add_to_plan_list
def set_side(side_num):
    """Set sample to side, origin edge
    side_num : int
    """
    sampleid = f"side{side_num}"
    yield from set_sample(sampleid)


@add_to_plan_list
def manual_sample_move(x, y, z, r, name, sample_id=-1):
    bl.current_sample.clear()
    bl.current_sample["sample_id"] = sample_id
    bl.current_sample["name"] = name
    bl.current_sample["origin"] = "manual"
    manipulator = bl["manipulator"]
    yield from mv(manipulator.x, x, manipulator.y, y, manipulator.z, z, manipulator.r, r)
