from bluesky.plan_stubs import abs_set
from sst_base.sampleholder import SampleHolder, make_1d_bar
from ucal.motors import multimesh

refholder = SampleHolder(manipulator=multimesh, name="i0up_multimesh")
geometry = make_1d_bar(160)
refholder.add_geometry(geometry)
refsamples = [('0', "C", (16, 20), 0),
              ('1', "HOPG", (26.2, 30.2), 0),
              ('2', "CaF2", (36.1, 40.1), 0),
              ('3', "TiN", (54.2, 58.2), 0),
              ('4', "V", (73.0, 77.0), 0),
              ('5', "Mn", (91.9, 95.9), 0),
              ('6', "CrFeCoNi", (110.9, 114.9), 0),
              ('7', "Blank", (131.5, 135.5), 0),
              ('8', "Photodiode", (149.0, 153.0), 0)]

for s in refsamples:
    refholder.add_sample(*s)

ref_dict = {"c": 0, "n": 3, "o": 4, "f": 2, "ca": 2,
            "ti": 3, "v": 4, "cr": 6, "mn": 5, "fe": 6,
            "co": 6, "ni": 6, "photodiode": 8, "empty": 7, "blank": 7}

def set_ref(refid):
    """
    Moves multimesh to a selected sample id

    refid : sampleid for refholder
    """
    yield from abs_set(refholder, refid, origin="center")
    yield from abs_set(multimesh, 0)
    
def set_edge(edge):
    """
    Moves multimesh to a sample that is appropriate for the requested
    x-ray edge

    edge : Element edge from ref_dict (c, n, o, etc)
    if not found, defaults to CrFeCoNi sample
    """
    refid = ref_dict.get(edge.lower(), 6)
    yield from set_ref(refid)
    
