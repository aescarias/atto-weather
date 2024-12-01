from atto_weather.i18n import get_translation as lo
from atto_weather.store import store, write_secrets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout


class CredentialsRequiredDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(lo("app.creds_required"))
        self.setMinimumSize(400, 100)

        self.main_layout = QVBoxLayout()

        self.details_label = QLabel()
        self.details_label.setOpenExternalLinks(True)
        self.details_label.setTextFormat(Qt.TextFormat.RichText)
        self.details_label.setWordWrap(True)
        self.details_label.setText(lo("app.creds_required_details"))

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText(lo("app.enter_api_key"))
        self.api_key_edit.textChanged.connect(self.check_input)

        self.confirm_button = QPushButton(lo("app.confirm"))
        self.confirm_button.clicked.connect(self.store_api_creds)

        self.main_layout.addWidget(self.details_label)
        self.main_layout.addWidget(self.api_key_edit)
        self.main_layout.addWidget(self.confirm_button)

        self.check_input()
        self.rejected.connect(self.handle_rejection)
        self.setLayout(self.main_layout)

    def store_api_creds(self) -> None:
        store.secrets = {"weatherapi": self.api_key_edit.text()}
        write_secrets(store.secrets)

        self.accept()

    def handle_rejection(self) -> None:
        self.close()

    def check_input(self) -> None:
        if self.api_key_edit.text().strip():
            self.confirm_button.setEnabled(True)
        else:
            self.confirm_button.setEnabled(False)
