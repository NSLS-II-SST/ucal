from ucal.sampleholder import sampleholder, refholder
from ucal.motors import samplex, sampley, samplez, sampler
from ucal.configuration import beamline_config
from sst_base.sampleholder import make_two_sided_bar, make_regular_polygon
from bluesky.plan_stubs import mv, abs_set
from os.path import abspath
import csv

#filename = "../../examples/sample_load.csv"


def read_sample_csv(filename):
    with open(filename, 'r') as f:
        sampleReader = csv.reader(f)
        samplelist = [row for row in sampleReader]
        # rownames = [n for n in samplelist[0] if n != ""]
        rownames = ["sample_id", "sample_name", "side", "x1", "y1", "x2", "y2",
                    "t", "tags"]
        samples = {}
        for sample in samplelist[1:]:
            sample_id = sample[0]
            sample_dict = {key: sample[rownames.index(key)] for
                           key in rownames[1:-1]}
            sample_tags = sample[rownames.index("tags"):]
            sample_dict['tags'] = [t for t in sample_tags if t != ""]
            samples[sample_id] = sample_dict
    return samples


def load_sample_dict_into_holder(samples, holder, clear=True):
    """
    Sample dictionary
    """
    if clear:
        holder.clear_samples()
    for sample_id, s in samples.items():
        position = (float(s['x1']), float(s['y1']), float(s['x2']), float(s['y2']))
        name = s['sample_name']
        side = int(s['side'])
        thickness = float(s['t'])
        holder.add_sample(sample_id, name, position, side, thickness)
    return


def load_sample_dict(samples):
    load_sample_dict_into_holder(samples, sampleholder)


def load_samples_into_holder(filename, holder, **kwargs):
    samples = read_sample_csv(filename)
    load_sample_dict_into_holder(samples, holder, **kwargs)


def load_standard_two_sided_bar(filename):
    bar = make_two_sided_bar(13, 300, 2)
    sampleholder.add_geometry(bar)
    beamline_config['loadfile'] = abspath(filename)
    beamline_config['bar'] = "Standard 2-sided bar"
    load_samples_into_holder(filename, sampleholder, clear=False)


def load_standard_four_sided_bar(filename):
    bar = make_regular_polygon(24.5, 215, 4)
    sampleholder.add_geometry(bar)
    beamline_config['loadfile'] = abspath(filename)
    beamline_config['bar'] = "Standard 4-sided bar"
    load_samples_into_holder(filename, sampleholder, clear=False)


def load_samples(filename):
    beamline_config['loadfile'] = abspath(filename)
    load_samples_into_holder(filename, sampleholder)


def set_side(side_num):
    """
    Set sample to side, origin edge
    side_num : int
    """
    sampleid = f"side{side_num}"
    yield from set_sample_edge(sampleid)

def set_ref(edge):
    ref_dict = {"c": 0, "n": 3, "o": 4, "f": 2, "ca": 2,
                "ti": 3, "v": 4, "cr": 6, "mn": 5, "fe": 6,
                "co": 6, "ni": 6, "photodiode": 8, "empty": 7}
    sampleid = ref_dict.get(edge.lower(), 6)
    yield from abs_set(refholder, sampleid, origin="center")

def set_sample(sampleid, origin="center"):
    yield from abs_set(sampleholder, sampleid, origin=origin)


def set_sample_center(sampleid):
    yield from set_sample(sampleid, origin="center")


def set_sample_edge(sampleid):
    yield from set_sample(sampleid, origin='edge')


def sample_move(x, y, r, sampleid=None, **kwargs):
    if sampleid is not None:
        yield from set_sample(sampleid, **kwargs)
    yield from mv(samplex, x, sampley, y, samplez, 0, sampler, r)


def list_samples():
    print("Samples loaded in sampleholder")
    for v in sampleholder.sample_md.values():
        if v['sample_id'] == 'null':
            pass
        else:
            print(f"id: {v['sample_id']}, name: {v['sample_name']}: ")
