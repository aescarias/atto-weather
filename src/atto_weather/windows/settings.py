import logging
from functools import partial
from typing import cast

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QComboBox, QCheckBox,
                               QLineEdit, QPushButton, QWidget, QHBoxLayout, QSpacerItem, 
                               QSizePolicy)

from atto_weather.i18n import get_language_map
from atto_weather.i18n import get_translation as lo
from atto_weather.store import store, write_settings, write_secrets

logging.basicConfig()

LOGGER = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "language": "en",
    "temperature": "celsius",
    "distance": "km",
    "pressure": "mbar",
    "height": "mm",
    "round_temp_values": True
}

DEFAULT_SECRETS = {
    "weatherapi": ""
}

SETTINGS_FIELDS = {
    "language": {
        "label": "settings.language",
        "type": "select",
        "options": get_language_map(),
        "options_preloc": True
    },
    "temperature": {
        "label": "settings.temperature.label",
        "type": "select",
        "options": {
            "celsius": "settings.temperature.celsius",
            "fahrenheit": "settings.temperature.fahrenheit"
        }
    },
    "pressure": {
        "label": "settings.pressure.label",
        "type": "select",
        "options": {
            "mbar": "settings.pressure.millibars",
            "inhg": "settings.pressure.inhg"
        }
    },
    "height": {
        "label": "settings.height.label",
        "type": "select",
        "options": {
            "mm": "settings.height.millimeters",
            "in": "settings.height.inches"
        }
    },
    "distance": {
        "label": "settings.distance.label",
        "type": "select",
        "options": { 
            "km": "settings.distance.kilometers",
            "mi": "settings.distance.miles"
        }
    },
    "round_temp_values": {
        "label": "settings.round_temp_values",
        "type": "check"
    }
}

SECRETS_FIELDS = {
    "weatherapi": {
        "label": "settings.weather_api_key",
        "type": "password"
    }
}


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

            if field["type"] == "select":
                combobox = QComboBox()
                if field.get("options_preloc"):
                    combobox.addItems(list(field["options"].values()))
                    combobox.setCurrentText(field["options"][value])
                else:
                    combobox.addItems(list(map(lo, field["options"].values())))
                    combobox.setCurrentText(lo(field["options"][value]))
            
                combobox.currentIndexChanged.connect(
                    partial(self.update_combobox, combobox, setting)
                )

                self.main_layout.addRow(lo(field["label"]), combobox)
            elif field["type"] == "check":
                checkbox = QCheckBox(lo(field["label"]))
                checkbox.setChecked(value)
                checkbox.checkStateChanged.connect(
                    partial(self.update_checkbox, checkbox, setting)
                )
                self.main_layout.addRow(checkbox)                

        for secret, value in store.secrets.items():
            field = SECRETS_FIELDS.get(secret)
            if field is None:
                LOGGER.warning(f"unknown field for secrets: {secret!r}")
                continue
            
            if field["type"] == "password":
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
        self.actions_layout.addSpacerItem(QSpacerItem(50, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.actions_layout.addWidget(self.confirm_button)

        self.main_layout.addRow(self.actions_layout)
        self.setLayout(self.main_layout)
    
    @Slot()
    def update_password(self, edit: QLineEdit, secret: str, *_qt_args) -> None:
        store.secrets[secret] = edit.text()

    @Slot()
    def update_combobox(self, combo: QComboBox, setting: str, *_qt_args) -> None:
        if SETTINGS_FIELDS[setting].get("options_preloc"):
            labels_to_values = {v: k for k, v in SETTINGS_FIELDS[setting]["options"].items()}
        else:
            labels_to_values = {lo(v): k for k, v in SETTINGS_FIELDS[setting]["options"].items()}

        store.settings[setting] = labels_to_values[combo.currentText()]

    @Slot()
    def update_checkbox(self, check: QCheckBox, setting: str, *_qt_args) -> None:
        if check.checkState() is Qt.CheckState.Checked:
            store.settings[setting] = True
        elif check.checkState() is Qt.CheckState.Unchecked:
            store.settings[setting] = False

    @Slot(QWidget, QWidget)
    def handle_edit_focus(self, old: QWidget, new: QWidget, *, widget: QLineEdit):
        if old is widget: # lost focus
            widget.setEchoMode(QLineEdit.EchoMode.Password)
        if new is widget: # gained focus
            widget.setEchoMode(QLineEdit.EchoMode.Normal)

    def closeEvent(self, arg__1: QCloseEvent) -> None:
        write_secrets(store.secrets)
        write_settings(store.settings)

        return super().closeEvent(arg__1)
