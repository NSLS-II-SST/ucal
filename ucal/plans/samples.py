from ucal.sampleholder import sampleholder
from ucal.hw import samplex, sampley, samplez, sampler, manipx, manipy, manipz, manipr
from ucal.configuration import beamline_config
from nbs_bl.help import add_to_func_list, add_to_plan_list
from sst_base.sampleholder import make_two_sided_bar, make_regular_polygon
from bluesky.plan_stubs import mv, abs_set
from os.path import abspath
import csv
import copy
from nbs_bl.globalVars import GLOBAL_SAMPLES, GLOBAL_SELECTED

# filename = "../../examples/sample_load.csv"


def read_sample_csv(filename):
    with open(filename, "r") as f:
        sampleReader = csv.reader(f, skipinitialspace=True)
        samplelist = [row for row in sampleReader]
        rownames = [n for n in samplelist[0] if n != ""]
        # rownames = ["sample_id", "sample_name", "side", "x1", "y1", "x2", "y2",
        #            "t", "tags"]
        samples = {}
        for sample in samplelist[1:]:
            sample_id = sample[0]
            sample_dict = {
                key: sample[rownames.index(key)]
                for key in rownames[1:]
                if sample[rownames.index(key)] != ""
            }
            # sample_tags = sample[rownames.index("tags"):]
            # sample_dict['tags'] = [t for t in sample_tags if t != ""]
            samples[sample_id] = sample_dict
    return samples


def load_sample_dict_into_holder(samples, holder, clear=True):
    """
    Sample dictionary
    """
    if clear:
        holder.clear_samples()
        GLOBAL_SAMPLES.clear()
    for sample_id, s in samples.items():
        sdict = copy.deepcopy(s)
        position = (
            float(sdict.pop("x1")),
            float(sdict.pop("y1")),
            float(sdict.pop("x2")),
            float(sdict.pop("y2")),
        )
        name = sdict.pop("sample_name")
        description = sdict.pop("description", name)
        side = int(sdict.pop("side"))
        thickness = float(sdict.pop("t", 0))
        add_sample_to_globals(
            sample_id, name, position, side, thickness, description, **sdict
        )
        holder.add_sample(
            sample_id, name, position, side, thickness, description=description, **sdict
        )
    return


def add_sample_to_globals(
    sample_id, name, position, side, thickness, description=None, **kwargs
):
    GLOBAL_SAMPLES[sample_id] = {
        "name": name,
        "position": position,
        "side": side,
        "thickness": thickness,
        "description": description,
        **kwargs,
    }


def load_sample_dict(samples):
    load_sample_dict_into_holder(samples, sampleholder)


def load_samples_into_holder(filename, holder, **kwargs):
    samples = read_sample_csv(filename)
    load_sample_dict_into_holder(samples, holder, **kwargs)


def load_standard_two_sided_bar(filename):
    bar = make_two_sided_bar(13, 300, 2)
    sampleholder.add_geometry(bar)
    beamline_config["loadfile"] = abspath(filename)
    beamline_config["bar"] = "Standard 2-sided bar"
    load_samples_into_holder(filename, sampleholder, clear=False)


def load_standard_four_sided_bar(filename):
    bar = make_regular_polygon(24.5, 215, 4)
    sampleholder.add_geometry(bar)
    beamline_config["loadfile"] = abspath(filename)
    beamline_config["bar"] = "Standard 4-sided bar"
    load_samples_into_holder(filename, sampleholder, clear=False)


def load_samples(filename):
    beamline_config["loadfile"] = abspath(filename)
    load_samples_into_holder(filename, sampleholder)


@add_to_plan_list
def set_side(side_num):
    """Set sample to side, origin edge
    side_num : int
    """
    sampleid = f"side{side_num}"
    yield from set_sample_edge(sampleid)


def set_sample(sampleid, origin="center"):
    print(f"Setting sample to {sampleid}")
    sample_info = GLOBAL_SAMPLES.get(str(sampleid), {})
    GLOBAL_SELECTED.clear()
    GLOBAL_SELECTED["sample_id"] = sampleid
    GLOBAL_SELECTED["origin"] = origin
    GLOBAL_SELECTED.update(sample_info)
    yield from abs_set(sampleholder, sampleid, origin=origin)


def set_sample_center(sampleid):
    yield from set_sample(sampleid, origin="center")


def set_sample_edge(sampleid):
    yield from set_sample(sampleid, origin="edge")


@add_to_plan_list
def print_selected_sample():
    """Print info about the currently selected sample"""
    if GLOBAL_SELECTED.get("sample_id", None) is not None:
        print(f"Current sample id: {GLOBAL_SELECTED['sample_id']}")
        print(f"Current sample name: {GLOBAL_SELECTED.get('name', '')}")
    else:
        print(f"No sample currently selected")


@add_to_plan_list
def sample_move(x, y, r, sampleid=None, **kwargs):
    """Move to a specified point on a sample"""
    if sampleid is not None:
        yield from set_sample(sampleid, **kwargs)
    yield from mv(samplex, x, sampley, y, samplez, 0, sampler, r)


@add_to_plan_list
def manual_sample_move(x, y, z, r, name, sample_id=-1):
    GLOBAL_SELECTED.clear()
    GLOBAL_SELECTED["sample_id"] = sample_id
    GLOBAL_SELECTED["name"] = name
    GLOBAL_SELECTED["origin"] = "manual"
    yield from mv(manipx, x, manipy, y, manipz, z, manipr, r)


@add_to_func_list
def list_samples():
    """List the currently loaded samples"""

    print("Samples loaded in sampleholder")
    for v in sampleholder.sample_md.values():
        if v["sample_id"] == "null":
            pass
        else:
            print(f"id: {v['sample_id']}, name: {v['name']}")
