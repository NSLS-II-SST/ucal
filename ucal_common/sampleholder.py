from sst_base.sampleholder import (SampleHolder, make_regular_polygon,
                                   make_1d_bar)
from ucal_common.motors import manipulator, multimesh

sampleholder = SampleHolder(manipulator=manipulator, name="Sample Holder")

multimesh_holder = SampleHolder(manipulator=multimesh,
                                geometry=make_1d_bar(150),
                                name="multimesh")

refsamples = [[1, "HOPG", 28.2, 1, 0, "C Reference"],
              [2, "CaF2", 38.1, 1, 0, "Ca/F Reference"],
              [3, "TiN", 56.2, 1, 0, "N/Ti Reference"],
              [4, "V", 75.0, 1, 0, "V Reference"],
              [5, "Mn", 93.9, 1, 0, "Mn Reference"],
              [6, "CrFeCoNi", 112.9, 1, 0, "Cr/Fe/Co/Ni Reference"]]
for s in refsamples:
    multimesh_holder.add_sample(*s)

"""
geometry = make_two_sided_bar(10, 60, 1)
refholder.add_geometry(geometry)

"""
