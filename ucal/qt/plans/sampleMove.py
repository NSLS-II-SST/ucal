from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal, Qt
from bluesky_queueserver_api import BPlan
from nbs_gui.plans.base import BasicPlanWidget


class ManualSampleWidget(BasicPlanWidget):
    def __init__(self, model, parent=None):
        self.display_name = "Manual Sample Move"
        super().__init__(
            model, parent, x=float, y=float, z=float, r=float, name=str, sample_id=str
        )

    def create_plan_items(self):
        plan = "manual_sample_move"
        params = self.get_params()
        item = BPlan(plan, **params)
        return [item]
