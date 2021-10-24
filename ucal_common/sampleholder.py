from bl_base.sampleholder import SampleHolder

sampleholder = SampleHolder(name="Sample Holder")
refholder = SampleHolder(name="Energy Reference")
refholder.load_geometry(10, 60, 1)

refsamples = [[1, "HOPG", 28.2, 1, 0, "C Reference"],
              [2, "CaF2", 38.1, 1, 0, "Ca/F Reference"],
              [3, "TiN", 56.2, 1, 0, "N/Ti Reference"],
              [4, "V", 75.0, 1, 0, "V Reference"],
              [5, "Mn", 93.9, 1, 0, "Mn Reference"],
              [6, "CrFeCoNi", 112.9, 1, 0, "Cr/Fe/Co/Ni Reference"]]
for s in refsamples:
    refholder.add_sample(*s)
