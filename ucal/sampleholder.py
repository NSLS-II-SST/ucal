from sst_base.sampleholder import SampleHolder

# from ucal.motors import manipulator


def SampleHolderFactory(prefix, *, name, beamline):
    manipulator = beamline.devices["manipulator"]
    sampleholder = SampleHolder(manipulator=manipulator, name=name)
    sampleholder.sample.sample_name.name = "sample_name"
    sampleholder.sample.sample_id.name = "sample_id"
    sampleholder.sample.sample_desc.name = "sample_desc"
    return sampleholder


# Need to then have a dictionary that maps edges to refsample IDs (which aims to be complete?)
