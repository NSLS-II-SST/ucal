# Abstracted Dastard/TES setup
tes.rpc.set_pulse_triggers()
tes.rpc.set_projectors()
tes._file_start()
tes.rpc.calibration_load_from_disk()
# Wait for some pulses

# Set some ROIs
tes.set_roi( "ckalpha", 250, 300) 
tes.set_roi( "okalpha", 500, 550) 
tes.set_roi(   "felab", 690, 740) 
tes.set_roi(   "nilab", 840, 890) 
tes.set_roi(   "culab", 915, 965) 

# Get some ROIs
tes.acquire_time.set(5)
RE(scan([tes], en, 1000, 500, 51))
