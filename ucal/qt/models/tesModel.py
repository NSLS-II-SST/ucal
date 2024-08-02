from qtpy.QtCore import QObject, QTimer, Signal
from nbs_gui.models import BaseModel, formatFloat, formatInt, PVModelRO, EnumModel
from ucal.qt.widgets.signalTuple import SignalTupleMonitor
from ucal.qt.widgets.tesSetup import TESControl


class PVModelNoSub(BaseModel):
    valueChanged = Signal(str)

    def __init__(self, name, obj, group, long_name, update_time=5000, **kwargs):
        super().__init__(name, obj, group, long_name, **kwargs)
        if hasattr(obj, "metadata"):
            self.units = obj.metadata.get("units", None)
            print(f"{name} has units {self.units}")
        else:
            self.units = None
            print(f"{name} has no metadata")

        self.update_time = update_time
        self.value_type = None
        self._value = "Disconnected"
        self._check_value()

    def _check_value(self):
        try:
            value = self.obj.get(connection_timeout=0.2, timeout=0.2)
            self._value_changed(value)
            QTimer.singleShot(self.update_time, self._check_value)
        except:
            QTimer.singleShot(self.update_time, self._check_value)

    def _value_changed(self, value, **kwargs):
        if self.value_type is None:
            if isinstance(value, float):
                self.value_type = float
            elif isinstance(value, int):
                self.value_type = int
            elif isinstance(value, str):
                self.value_type = str
            else:
                self.value_type = type(value)
        try:
            if self.value_type is float:
                value = formatFloat(value)
            elif self.value_type is int:
                value = formatInt(value)
            else:
                value = str(value)
        except ValueError:
            self.value_type = None
            return
        self._value = value
        self.valueChanged.emit(value)

    @property
    def value(self):
        return self._value


class TESModel(QObject):
    default_monitor = SignalTupleMonitor
    default_controller = TESControl

    def __init__(self, name, obj, group, label, **kwargs):
        super().__init__()
        self.name = name
        self.obj = obj
        self.group = group
        self.label = label
        for key, value in kwargs.items():
            setattr(self, key, value)

        connected = PVModelRO(obj.connected.name, obj.connected, group, "TES Connected")
        currentFile = PVModelRO(
            obj.filename.name, obj.filename, group, "Current Filename"
        )
        noiseUID = PVModelRO(
            obj.noise_uid.name, obj.noise_uid, group, "UID For Noise Data"
        )
        projUID = PVModelRO(
            obj.projector_uid.name, obj.projector_uid, group, "UID For Projector Data"
        )
        state = PVModelRO(obj.state.name, obj.state, group, "TES State")
        counts = PVModelRO(obj.mca.counts.name, obj.mca.counts, group, "TES Counts")
        rsyncScan = EnumModel(
            obj.rsync_on_scan_end.name,
            obj.rsync_on_scan_end,
            group,
            "Copy TES Files on Scan End",
        )
        writeOff = EnumModel(
            obj.write_off.name,
            obj.write_off,
            group,
            "Write Off",
        )
        writeLjh = EnumModel(
            obj.write_ljh.name,
            obj.write_ljh,
            group,
            "Write LJH",
        )
        self.signals = [
            connected,
            state,
            currentFile,
            noiseUID,
            projUID,
            rsyncScan,
            counts,
            writeOff,
            writeLjh,
        ]
