from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QSizePolicy,
)
from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal, Qt
from bluesky_queueserver_api import BPlan
from nbs_gui.plans.base import AutoPlanWidget
from nbs_gui.plans.nbsPlan import NBSPlanWidget
from nbs_gui.plans.scanPlan import ScanPlanWidget
from nbs_gui.plans.sampleModifier import SampleSelectWidget


class TESCountWidget(AutoPlanWidget):
    display_name = "TES Count"

    def __init__(self, model, parent=None):
        print("Initializing TES Count")
        super().__init__(
            model,
            parent,
            {"Count": "tes_count", "XES": "tes_xes"},
            num=int,
            energy=float,
            repeat=int,
            eslit=("Exit Slit", float),
            dwell=float,
            r=("Sample Angle", float),
            group_name=("Group Name", str),
            comment=str,
        )

    def setup_widget(self):
        super().setup_widget()
        self.sample_widget = SampleSelectWidget(self.model, self)
        self.sample_widget.editingFinished.connect(self.check_plan_ready)
        self.basePlanLayout.addWidget(self.sample_widget)

    def check_plan_ready(self):
        """
        Check if all selections have been made and emit the plan_ready signal if they have.
        """
        print("Checking XAS Plan")
        if self.sample_widget.check_ready():
            print("XAS Ready to Submit")
            self.plan_ready.emit(True)
        else:
            print("XAS not ready")
            self.plan_ready.emit(False)

    def create_plan_items(self):
        plan = self.current_plan
        samples = self.sample_widget.get_value()
        params = self.get_params()
        items = []
        for s in samples:
            item = BPlan(plan, **s, **params)
            items.append(item)
        return items


class TESCalibrateWidget(NBSPlanWidget):
    display_name = "TES Calibrate"

    def __init__(self, model, parent=None):
        print("Initializing TES Calibrate")
        super().__init__(
            model,
            parent,
            "tes_calibrate",
            time=float,
            energy=float,
            eslit=("Exit Slit", float),
            dwell={
                "type": "spinbox",
                "args": {"minimum": 0.1, "value_type": float, "default": 10},
                "label": "Dwell Time per Step (s)",
            },
            beamline_setup=False,
        )

    def _check_ready(self):
        """
        Check if all required parameters are present.

        Returns
        -------
        bool
            True if all required parameters are present, False otherwise
        """
        params = self.get_params()
        return (
            self.sample_select.check_ready() and "time" in params and "energy" in params
        )

    def check_plan_ready(self):
        """
        Check if all selections have been made and emit the plan_ready signal if they have.
        """
        self.plan_ready.emit(self._check_ready())

    def create_plan_items(self):
        params = self.get_params()
        samples = params.pop("samples", [{}])
        time = params.pop("time")
        items = []
        for s in samples:
            item = BPlan(self.current_plan, time, **s, **params)
            items.append(item)
        return items


class TESScanWidget(ScanPlanWidget):
    display_name = "TES Scans"

    def __init__(self, model, parent=None):
        print("Initializing TES Scan Widget")

        super().__init__(
            model,
            parent,
            {
                "Scan": "tes_scan",
                "Relative Scan": "tes_rel_scan",
            },
        )
