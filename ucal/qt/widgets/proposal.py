from nbs_gui.widgets.status import StatusBox
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QFormLayout, QPushButton, QWidget
from redis_json_dict import RedisJSONDict
import redis
import warnings
from ldap3 import Server, Connection, NTLM
from ldap3.core.exceptions import LDAPInvalidCredentialsResult
from nslsii.sync_experiment.sync_experiment import validate_proposal, should_they_be_here, get_current_cycle
from datetime import datetime

class AuthorizationError(Exception): ...


def authenticate(username, password):
    auth_server = Server("dc2.bnl.gov", use_ssl=True)

    try:
        connection = Connection(
            auth_server,
            user=f"BNL\\{username}",
            password=password,
            authentication=NTLM,
            auto_bind=True,
            raise_exceptions=True,
        )
        print(f"\nAuthenticated as : {connection.extend.standard.who_am_i()}")

    except LDAPInvalidCredentialsResult:
        raise RuntimeError(f"Invalid credentials for user '{username}'.") from None


def sync_experiment(proposal_number, username, password):

    redis_client = redis.Redis(host="info.sst.nsls2.bnl.gov")
    beamline = "sst1"
    md = RedisJSONDict(redis_client=redis_client, prefix='nexafs-')

    new_data_session = f"pass-{proposal_number}"

    if (new_data_session == md.get("data_session")) and (
        username == md.get("username")
    ):

        warnings.warn(
            f"Experiment {new_data_session} was already started by the same user."
        )

    else:

        proposal_data = validate_proposal(new_data_session, beamline)
        users = proposal_data.pop("users")

        authenticate(username, password)

        if not should_they_be_here(username, new_data_session, beamline):
            raise AuthorizationError(
                f"User '{username}' is not allowed to take data on proposal {new_data_session}"
            )

        pi_name = ""
        for user in users:
            if user.get("is_pi"):
                pi_name = (
                    f'{user.get("first_name", "")} {user.get("last_name", "")}'.strip()
                )

        md["data_session"] = new_data_session
        md["username"] = username
        md["start_datetime"] = datetime.now().isoformat()
        md["cycle"] = get_current_cycle()
        md["proposal"] = {
            "proposal_id": proposal_data.get("proposal_id"),
            "title": proposal_data.get("title"),
            "type": proposal_data.get("type"),
            "pi_name": pi_name,
        }

        print(f"Started experiment {new_data_session}.")


class ProposalSyncExperiment(QDialog):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        vbox = QVBoxLayout()
        button = QPushButton("Submit")
        button.clicked.connect(self.submit_form)
        
        form = QFormLayout()
        self.username = QLineEdit()
        self.proposal = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Username", self.username)
        form.addRow("Proposal ID", self.proposal)
        form.addRow("Password", self.password)
        vbox.addLayout(form)
        vbox.addWidget(button)
        self.setLayout(vbox)

    def submit_form(self):
        username = self.username.text()
        proposal = self.proposal.text()
        password = self.password.text()

        print(f"Authenticating {username} and {proposal}")
        
        sync_experiment(proposal, username, password)
            
class ProposalBox(StatusBox):
    def __init__(self, user_status, parent=None):
        super().__init__(user_status, "User Metadata", "USER_MD", parent=parent)

    @Slot(object)
    def update_md(self, user_md):
        cleaned_md = {}
        prop_md = user_md.get('proposal', {})
        cleaned_md["Title"] = prop_md.get('title', "")
        cleaned_md["Proposal ID"] = prop_md.get('proposal_id', '')
        cleaned_md["Data Session"] = user_md.get('data_session', '')
        cleaned_md["Type"] = prop_md.get('type', '')
        cleaned_md["PI"] = prop_md.get('pi_name', '')
        cleaned_md["Start Date"] = user_md.get('beamtime_start', '')

        super().update_md(cleaned_md)

class ProposalStatus(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.REClientModel = model.run_engine
        self.user_status = model.user_status
        
        status = ProposalBox(self.user_status)
        
        self.button = QPushButton("New Proposal")
        self.button.clicked.connect(self.push_button)
        vbox = QVBoxLayout()
        vbox.addWidget(status)
        vbox.addWidget(self.button)
        self.setLayout(vbox)

    def push_button(self):
        dlg = ProposalSyncExperiment("New Proposal")
        dlg.exec()
