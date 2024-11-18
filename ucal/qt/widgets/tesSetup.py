from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

from qtpy.QtWidgets import QLabel, QWidget
from qtpy.QtCore import Signal, Slot, QFileSystemWatcher
from bluesky_queueserver_api import BPlan, BFunc
from nbs_gui.widgets.views import AutoMonitor, AutoControl
from nbs_gui.settings import SETTINGS
from os.path import join
import pickle
from os.path import exists
import numpy as np


class TESControl(QWidget):
    def __init__(self, model, parent_model, orientation="h"):
        super().__init__()
        self.model = model
        self.run_engine = parent_model.run_engine

        if orientation == "v":
            main_layout = QVBoxLayout()
        else:
            main_layout = QHBoxLayout()

        # Status GroupBox
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_layout.addWidget(AutoMonitor(model.status, parent_model))
        status_layout.addWidget(AutoMonitor(model.state, parent_model))
        status_layout.addWidget(AutoMonitor(model.proj_status, parent_model))
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
        self.activateButton = QPushButton("Activate")
        self.deactivateButton = QPushButton("Deactivate")
        self.startButton.setEnabled(False)  # Need to be connected & RunEngine idle
        self.stopButton.clicked.connect(self.close_file)
        self.startButton.clicked.connect(self.open_file)
        self.activateButton.clicked.connect(self.activate)
        self.deactivateButton.clicked.connect(self.deactivate)
        button_layout.addWidget(self.stopButton)
        button_layout.addWidget(self.startButton)
        button_layout.addWidget(self.activateButton)
        button_layout.addWidget(self.deactivateButton)

        # Combine layouts
        vbox = QVBoxLayout()
        vbox.addLayout(main_layout)
        vbox.addLayout(button_layout)
        self.setLayout(vbox)

    def deactivate(self):
        item = BFunc("deactivate_detector", "tes")
        try:
            self.run_engine._client.function_execute(item)
        except Exception as e:
            QMessageBox.critical(
                self,
                "QueueServer Error",
                f"Failed to deactivate TES: {str(e)}",
                QMessageBox.Ok,
            )
            return False

    def activate(self):
        item = BFunc("activate_detector", "tes")
        try:
            self.run_engine._client.function_execute(item)
        except Exception as e:
            QMessageBox.critical(
                self,
                "QueueServer Error",
                f"Failed to activate TES: {str(e)}",
                QMessageBox.Ok,
            )
            return False

    def open_file(self):
        item = BPlan("tes_start_file")
        try:
            self.run_engine._client.item_execute(item)
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "TES Start Error",
                f"Failed to start TES: {str(e)}",
                QMessageBox.Ok,
            )
            return False

    def close_file(self):
        try:
            self.model.obj._file_end()
        except Exception as e:
            QMessageBox.critical(
                self,
                "TES Stop Error",
                f"Failed to stop TES: {str(e)}",
                QMessageBox.Ok,
            )

    @Slot(bool, object)
    def slot_update_widgets(self, is_connected, status):
        # 'is_connected' takes values True, False
        worker_exists = status.get("worker_environment_exists", False)
        running_item_uid = status.get("running_item_uid", None)
        self.globalEnable = (
            worker_exists and not bool(running_item_uid) and is_connected
        )
        self.enable_buttons()

    def enable_buttons(self, value=""):
        self.startButton.setEnabled(self.globalEnable)
        self.activateButton.setEnabled(self.globalEnable)
        self.deactivateButton.setEnabled(self.globalEnable)


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
        item1 = BPlan("tes_setup")
        msg = "TES Noise and Projectors will run. This will take some time, and open/close a beam shutter. Ensure that beam is currently hitting a sample, with a count rate of at least 1000 cps. Then hit yes"
        self.confirm_item_execution(msg, item1)
        # item2 = BPlan("tes_take_projectors")
        # item3 = BPlan("tes_make_and_load_projectors")

        # self.run_engine._client.item_execute(item2)
        # self.run_engine._client.item_execute(item3)

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
                return True
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "TES Error",
                    f"Failed TES Operation: {str(e)}",
                    QMessageBox.Ok,
                )
                return False

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


