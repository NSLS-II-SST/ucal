shim_name = "sst_sim"
print(shim_name)
if shim_name == "sst_sim":
    from sst_sim_shims.api import *
else:
    from sst_sim_shims.api import *
    
#Essentially defines the API for shim class
#from shim.api import samplex, sampley, samplez, sampler
#from shim.api import i1, man
