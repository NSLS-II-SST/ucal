# import nslsii does a bunch of setup I don't actually want yet
# startup sequence for beamline

from bluesky import RunEngine
from sst_common.run_engine import setup_run_engine
from databroker import Broker

RE = RunEngine({}, call_returns_result=True)
RE = setup_run_engine(RE)


db = Broker.named('temp')
RE.subscribe(db.insert)
