# Abstracted Dastard/TES setup
tes.rpc.set_pulse_triggers()
tes.rpc.set_projectors()
tes._file_start()
tes._calibration_start()
# Wait for some pulses
tes.rpc.scan_end(_try_post_processing=False)
tes.rpc.calibration_learn_from_last_data()

# Set some ROIs
tes.rpc.roi_set({"ckalpha": (250, 300), "okalpha": (500, 550), "felab": (690, 740), "nilab":(840, 890), "culab":(915, 965)}

# Get some ROIs

tes.rpc.scan_start("motor", "index", tes.scan_num.get(), 1, "sample")
tes.rpc.scan_point_start(1)
tes.rpc.scan_point_end()
tes.rpc.roi_get_counts()
tes.rpc.scan_end()
