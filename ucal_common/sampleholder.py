from sst_base.sampleholder import SampleHolder
from ucal_common.motors import manipulator

sampleholder = SampleHolder(manipulator=manipulator, name="ucal_sampleholder")
sampleholder.sample.sample_name.name = "sample_name"
sampleholder.sample.sample_id.name = "sample_id"
sampleholder.sample.sample_desc.name = "sample_desc"
"""
geometry = make_two_sided_bar(10, 60, 1)
refholder.add_geometry(geometry)

"""
