from nbs_bl.hw import samplex, sampley, samplez, sampler, manipx, manipy, manipz, manipr
from nbs_bl.help import add_to_func_list, add_to_plan_list
from bluesky.plan_stubs import mv
from nbs_bl.samples import set_sample
from nbs_bl.beamline import GLOBAL_BEAMLINE


@add_to_plan_list
def set_side(side_num):
    """Set sample to side, origin edge
    side_num : int
    """
    sampleid = f"side{side_num}"
    yield from set_sample(sampleid)


@add_to_plan_list
def manual_sample_move(x, y, z, r, name, sample_id=-1):
    GLOBAL_BEAMLINE.current_sample.clear()
    GLOBAL_BEAMLINE.current_sample["sample_id"] = sample_id
    GLOBAL_BEAMLINE.current_sample["name"] = name
    GLOBAL_BEAMLINE.current_sample["origin"] = "manual"
    yield from mv(manipx, x, manipy, y, manipz, z, manipr, r)
