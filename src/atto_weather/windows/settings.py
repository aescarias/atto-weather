import logging
from functools import partial
from typing import cast

from atto_weather.i18n import get_translation as lo
from atto_weather.store import store, write_secrets, write_settings
from atto_weather.utils.settings import SECRETS_FIELDS, SETTINGS_FIELDS, SelectUISetting
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

logging.basicConfig()

LOGGER = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(lo("app.settings"))
        self.main_layout = QFormLayout()

        for setting, value in store.settings.items():
            field = SETTINGS_FIELDS.get(setting)
            if field is None:
                LOGGER.warning(f"unknown field for settings: {setting!r}")
                continue

            if field["kind"] == "select":
                assert isinstance(value, str)

                combobox = QComboBox()
                if field.get("options_preloc", False):
                    combobox.addItems(list(field["options"].values()))
                    combobox.setCurrentText(field["options"][value])
                else:
                    combobox.addItems(list(map(lo, field["options"].values())))
                    combobox.setCurrentText(lo(field["options"][value]))

                combobox.currentIndexChanged.connect(
                    partial(self.update_combobox, combobox, setting)
                )

                self.main_layout.addRow(lo(field["label"]), combobox)
            elif field["kind"] == "check":
                assert isinstance(value, bool)

                checkbox = QCheckBox(lo(field["label"]))
                checkbox.setChecked(value)
                checkbox.checkStateChanged.connect(partial(self.update_checkbox, checkbox, setting))

                self.main_layout.addRow(checkbox)

        for secret, value in store.secrets.items():
            field = SECRETS_FIELDS.get(secret)
            if field is None:
                LOGGER.warning(f"unknown field for secrets: {secret!r}")
                continue

            if field["kind"] == "password":
                assert isinstance(value, str)

                edit = QLineEdit()
                edit.setText(value)
                edit.setEchoMode(QLineEdit.EchoMode.Password)

                if (app := cast(QApplication, QApplication.instance())) is not None:
                    app.focusChanged.connect(partial(self.handle_edit_focus, widget=edit))

                edit.textChanged.connect(partial(self.update_password, edit, secret))
                self.main_layout.addRow(lo(field["label"]), edit)

        self.actions_layout = QHBoxLayout()
        self.confirm_button = QPushButton(lo("app.confirm"))
        self.confirm_button.clicked.connect(self.close)
        self.actions_layout.addSpacerItem(
            QSpacerItem(50, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.actions_layout.addWidget(self.confirm_button)

        self.main_layout.addRow(self.actions_layout)
        self.setLayout(self.main_layout)

    @Slot()
    def update_password(self, edit: QLineEdit, secret: str, *_qt_args) -> None:
        store.secrets[secret] = edit.text()

    @Slot()
    def update_combobox(self, combo: QComboBox, setting: str, *_qt_args) -> None:
        select = cast(SelectUISetting, SETTINGS_FIELDS[setting])

        if select.get("options_preloc", False):
            labels_to_values = {v: k for k, v in select["options"].items()}
        else:
            labels_to_values = {lo(v): k for k, v in select["options"].items()}

        store.settings[setting] = labels_to_values[combo.currentText()]

    @Slot()
    def update_checkbox(self, check: QCheckBox, setting: str, *_qt_args) -> None:
        if check.checkState() is Qt.CheckState.Checked:
            store.settings[setting] = True
        elif check.checkState() is Qt.CheckState.Unchecked:
            store.settings[setting] = False

    @Slot(QWidget, QWidget)
    def handle_edit_focus(self, old: QWidget, new: QWidget, *, widget: QLineEdit):
        if old is widget:  # lost focus
            widget.setEchoMode(QLineEdit.EchoMode.Password)

        if new is widget:  # gained focus
            widget.setEchoMode(QLineEdit.EchoMode.Normal)

    def closeEvent(self, arg__1: QCloseEvent) -> None:
        write_secrets(store.secrets)
        write_settings(store.settings)

        return super().closeEvent(arg__1)
