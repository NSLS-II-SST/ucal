from sst_base.sampleholder import SampleHolder, make_1d_bar
from ucal_common.motors import manipulator, multimesh

sampleholder = SampleHolder(manipulator=manipulator, name="ucal_sampleholder")
sampleholder.sample.sample_name.name = "sample_name"
sampleholder.sample.sample_id.name = "sample_id"
sampleholder.sample.sample_desc.name = "sample_desc"

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

# Need to then have a dictionary that maps edges to refsample IDs (which aims to be complete?)
