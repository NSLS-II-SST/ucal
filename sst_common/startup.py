#import nslsii

from bluesky import RunEngine
from databroker import Broker
from sst_common.api import *

RE = RunEngine({})
db = Broker.named('temp')
RE.subscribe(db.insert)

