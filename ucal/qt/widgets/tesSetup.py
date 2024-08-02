from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

from qtpy.QtWidgets import QLabel, QWidget
from qtpy.QtCore import Signal, Slot
from bluesky_queueserver_api import BPlan
from nbs_gui.widgets.views import AutoMonitor, AutoControl


class TESControl(QWidget):
    def __init__(self, model, parent_model, orientation="h"):
        super().__init__()
        self.model = model
        vbox = QVBoxLayout()
        vbox.addWidget(AutoMonitor(model, parent_model, orientation=orientation))
        self.stopButton = QPushButton("Stop File")
        self.startButton = QPushButton("Start File")

        self.stopButton.clicked.connect(self.close_file)
        self.startButton.clicked.connect(self.open_file)

        hbox = QHBoxLayout()
        hbox.addWidget(self.stopButton)
        hbox.addWidget(self.startButton)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def open_file(self):
        try:
            self.model.obj._file_start()
        except:
            pass

    def close_file(self):
        try:
            self.model.obj._file_end()
        except:
            pass


class TESSetup(QGroupBox):
    signal_update_widget = Signal(bool, object)

    def __init__(self, run_engine_model, *args, **kwargs):
        super().__init__("TES Setup", *args, **kwargs)
        self.run_engine = run_engine_model
        self.run_engine.events.status_changed.connect(self.on_update_widgets)
        self.signal_update_widget.connect(self.slot_update_widgets)

        hbox = QHBoxLayout()
        step1 = QVBoxLayout()
        step2 = QVBoxLayout()
        step3 = QVBoxLayout()

        self.step1Button = QPushButton("Take Noise")
        self.step2Button = QPushButton("Take Projectors")
        self.step3Button = QPushButton("Make and Send Projectors")

        self.step1Button.clicked.connect(self.take_noise)
        self.step2Button.clicked.connect(self.take_projectors)
        self.step3Button.clicked.connect(self.make_projectors)

        step1.addWidget(QLabel("Take TES Noise Data\nMust close Beam Shutter first"))
        step1.addWidget(self.step1Button)

        step2.addWidget(
            QLabel("Take TES Projector Data\nMust have X-rays being observed with TES")
        )
        step2.addWidget(self.step2Button)

        step3.addWidget(
            QLabel("After TES Noise and TES Projectors have been made, push this")
        )
        step3.addWidget(self.step3Button)

        hbox.addLayout(step1)
        hbox.addLayout(step2)
        hbox.addLayout(step3)

        self.setLayout(hbox)

    def take_noise(self):
        item = BPlan("tes_take_noise")
        msg = "To take TES Noise data, close the beam shutter and ensure that no x-rays are hitting the TES. Then hit yes"
        self.confirm_item_execution(msg, item)

    def take_projectors(self):
        msg = "To take TES Projector data, open the beam shutter and ensure that x-rays are hitting the TES. The count rate should be at least 1000 cps. Then hit yes"
        item = BPlan("tes_take_projectors")
        self.confirm_item_execution(msg, item)

    def make_projectors(self):
        item = BPlan("tes_make_and_load_projectors")
        msg = "Make and set projectors after Noise and Pulses have been taken. Will take about 2 minutes, and the GUI may freeze during this time."
        self.confirm_item_execution(msg, item)

    def confirm_item_execution(self, message, item):
        """
        Show the confirmation dialog with the proper message in case
        ```showConfirmMessage``` is True.

        Returns
        -------
        bool
            True if the message was confirmed or if ```showCofirmMessage```
            is False.
        """

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)

        msg.setText(message)

        # Force "Yes" button to be on the right (as on macOS) to follow common design practice
        msg.setStyleSheet("button-layout: 1")  # MacLayout

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        ret = msg.exec_()
        if ret == QMessageBox.No:
            return False
        else:
            self.run_engine._client.item_execute(item)
            return True

    def on_update_widgets(self, event):
        is_connected = bool(event.is_connected)
        status = event.status
        self.signal_update_widget.emit(is_connected, status)

    @Slot(bool, object)
    def slot_update_widgets(self, is_connected, status):
        # 'is_connected' takes values True, False
        worker_exists = status.get("worker_environment_exists", False)
        running_item_uid = status.get("running_item_uid", None)
        enable = worker_exists and not bool(running_item_uid) and is_connected
        self.step1Button.setEnabled(enable)
        self.step2Button.setEnabled(enable)
        self.step3Button.setEnabled(enable)
