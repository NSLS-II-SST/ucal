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
from nbs_gui.plans.base import PlanWidget
from nbs_gui.plans.scanPlan import ScanPlanWidget
from nbs_gui.plans.sampleModifier import SampleSelectWidget

class TESCountWidget(PlanWidget):
    def __init__(self, model, parent=None):
        super().__init__(
            model,
            parent,
            num=int,
            energy=float,
            repeat=int,
            eslit=("Exit Slit", float),
            dwell=float,
            r=("Sample Angle", float),
            group_name=("Group Name", str),
            comment=str,
        )
        self.display_name = "TES Count"
        self.plans = QComboBox(self)
        self.plans.addItems(["tes_count", "tes_xes"])
        self.sample_widget = SampleSelectWidget(model, self)
        self.sample_widget.is_ready.connect(self.check_plan_ready)
        self.basePlanLayout.addWidget(self.plans)
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

    def submit_plan(self):
        plan = self.plans.currentText()
        samples = self.sample_widget.get_samples()
        params = self.get_params()
        for s in samples:
            item = BPlan(plan, sample=s, **params)
            self.run_engine_client.queue_item_add(item=item)

class TESCalibrateWidget(PlanWidget):
    def __init__(self, model, parent=None):
        super().__init__(
            model,
            parent,
            time=float,
            energy=float,
            repeat=int,
            eslit=("Exit Slit", float),
            dwell=float,
            r=("Sample Angle", float)
            group_name=("Group Name", str),
            comment=str,
        )
        self.display_name = "TES Calibrate"
        self.sample_widget = SampleSelectWidget(model, self)
        self.sample_widget.is_ready.connect(self.check_plan_ready)
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

    def submit_plan(self):
        plan = "tes_calibrate"
        samples = self.sample_widget.get_samples()
        params = self.get_params()
        time = params.pop('time')
        for s in samples:
            item = BPlan(plan, time, sample=s, **params)
            self.run_engine_client.queue_item_add(item=item)

class TESScanWidget(ScanPlanWidget):
    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        self.display_name = "TES Scans"
        self.plans = QComboBox(self)
        self.plans.addItems(["tes_scan", "tes_rel_scan", "tes_list_scan"])
        self.basePlanLayout.insertWidget(0, self.plans)

    def submit_plan(self):
        plan = self.plans.currentText()
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        params = self.get_params()
        # start = float(self.modifier_input_from.text())
        # end = float(self.modifier_input_to.text())
        # steps = int(self.modifier_input_steps.text())
        item = BPlan(
            plan,
            motor,
            params["start"],
            params["end"],
            params["steps"],
            dwell=params.get("dwell", None),
            comment=params.get("comment", None),
        )
        self.run_engine_client.queue_item_add(item=item)
