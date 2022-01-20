from sst_base.sampleholder import (SampleHolder, make_regular_polygon,
                                   make_1d_bar)
from ucal_common.motors import manipulator, multimesh

sampleholder = SampleHolder(manipulator=manipulator, name="Sample Holder")

multimesh_holder = SampleHolder(manipulator=multimesh,
                                geometry=make_1d_bar(150),
                                name="multimesh")

refsamples = [[1, "HOPG", (28.0, 28.4), 1, "C Reference"],
              [2, "CaF2", (37.9, 38.3), 1, "Ca/F Reference"],
              [3, "TiN", (56.0, 56.4), 1, "N/Ti Reference"],
              [4, "V", (74.8, 75.2), 1, "V Reference"],
              [5, "Mn", (93.7, 94.1), 1, "Mn Reference"],
              [6, "CrFeCoNi", (112.7, 113.1), 1, "Cr/Fe/Co/Ni Reference"]]
for s in refsamples:
    multimesh_holder.add_sample(*s)

"""
geometry = make_two_sided_bar(10, 60, 1)
refholder.add_geometry(geometry)

"""
