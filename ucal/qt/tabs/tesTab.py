from nbs_gui.widgets.utils import HLine
from qtpy.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from qtpy.QtCore import Signal, Slot
from bluesky_queueserver_api import BPlan
from nbs_gui.views.views import AutoControl
from ..widgets.tesSetup import TESSetup, TESProcessing


class TESTabWidget(QWidget):
    name = "TES Control Tab"

    def __init__(self, model, *args, **kwargs):
        print("Very beginning of TES Tab widget")
        super().__init__(*args, **kwargs)
        self.run_engine = model.run_engine
        self.user_status = model.user_status
        self.beamline = model.beamline
        print("Prior to QVBoxLayout")
        vbox = QVBoxLayout()
        print("Getting TES Object")
        print(self.beamline)
        tes = self.beamline.devices.get("tes", None)
        print("Got TES Object")
        if tes is not None:
            print("Got TES model")
        else:
            raise ValueError("TES Object is None")
        print("Adding TES Autocontrol")
        vbox.addWidget(AutoControl(tes, model))
        print("Adding TES Setup")
        vbox.addWidget(TESSetup(tes, model))
        print("Adding TES Processing")
        vbox.addWidget(TESProcessing(model))
        vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(vbox)
