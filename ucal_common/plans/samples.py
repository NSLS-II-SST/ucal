from ucal_common.sampleholder import sampleholder
from ucal_common.motors import samplex, sampley, samplez, sampler
from ucal_common.configuration import beamline_config
from sst_base.sampleholder import make_two_sided_bar
from bluesky.plan_stubs import mv, abs_set
import csv

filename = "../../examples/sample_load.csv"


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


def load_samples_dict_into_holder(samples, holder):
    """
    Sample dictionary
    """
    for sample_id, s in samples.items():
        position = (s['x1'], s['y1'], s['x2'], s['y2'])
        name = s['sample_name']
        side = s['side']
        thickness = s['t']
        holder.add_sample(sample_id, name, position, side, thickness)
    return


def load_standard_two_sided_bar():
    bar = make_two_sided_bar(13, 300, 2)
    sampleholder.add_geometry(bar)


def load_samples_into_holder(filename, holder):
    holder._reset()
    samples = read_sample_csv(filename)
    load_samples_dict_into_holder(samples, holder)


def load_samples(filename):
    beamline_config['loadfile'] = filename
    load_samples_into_holder(filename, sampleholder)


def set_side(side_num):
    yield from abs_set(sampleholder, "side%d" % side_num)


def set_sample(sampleid, origin="center"):
    yield from abs_set(sampleholder, sampleid, origin=origin)


def set_sample_center(sampleid):
    yield from set_sample(sampleid, origin="center")


def set_sample_edge(sampleid):
    yield from set_sample(sampleid, origin='edge')


def sample_move(x, y, r, sampleid=None, **kwargs):
    if sampleid is not None:
        yield from set_sample(sampleid, **kwargs)
    yield from mv(samplex, x, sampley, y, sampler, r)
