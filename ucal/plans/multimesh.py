from bluesky.plan_stubs import abs_set
from sst_base.sampleholder import SampleHolder, make_1d_bar
from ucal.motors import multimesh

multimesh_holder = SampleHolder(manipulator=multimesh,
                                geometry=make_1d_bar(150),
                                name="multimesh")

refsamples = [[1, "HOPG", (28.0, 28.4), 1, "C Reference"],
              [2, "CaF2", (37.9, 38.3), 1, "Ca/F Reference"],
              [3, "TiN", (56.0, 56.4), 1, "N/Ti Reference"],
              [4, "V", (74.8, 75.2), 1, "V Reference"],
              [5, "Mn", (93.7, 94.1), 1, "Mn Reference"],
              [6, "CrFeCoNi", (112.7, 113.1), 1, "Cr/Fe/Co/Ni Reference"]]

refelements = {"C": 1, "Ca": 2, "F": 2, "N": 3, "Ti": 3, "O": 4, "V": 4,
               "Mn": 5, "Cr": 6, "Fe": 6, "Co": 6, "Ni": 6}

for s in refsamples:
    multimesh_holder.add_sample(*s)


def set_multimesh(element):
    sampleid = refelements.get(element)
    yield from abs_set(multimesh_holder, sampleid, origin="center")
