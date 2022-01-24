from sst_base.sampleholder import SampleHolder
from ucal_common.motors import manipulator

sampleholder = SampleHolder(manipulator=manipulator, name="Sample Holder")

"""
geometry = make_two_sided_bar(10, 60, 1)
refholder.add_geometry(geometry)

"""
