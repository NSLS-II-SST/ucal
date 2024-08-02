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
from nbs_gui.widgets.views import AutoControl
from ..widgets.tesSetup import TESSetup


class TESTabWidget(QWidget):
    name = "TES Control Tab"

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_engine = model.run_engine
        self.user_status = model.user_status
        self.beamline = model.beamline

        vbox = QVBoxLayout()
        tes = self.beamline.misc["tes"]
        print("Got TES model")
        print("Adding TES Autocontrol")
        vbox.addWidget(AutoControl(tes, model))
        print("Adding TES Setup")
        vbox.addWidget(TESSetup(model.run_engine))
        vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(vbox)
