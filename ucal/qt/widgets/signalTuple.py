from nbs_gui.widgets.views import AutoMonitorBox

class SignalTupleMonitor(AutoMonitorBox):
    def __init__(self, model, parent_model, orientation="h"):
        super().__init__(model.signals, model.name, parent_model, orientation="h")
