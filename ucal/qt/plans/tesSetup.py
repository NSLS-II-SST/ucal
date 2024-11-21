from qtpy.QtWidgets import QWidget
from nbs_gui.plans.base import MultiPlanWidget, AutoPlanWidget, PlanWidgetBase
from bluesky_queueserver_api import BPlan
from .tesBasic import TESCalibrateWidget


class TESShutoffWidget(AutoPlanWidget):
    """Widget for TES shutoff plan"""

    display_name = "TES Shutoff"

    def __init__(self, model, parent=None):
        super().__init__(
            model,
            parent,
            "tes_shutoff",
            should_close_shutter={
                "label": "Should Close Shutter",
                "type": bool,
                "default": False,
            },
        )

    def create_plan_items(self):
        """
        Create plan item for TES shutoff.

        Returns
        -------
        list
            List containing single BPlan for TES shutoff
        """
        params = self.get_params()
        return [
            BPlan("tes_shutoff", should_close_shutter=params["should_close_shutter"])
        ]


class TESCycleCryostatWidget(AutoPlanWidget):
    """Widget for TES cryostat cycling plan"""

    display_name = "TES Cycle Cryostat"

    def __init__(self, model, parent=None):
        super().__init__(
            model,
            parent,
            "tes_cycle_cryostat",
            wait={"label": "Wait for Completion", "type": bool, "default": True},
            should_close_shutter={
                "label": "Should Close Shutter",
                "type": bool,
                "default": True,
            },
        )

    def create_plan_items(self):
        """
        Create plan item for TES cryostat cycling.

        Returns
        -------
        list
            List containing single BPlan for TES cryostat cycling
        """
        params = self.get_params()
        return [
            BPlan(
                "tes_cycle_cryostat",
                wait=params["wait"],
                should_close_shutter=params["should_close_shutter"],
            )
        ]


class TESWaitForCycleWidget(PlanWidgetBase):
    """Widget for waiting for TES cycle completion"""

    display_name = "Wait for TES Cycle"

    def create_plan_items(self):
        """
        Create plan item for waiting for TES cycle completion.

        Returns
        -------
        list
            List containing single BPlan for waiting for TES cycle
        """
        return [BPlan("tes_wait_for_cycle")]

    def _check_ready(self):
        return True


class TESSetupWidget(MultiPlanWidget):
    """
    Widget for TES setup operations combining multiple TES-related plan widgets.

    Parameters
    ----------
    model : object
        The model object containing run_engine and user_status
    parent : QWidget, optional
        Parent widget
    """

    display_name = "TES Setup"

    def __init__(self, model, parent=None):
        # Create individual plan widgets
        shutoff_widget = TESShutoffWidget(model)
        cycle_widget = TESCycleCryostatWidget(model)
        wait_widget = TESWaitForCycleWidget(model)
        calibrate_widget = TESCalibrateWidget(model)

        # Initialize MultiPlanWidget with the created widgets
        super().__init__(
            model,
            parent,
            plan_widgets=[
                shutoff_widget,
                cycle_widget,
                wait_widget,
                calibrate_widget,
            ],
        )
