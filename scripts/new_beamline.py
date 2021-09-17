import os
from os.path import join
import sys

config_dir = os.getenv("SST_CONFIG_DIR", None)
if config_dir is None:
    print('You must set the variable "SST_CONFIG_DIR" first')
    sys.exit(0)

home_dir = os.getenv("HOME")
full_dir = join(home_dir, config_dir)
os.mkdir(full_dir)
