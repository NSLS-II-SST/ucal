from sst_base.sampleholder import SampleHolder
from .hw import manipulator

# from ucal.motors import manipulator

sampleholder = SampleHolder(manipulator=manipulator, name="ucal_sampleholder")
sampleholder.sample.sample_name.name = "sample_name"
sampleholder.sample.sample_id.name = "sample_id"
sampleholder.sample.sample_desc.name = "sample_desc"


# Need to then have a dictionary that maps edges to refsample IDs (which aims to be complete?)
