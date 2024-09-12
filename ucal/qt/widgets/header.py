from qtpy.QtWidgets import QWidget, QHBoxLayout, QLabel
from nbs_gui.widgets.header import Header

# Use GLOBAL_USER_MD


class ProposalData(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("Proposal: N/A")
        layout.addWidget(self.label)

    def update_proposal(self, proposal_id):
        self.label.setText(f"Proposal: {proposal_id}")


class UCALHeader(Header):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create the ProposalData widget
        self.proposal_data = ProposalData()

        # Insert the ProposalData widget into the second to last position
        self.layout().insertWidget(self.layout().count() - 1, self.proposal_data)
