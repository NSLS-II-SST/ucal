from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal, Qt
from bluesky_queueserver_api import BPlan
from nbs_gui.plans.base import PlanWidget

class ManualSampleWidget(PlanWidget):
    def __init__(self, model, parent=None):
        super().__init__(
            model,
            parent,
            x=float,
            y=float,
            z=float,
            r=float,
            name=str,
            sample_id=str)
        self.display_name = "Manual Sample Move"
        
    def submit_plan(self):
        plan = "manual_sample_move"
        params = self.get_params()
        item = BPlan(plan, **params)
        self.run_engine_client.queue_item_add(item=item)
