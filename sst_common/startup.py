#import nslsii

from bluesky import RunEngine
from databroker import Broker
from sst_common.api import *
from sst_base.commands import generic_cmd

RE = RunEngine({})
db = Broker.named('temp')
RE.subscribe(db.insert)
RE.register_command("calibrate", generic_cmd)
