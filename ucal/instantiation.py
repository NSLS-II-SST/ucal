from sst_funcs.configuration import loadConfigDB, instantiateGroup, findAndLoadDevice
from os.path import join, dirname

loadConfigDB(join(dirname(__file__), "object_config.yaml"))
#loadConfigDB(join(dirname(__file__), "sim_config.yaml"))
