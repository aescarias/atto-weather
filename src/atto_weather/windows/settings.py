from functools import partial
from typing import cast

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from atto_weather._self import APP_COPYRIGHT, APP_NAME, APP_VERSION
from atto_weather.i18n import get_translation as lo
from atto_weather.store import store, write_secrets, write_settings
from atto_weather.utils.settings import (
    DEFAULT_SECRETS,
    DEFAULT_SETTINGS,
    SECRETS_FIELDS,
    SETTINGS_FIELDS,
    SelectUISetting,
)


class SettingsDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(lo("app.settings"))

        self.vbox = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.general_tab = GeneralTab()
        self.about_tab = AboutTab()

        self.tab_widget.addTab(self.general_tab, lo("settings.general"))
        self.tab_widget.addTab(self.about_tab, lo("settings.about"))

        self.actions_hbox = QHBoxLayout()

        self.confirm_button = QPushButton(lo("app.confirm"))
        self.confirm_button.clicked.connect(self.close)

        self.actions_hbox.addSpacerItem(QSpacerItem(50, 10, QSizePolicy.Policy.Expanding))
        self.actions_hbox.addWidget(self.confirm_button)

        self.vbox.addWidget(self.tab_widget)
        self.vbox.addLayout(self.actions_hbox)
        self.setLayout(self.vbox)

    def closeEvent(self, event: QCloseEvent) -> None:
        write_secrets(store.secrets)
        write_settings(store.settings)

        return super().closeEvent(event)


class AboutTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap(":/app/app_icon.png").scaled(64, 64))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.app_name_label = QLabel(APP_NAME)
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.app_version_label = QLabel(APP_VERSION)
        self.app_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.app_rights_label = QLabel(APP_COPYRIGHT)
        self.app_rights_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.links_label = QLabel(
            f"""
            <a href='https://github.com/aescarias/atto-weather'>Github</a>
            <br><br>
            {lo("app.powered_by")}
            """
        )
        self.links_label.setOpenExternalLinks(True)
        self.links_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vbox.addWidget(self.image_label)
        self.vbox.addWidget(self.app_name_label)
        self.vbox.addWidget(self.app_version_label)
        self.vbox.addWidget(self.app_rights_label)
        self.vbox.addWidget(self.links_label)

        self.setLayout(self.vbox)


class GeneralTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.form = QFormLayout()

        for setting, field in SETTINGS_FIELDS.items():
            value = store.settings.get(setting)
            if value is None:
                value = DEFAULT_SETTINGS[setting]

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

                self.form.addRow(lo(field["label"]), combobox)
            elif field["kind"] == "check":
                assert isinstance(value, bool)

                checkbox = QCheckBox(lo(field["label"]))
                checkbox.setChecked(value)
                checkbox.checkStateChanged.connect(partial(self.update_checkbox, checkbox, setting))

                self.form.addRow(checkbox)

        for secret, field in SECRETS_FIELDS.items():
            value = store.secrets.get(secret)
            if field is None:
                value = DEFAULT_SECRETS[secret]
                continue

            if field["kind"] == "password":
                assert isinstance(value, str)

                edit = QLineEdit()
                edit.setText(value)
                edit.setEchoMode(QLineEdit.EchoMode.Password)

                if (app := cast(QApplication, QApplication.instance())) is not None:
                    app.focusChanged.connect(partial(self.handle_edit_focus, widget=edit))

                edit.textChanged.connect(partial(self.update_password, edit, secret))
                self.form.addRow(lo(field["label"]), edit)

        self.setLayout(self.form)

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
