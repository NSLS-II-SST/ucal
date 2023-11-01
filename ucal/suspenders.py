
from .signals import ring_current
from .shutters import psh4, psh1, psh10, psh7
from bluesky.suspenders import SuspendBoolHigh, SuspendFloor, SuspendCeil, SuspendBoolLow, SuspendWhenChanged

suspend_current = SuspendFloor(
    ring_current,
    resume_thresh=350,
    suspend_thresh=250,
    sleep=30,
    tripped_message="Beam Current is below threshold, will resume when above 350 mA",
    #pre_plan=beamdown_notice,
    #post_plan=beamup_notice,
)

suspend_shutter1 = SuspendBoolHigh(
    psh1.state,
    sleep=30,
    tripped_message="Front End Shutter Closed, waiting for it to open",
    #pre_plan=beamdown_notice,
    #post_plan=beamup_notice,
)

suspend_shutter4 = SuspendBoolHigh(
    psh4.state,
    sleep=30,
    tripped_message="Hutch Shutter Closed, waiting for it to open",
)

suspend_shutter7 = SuspendBoolHigh(
    psh7.state,
    sleep=30,
    tripped_message="Shutter 7 Closed, waiting for it to open",
)

suspend_shutter10 = SuspendBoolHigh(
    psh10.state,
    sleep=30,
    tripped_message="Shutter 10 Closed, waiting for it to open",
)


def turn_on_checks(engine):
    engine.install_suspender(suspend_current)
    engine.install_suspender(suspend_shutter1)
    engine.install_suspender(suspend_shutter4)
    engine.install_suspender(suspend_shutter7)
    engine.install_suspender(suspend_shutter10)

def turn_off_checks(engine):
    engine.remove_suspender(suspend_current)
    engine.remove_suspender(suspend_shutter1)
    engine.remove_suspender(suspend_shutter4)
    engine.remove_suspender(suspend_shutter7)
    engine.remove_suspender(suspend_shutter10)