class TESProcessing(QGroupBox):
    """
    Widget for displaying TES processing information.

    Parameters
    ----------
    model : object
        TES model object
    *args : tuple
        Additional arguments passed to QGroupBox
    **kwargs : dict
        Additional keyword arguments passed to QGroupBox
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__("TES Processing Status")
        self.model = model

        # Get file paths from settings
        config_path = SETTINGS.beamline_config.get("settings", {}).get(
            "tes_processing", ""
        )
        self.science_file = join(config_path, "data_processing_info.pkl")
        self.cal_file = join(config_path, "data_calibration_info.pkl")

        # Initialize file watcher
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.on_file_changed)

        # Add files to watch if they exist
        for file_path in [self.science_file, self.cal_file]:
            if exists(file_path):
                self.watcher.addPath(file_path)

        # Initialize data dictionaries
        self.science_info = {}
        self.cal_info = {}

        # Create layout
        layout = QVBoxLayout()

        # Create refresh button
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Processing Info")
        self.refresh_button.clicked.connect(self.update)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Create calibration info section
        cal_group = QGroupBox("Calibration Information")
        self.cal_layout = QVBoxLayout()
        self.cal_labels = {}
        cal_group.setLayout(self.cal_layout)

        # Create science info section
        science_group = QGroupBox("Science Run Information")
        self.science_layout = QVBoxLayout()
        self.science_labels = {}
        science_group.setLayout(self.science_layout)

        # Add groups to main layout
        hlayout = QHBoxLayout()
        hlayout.addWidget(cal_group)
        hlayout.addWidget(science_group)
        layout.addLayout(hlayout)
        self.setLayout(layout)

        # Initial update
        self.update()

    def on_file_changed(self, path):
        """Handle file change events."""
        print(f"File changed: {path}")
        # Re-add the file to the watcher as it might be removed after being modified
        if exists(path):
            self.watcher.addPath(path)
        self.update()

    def update(self):
        """Update processing information display from files."""
        # Load calibration info
        if exists(self.cal_file):
            try:
                with open(self.cal_file, "rb") as f:
                    self.cal_info = pickle.load(f)
                # Add file to watcher if not already watching
                if self.cal_file not in self.watcher.files():
                    self.watcher.addPath(self.cal_file)
                self._update_cal_display()
            except Exception as e:
                print(f"Error loading calibration info: {e}")

        # Load science info
        if exists(self.science_file):
            try:
                with open(self.science_file, "rb") as f:
                    self.science_info = pickle.load(f)
                # Add file to watcher if not already watching
                if self.science_file not in self.watcher.files():
                    self.watcher.addPath(self.science_file)
                self._update_science_display()
            except Exception as e:
                print(f"Error loading science info: {e}")

    def _create_info_row(self, label, value):
        """Create a horizontal layout with label and value."""
        row = QHBoxLayout()
        label_widget = QLabel(f"{label}:")
        label_widget.setStyleSheet("font-weight: bold;")
        value_widget = QLabel(str(value))
        row.addWidget(label_widget)
        row.addWidget(value_widget)
        row.addStretch()
        return row

    def _clear_layout(self, layout):
        """Properly clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()
            elif item.widget():
                item.widget().deleteLater()

    def _update_cal_display(self):
        """Update calibration information display."""
        # Clear existing content
        self._clear_layout(self.cal_layout)

        if not self.cal_info:
            self.cal_layout.addLayout(
                self._create_info_row("Status", "No calibration data")
            )
            return

        # Add run information
        run_info = self.cal_info.get("run_info", {})
        self.cal_layout.addLayout(
            self._create_info_row("Scan ID", run_info.get("scan_id", "N/A"))
        )
        self.cal_layout.addLayout(
            self._create_info_row("Sample", run_info.get("sample_name", "N/A"))
        )
        self.cal_layout.addLayout(
            self._create_info_row("Timestamp", run_info.get("timestamp", "N/A"))
        )

        # Add calibration statistics
        self.cal_layout.addLayout(
            self._create_info_row(
                "Calibrated Channels",
                f"{self.cal_info.get('calibrated_channels', 0)}/{self.cal_info.get('total_channels', 0)}",
            )
        )
        median_rms = np.median(list(self.cal_info.get("rms_per_channel", [0]).values()))
        self.cal_layout.addLayout(
            self._create_info_row("Median RMS (should be < 0.2)", f"{median_rms:.3f}")
        )

    def _update_science_display(self):
        """Update science run information display."""
        # Clear existing content
        self._clear_layout(self.science_layout)

        if not self.science_info:
            self.science_layout.addLayout(
                self._create_info_row("Status", "No science data")
            )
            return

        # Add run information
        run_info = self.science_info.get("run_info", {})
        self.science_layout.addLayout(
            self._create_info_row("Scan ID", run_info.get("scan_id", "N/A"))
        )
        self.science_layout.addLayout(
            self._create_info_row("Sample", run_info.get("sample_name", "N/A"))
        )
        self.science_layout.addLayout(
            self._create_info_row("Timestamp", run_info.get("timestamp", "N/A"))
        )

        # Add calibration source information
        cal_source = self.science_info.get("calibration_source", {})
        self.science_layout.addLayout(
            self._create_info_row("Cal. Scan ID", cal_source.get("scan_id", "N/A"))
        )

        # Add processing statistics
        self.science_layout.addLayout(
            self._create_info_row(
                "Processed Channels",
                f"{self.science_info.get('calibrated_channels', 0)}/{self.science_info.get('total_channels', 0)}",
            )
        )
        self.science_layout.addLayout(
            self._create_info_row(
                "Data Saved",
                "Yes" if self.science_info.get("data_saved", False) else "No",
            )
        )
