from qtpy.QtWidgets import (
    QTableView,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QHBoxLayout,
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
)
from qtpy.QtCore import QAbstractTableModel, Qt, Signal, Slot
from nbs_gui.plans.base import PlanWidget
from nbs_gui.tabs.sampleTab import QtSampleView
from bluesky_queueserver_api import BFunc
import ast
import csv


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
        dialog = AddSampleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            sample_info = dialog.get_sample_info()
            print(f"Adding sample: {sample_info}")

            # Create a BFunc to call the add_sample function in queueserver
            plan = BFunc(
                "add_sample",
                sample_info["id"],
                sample_info["name"],
                sample_info["coordinates"],
                sample_info["side"],
                sample_info["thickness"],
                sample_info["description"],
            )

            try:
                self.run_engine._client.function_execute(plan)
                print("Sample added successfully")
            except Exception as e:
                print(f"Error adding sample: {e}")

    def clear_all_samples(self):
        func = BFunc("clear_samples")
        try:
            self.run_engine._client.function_execute(func)
            print("Sample added successfully")
        except Exception as e:
            print(f"Error adding sample: {e}")  # Stub method for clearing all samples

    def save_to_file(self):
        # Get the file path from the user
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Sample File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            print("Save cancelled")
            return

        # Ensure the file has a .csv extension
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            # Get the data from the sample_view
            sample_data = self.parent().sample_view.tableModel._data

            # Write the data to the CSV file
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write the header
                if sample_data:
                    header = list(sample_data.keys())
                    writer.writerow(header)

                # Write the sample data
                for sample_id, sample_info in sample_data.items():
                    writer.writerow([sample_info.get(key, "") for key in header])

            print(f"Sample data saved to {file_path}")
        except Exception as e:
            print(f"Error saving sample data: {e}")

    def remove_sample(self):
        # Get the QtSampleView
        sample_view = self.parent().sample_view

        # Get the selected row
        selected_indexes = sample_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(
                self, "No Selection", "Please select a sample to remove."
            )
            return

        # Get the row of the first selected cell
        selected_row = selected_indexes[0].row()

        # Get the sample ID from the model
        sample_ids = list(sample_view.tableModel._data.keys())
        if selected_row < len(sample_ids):
            sample_id = sample_ids[selected_row]

            # Create a BFunc to call remove_sample
            func = BFunc("remove_sample", sample_id)

            try:
                # Execute the function
                self.run_engine._client.function_execute(func)
                print(f"Sample {sample_id} removed successfully")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to remove sample: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Invalid Selection",
                "The selected row does not correspond to a valid sample.",
            )


class AddSampleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Sample")
        self.layout = QFormLayout(self)

        # Create input fields
        self.name_input = QLineEdit(self)
        self.id_input = QLineEdit(self)
        self.description_input = QLineEdit(self)
        self.coordinates_input = QLineEdit(self)
        self.side_input = QSpinBox(self)
        self.thickness_input = QDoubleSpinBox(self)
        self.proposal_input = QLineEdit(self)

        # Configure numeric inputs
        self.side_input.setMinimum(1)
        self.side_input.setMaximum(4)
        self.thickness_input.setDecimals(3)
        self.thickness_input.setMinimum(0)
        self.thickness_input.setMaximum(1000)
        self.thickness_input.setSingleStep(0.1)

        # Add input fields to the layout
        self.layout.addRow("Sample Name:", self.name_input)
        self.layout.addRow("Sample ID:", self.id_input)
        self.layout.addRow("Description:", self.description_input)
        self.layout.addRow("Coordinates:", self.coordinates_input)
        self.layout.addRow("Side:", self.side_input)
        self.layout.addRow("Thickness:", self.thickness_input)
        self.layout.addRow("Proposal (optional):", self.proposal_input)

        # Add OK and Cancel buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addRow(self.button_box)

    def get_sample_info(self):
        try:
            coordinates = ast.literal_eval(self.coordinates_input.text())
            if not isinstance(coordinates, (int, float, list)):
                raise ValueError("Coordinates must be a number or a list of numbers")
            if isinstance(coordinates, list) and not all(
                isinstance(x, (int, float)) for x in coordinates
            ):
                raise ValueError("All coordinates must be numbers")
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing coordinates: {e}")
            coordinates = None

        info = {
            "name": self.name_input.text(),
            "id": self.id_input.text(),
            "description": self.description_input.text(),
            "coordinates": coordinates,
            "side": self.side_input.value(),
            "thickness": self.thickness_input.value(),
        }
        prop_id = self.proposal_input.text()
        if prop_id != "":
            info["proposal"] = prop_id
        return info
