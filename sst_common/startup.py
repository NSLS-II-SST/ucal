# import nslsii does a bunch of setup I don't actually want yet

from sst_common.api import *
from sst_base.commands import generic_cmd
from bluesky import RunEngine
from databroker import Broker

RE = RunEngine({})
db = Broker.named('temp')
RE.subscribe(db.insert)
RE.register_command("calibrate", generic_cmd)
