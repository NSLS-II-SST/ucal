from qtpy.QtWidgets import (
    QTableView,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QHBoxLayout,
)
from qtpy.QtCore import QAbstractTableModel, Qt, Signal, Slot
from nbs_gui.plans.base import PlanWidget
from nbs_gui.tabs.sampleTab import QtSampleView
from bluesky_queueserver_api import BFunc


class SampleTab(QWidget):
    name = "Samples"

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.model = model

        self.sample_view = QtSampleView(model.user_status, parent=self)
        self.new_sample = SampleWidget(model, parent)
        self.layout.addWidget(self.new_sample)
        self.layout.addWidget(self.sample_view)


class SampleWidget(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.run_engine = model.run_engine
        self.beamline = model.beamline

        layout = QHBoxLayout(self)

        # Create buttons
        self.load_file_button = QPushButton("Load Sample File")
        self.add_sample_button = QPushButton("Add Sample")
        self.clear_samples_button = QPushButton("Clear All Samples")
        self.save_file_button = QPushButton("Save to File")
        self.remove_sample_button = QPushButton("Remove Sample")

        # Add buttons to layout
        layout.addWidget(self.load_file_button)
        layout.addWidget(self.add_sample_button)
        layout.addWidget(self.clear_samples_button)
        layout.addWidget(self.save_file_button)
        layout.addWidget(self.remove_sample_button)

        # Connect buttons to stub methods
        self.load_file_button.clicked.connect(self.load_sample_file)
        self.add_sample_button.clicked.connect(self.add_sample)
        self.clear_samples_button.clicked.connect(self.clear_all_samples)
        self.save_file_button.clicked.connect(self.save_to_file)
        self.remove_sample_button.clicked.connect(self.remove_sample)

    def load_sample_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Sample File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.sample_file_path = file_path
            print(f"Sample file loaded: {self.sample_file_path}")
        else:
            print("No file selected")
            return
        plan = BFunc("load_standard_four_sided_bar", self.sample_file_path)
        try:
            self.run_engine._client.function_execute(plan)
        except Exception as e:
            print(e)

    def add_sample(self):
        # Stub method for adding a sample
        print("Add sample method called")

    def clear_all_samples(self):
        # Stub method for clearing all samples
        print("Clear all samples method called")

    def save_to_file(self):
        # Stub method for saving to file
        print("Save to file method called")

    def remove_sample(self):
        # Stub method for removing a sample
        print("Remove sample method called")
