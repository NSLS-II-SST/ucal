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

        if orientation == "v":
            main_layout = QVBoxLayout()
        else:
            main_layout = QHBoxLayout()

        # Status GroupBox
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_layout.addWidget(AutoMonitor(model.status, parent_model))
        status_layout.addWidget(AutoMonitor(model.state, parent_model))
        status_layout.addWidget(AutoMonitor(model.counts, parent_model))
        status_group.setLayout(status_layout)

        # Writing GroupBox
        writing_group = QGroupBox("Writing")
        writing_layout = QVBoxLayout()
        writing_layout.addWidget(AutoMonitor(model.state, parent_model))
        writing_layout.addWidget(AutoMonitor(model.currentFile, parent_model))
        writing_layout.addWidget(AutoMonitor(model.writeLjh, parent_model))
        writing_layout.addWidget(AutoMonitor(model.writeOff, parent_model))
        writing_group.setLayout(writing_layout)

        # Setup GroupBox
        setup_group = QGroupBox("Setup")
        setup_layout = QVBoxLayout()
        setup_layout.addWidget(AutoMonitor(model.noiseUID, parent_model))
        setup_layout.addWidget(AutoMonitor(model.projUID, parent_model))
        setup_layout.addWidget(AutoMonitor(model.calUID, parent_model))
        setup_group.setLayout(setup_layout)

        main_layout.addWidget(status_group)
        main_layout.addWidget(writing_group)
        main_layout.addWidget(setup_group)

        # File control buttons
        button_layout = QHBoxLayout()
        self.stopButton = QPushButton("Stop File")
        self.startButton = QPushButton("Start File")
        self.stopButton.clicked.connect(self.close_file)
        self.startButton.clicked.connect(self.open_file)
        button_layout.addWidget(self.stopButton)
        button_layout.addWidget(self.startButton)

        # Combine layouts
        vbox = QVBoxLayout()
        vbox.addLayout(main_layout)
        vbox.addLayout(button_layout)
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

    def __init__(self, tes, parent_model, *args, **kwargs):
        super().__init__("TES Setup", *args, **kwargs)
        self.tes = tes
        self.run_engine = parent_model.run_engine
        print("Setting up signals")
        self.run_engine.events.status_changed.connect(self.on_update_widgets)
        self.signal_update_widget.connect(self.slot_update_widgets)
        print("Setting up ValueChanged")
        self.tes.status.valueChanged.connect(self.enable_buttons)
        self.globalEnable = False

        print("Setting up layout")
        layout = QVBoxLayout()
        allSetup = QHBoxLayout()
        step1 = QHBoxLayout()
        step2 = QHBoxLayout()
        step3 = QHBoxLayout()

        self.run_all_button = QPushButton("Run Setup")
        self.noise_button = QPushButton("Take Noise")
        self.projector_button = QPushButton("Take Projectors")
        self.projector_load_button = QPushButton("Make and Send Projectors")

        print("Connecting Buttons")
        self.run_all_button.clicked.connect(self.setup_all)
        self.noise_button.clicked.connect(self.take_noise)
        self.projector_button.clicked.connect(self.take_projectors)
        self.projector_load_button.clicked.connect(self.make_projectors)

        print("Adding Widgets")
        allSetup.addWidget(QLabel("Run All Setup Steps in Order"))
        allSetup.addWidget(self.run_all_button)

        step1.addWidget(QLabel("Take TES Noise Data\nMust close Beam Shutter first"))
        step1.addWidget(self.noise_button)

        step2.addWidget(
            QLabel("Take TES Projector Data\nMust have X-rays being observed with TES")
        )
        step2.addWidget(self.projector_button)

        step3.addWidget(
            QLabel("After TES Noise and TES Projectors have been made, push this")
        )
        step3.addWidget(self.projector_load_button)

        layout.addLayout(allSetup)
        layout.addLayout(step1)
        layout.addLayout(step2)
        layout.addLayout(step3)

        self.setLayout(layout)

    def setup_all(self):
        item1 = BPlan("tes_take_noise")
        msg = "TES Noise and Projectors will run. This will take some time, and open/close a beam shutter. Ensure that beam is currently hitting a sample, with a count rate of at least 1000 cps. Then hit yes"
        self.confirm_item_execution(msg, item1)
        item2 = BPlan("tes_take_projectors")
        item3 = BPlan("tes_make_and_load_projectors")

        self.run_engine._client.item_execute(item2)
        self.run_engine._client.item_execute(item3)

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
            try:
                self.run_engine._client.item_execute(item)
            except Exception as e:
                print(f"An error occurred: {str(e)}")
            return True

    def on_update_widgets(self, event):
        is_connected = bool(event.is_connected)
        status = event.status
        self.signal_update_widget.emit(is_connected, status)

    def enable_buttons(self, value=""):
        enable_base = self.globalEnable
        status_index = self.tes.status._index_value
        if status_index == 0:
            enable_base = False
        if status_index < 2:
            enable_projectors = False
        else:
            enable_projectors = True
        if status_index < 3:
            enable_projector_load = False
        else:
            enable_projector_load = True
        self.run_all_button.setEnabled(enable_base)
        self.noise_button.setEnabled(enable_base)
        self.projector_button.setEnabled(enable_base and enable_projectors)
        self.projector_load_button.setEnabled(enable_base and enable_projector_load)

    @Slot(bool, object)
    def slot_update_widgets(self, is_connected, status):
        # 'is_connected' takes values True, False
        worker_exists = status.get("worker_environment_exists", False)
        running_item_uid = status.get("running_item_uid", None)
        self.globalEnable = (
            worker_exists and not bool(running_item_uid) and is_connected
        )
        self.enable_buttons()
