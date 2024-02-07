from sst_funcs.configuration import loadConfigDB, instantiateGroup, findAndLoadDevice
from .settings import GLOBAL_SETTINGS

loadConfigDB(GLOBAL_SETTINGS['object_config'])
