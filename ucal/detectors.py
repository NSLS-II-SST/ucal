from sst_funcs.detectors import add_detector
from .instantiation import findAndLoadDevice


sc = findAndLoadDevice("sc")
i0 = findAndLoadDevice("i0")
ref = findAndLoadDevice("ref")
i0mir = findAndLoadDevice("i0mir")
tes = findAndLoadDevice("tes")

thresholds = {sc.name: .1, i0mir.name: 2e-11, ref.name: .1, i0.name: .1}

#add_detector(ucal_i400, "Small electric signals on ucal")
#add_detector(dm7_i400, "Large electric signals on ucal")
add_detector(sc, "Drain Current", plot=True)
add_detector(i0, "I0 mesh")
add_detector(ref, "multimesh")
add_detector(tes, "Transition-edge Sensor", plot=True)
#add_detector(tes_mca, "TES MCA Channels")
