from __future__ import annotations

from enum import IntEnum
from typing import Any

from PySide6.QtCore import Qt, QThreadPool, QTimer, Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from atto_weather._self import APP_NAME
from atto_weather.api.core import AutocompleteResult
from atto_weather.api.worker import WeatherWorker
from atto_weather.components.locations import LocationManager
from atto_weather.i18n import get_language_map, set_language
from atto_weather.i18n import get_translation as lo
from atto_weather.store import SECRETS_FILE, store, write_secrets, write_settings
from atto_weather.utils.settings import DEFAULT_SECRETS, StoredLocation


class PageId(IntEnum):
    WELCOME = 0
    API_SETUP = 1
    LOCATION_PROMPT = 2
    LOCATION_MANAGE = 3
    CONCLUSION = 4


class WelcomePage(QWizardPage):
    """The Welcome page greets the user and asks for their language."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(10)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)

        self.language_hbox = QHBoxLayout()

        self.language_select = QComboBox()

        self.language_select.addItems([lang for lang in get_language_map().values()])

        self.language_select_label = QLabel()

        self.language_hbox.addWidget(self.language_select_label)
        self.language_hbox.addWidget(self.language_select, 1)

        self.vbox.addWidget(self.info_label)
        self.vbox.addLayout(self.language_hbox)

        self.setLayout(self.vbox)

        self.registerField("language", self.language_select, "currentText", "currentTextChanged")

        self.localize()

    def localize(self) -> None:
        self.setTitle(lo("wizard.welcome.page"))

        self.info_label.setText(lo("wizard.welcome.details"))
        self.language_select_label.setText(lo("settings.language"))

    def nextId(self) -> int:
        lang_to_code = {lang: code for code, lang in get_language_map().items()}

        store.settings["language"] = lang_to_code[self.field("language")]
        set_language(store.settings["language"])
        write_settings(store.settings)

        # skip api setup if a key is present
        if SECRETS_FILE.exists():
            return PageId.LOCATION_PROMPT

        return PageId.API_SETUP


class APISetupPage(QWizardPage):
    """The API Setup page asks users for their API key from WeatherAPI and validates it with
    a request before continuing."""

    def __init__(self) -> None:
        super().__init__()

        self.pool = QThreadPool.globalInstance()

        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(10)

        self.info_label = QLabel()
        self.info_label.setOpenExternalLinks(True)
        self.info_label.setWordWrap(True)

        self.key_hbox = QHBoxLayout()

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.api_key_label = QLabel()

        self.key_hbox.addWidget(self.api_key_label)
        self.key_hbox.addWidget(self.api_key_edit, 1)

        self.status_label = QLabel()

        self.vbox.addWidget(self.info_label)
        self.vbox.addLayout(self.key_hbox)
        self.vbox.addWidget(self.status_label)

        self.registerField("apikey*", self.api_key_edit)

        self.localize()
        self.setLayout(self.vbox)

    def localize(self) -> None:
        self.setTitle(lo("wizard.api_setup.page"))

        self.info_label.setText(lo("wizard.api_setup.details"))
        self.api_key_label.setText(lo("wizard.api_setup.api_key"))

    def initializePage(self) -> None:
        """Initializes the page by adding the validation logic if not present."""
        if self.wizard().hasVisitedPage(PageId.API_SETUP):
            return

        self.wizard().currentIdChanged.connect(self.setup_on_visit)

    def validate_on_next(self) -> None:
        next_button = self.wizard().button(QWizard.WizardButton.NextButton)

        next_button.clicked.disconnect()
        next_button.clicked.connect(self.handle_validation)

    def setup_on_visit(self, new_id: int) -> None:
        if new_id == PageId.API_SETUP:
            self.validate_on_next()

    def handle_validation(self) -> None:
        self.wizard().button(QWizard.WizardButton.NextButton).setDisabled(True)
        self.status_label.setText(lo("wizard.api_setup.status_validating"))

        worker = WeatherWorker("forecast", "auto:ip", self.field("apikey"), "en")

        worker.signals.fetched.connect(self.handle_valid_key)
        worker.signals.errored.connect(self.handle_invalid_key)

        self.pool.tryStart(worker)

    @Slot()
    def handle_valid_key(self) -> None:
        self.status_label.setText(lo("wizard.api_setup.status_valid"))

        store.secrets = DEFAULT_SECRETS
        store.secrets["weatherapi"] = self.field("apikey")
        write_secrets(store.secrets)

        QTimer.singleShot(500, self._go_to_next_page)

    @Slot(str, int)
    def handle_invalid_key(self, message: str, code: int) -> None:
        self.status_label.setText(
            lo("wizard.api_setup.status_invalid").format(code=code, message=message)
        )

    def _go_to_next_page(self) -> None:
        # QWizard does not perform cleanup when going to the next page
        # so it must be called explicitly
        self.cleanupPage()

        # go to the next page as usual once cleanup happens
        self.wizard().next()

    def cleanupPage(self) -> None:
        """Disconnects the validation logic from Next and resets to defaults."""
        next_button = self.wizard().button(QWizard.WizardButton.NextButton)

        next_button.clicked.disconnect()
        next_button.clicked.connect(self._go_to_next_page)

        self.status_label.setText("")

        return super().cleanupPage()

    def nextId(self) -> int:
        return PageId.LOCATION_PROMPT


class LocationPromptPage(QWizardPage):
    """The location prompt page gives users a decision between adding their own
    locations or simply adding their current location."""

    def __init__(self) -> None:
        super().__init__()

        self.pool = QThreadPool.globalInstance()

        self.setTitle(lo("wizard.location_prompt.page"))

        self.vbox = QVBoxLayout()

        self.info_label = QLabel(lo("wizard.location_prompt.details"))

        self.location_manual_radio = QRadioButton(lo("wizard.location_prompt.manual"))
        self.location_auto_radio = QRadioButton(lo("wizard.location_prompt.auto"))
        self.location_auto_radio.setChecked(True)

        self.status_label = QLabel()

        self.vbox.addWidget(self.info_label)
        self.vbox.addWidget(self.location_manual_radio)
        self.vbox.addWidget(self.location_auto_radio)
        self.vbox.addWidget(self.status_label)

        self.setLayout(self.vbox)
        self.localize()

    def localize(self) -> None:
        self.setTitle(lo("wizard.location_prompt.page"))

        self.info_label.setText(lo("wizard.location_prompt.details"))
        self.location_manual_radio.setText(lo("wizard.location_prompt.manual"))
        self.location_auto_radio.setText(lo("wizard.location_prompt.auto"))

    def initializePage(self) -> None:
        # skip this page if locations are set
        if store.settings.get("locations"):
            return self.wizard().next()

        if self.wizard().hasVisitedPage(PageId.LOCATION_PROMPT):
            return

        # hook the "Next" button on visit
        self.wizard().currentIdChanged.connect(self.setup_on_visit)

    def check_prompt_on_next(self) -> None:
        next_button = self.wizard().button(QWizard.WizardButton.NextButton)

        next_button.clicked.disconnect()
        next_button.clicked.connect(self.check_prompt)

    def setup_on_visit(self, new_id: int) -> None:
        if new_id == PageId.LOCATION_PROMPT:
            self.check_prompt_on_next()

    def check_prompt(self) -> None:
        if not self.location_auto_radio.isChecked():
            return self.wizard().next()

        self.wizard().button(QWizard.WizardButton.NextButton).setDisabled(True)
        self.status_label.setText(lo("wizard.location_prompt.status_adding"))

        worker = WeatherWorker("search", "auto:ip", store.secrets["weatherapi"], "en")

        worker.signals.fetched.connect(self.handle_success)
        worker.signals.errored.connect(self.handle_failure)

        self.pool.tryStart(worker)

    @Slot(object)
    def handle_success(self, results: list[dict[str, Any]]) -> None:
        self.status_label.setText(lo("wizard.location_prompt.status_success"))

        autocomplete = AutocompleteResult.from_dict(results[0])

        location = StoredLocation(name=autocomplete.full_name, ident=autocomplete.ident)

        store.settings["locations"].append(location)
        write_settings(store.settings)

        QTimer.singleShot(500, self._go_to_next_page)

    @Slot(str, int)
    def handle_failure(self, message: str, code: int) -> None:
        self.status_label.setText(
            lo("wizard.location_prompt.status_failure").format(code=code, message=message)
        )

    def _go_to_next_page(self) -> None:
        self.cleanupPage()
        self.wizard().next()

    def cleanupPage(self) -> None:
        """Disconnects the autocomplete logic from Next and resets to defaults."""
        next_button = self.wizard().button(QWizard.WizardButton.NextButton)

        next_button.clicked.disconnect()
        next_button.clicked.connect(self._go_to_next_page)

        self.status_label.setText("")

        return super().cleanupPage()

    def nextId(self) -> int:
        if self.location_auto_radio.isChecked():
            return PageId.CONCLUSION

        return PageId.LOCATION_MANAGE


class LocationManagePage(QWizardPage):
    """The 'Manage Locations' page allows users to select their desired locations."""

    def __init__(self) -> None:
        super().__init__()

        self.vbox = QVBoxLayout()

        self.info_label = QLabel()

        self.manager = LocationManager()

        self.vbox.addWidget(self.info_label)
        self.vbox.addWidget(self.manager)

        self.setLayout(self.vbox)
        self.localize()

    def localize(self) -> None:
        self.setTitle(lo("wizard.location_prompt.page"))
        self.info_label.setText(lo("wizard.location_manage.details"))
        self.manager.localize()

    def nextId(self) -> int:
        return PageId.CONCLUSION


class ConclusionPage(QWizardPage):
    """The Conclusion page is the last page before the user enters the application."""

    def __init__(self) -> None:
        super().__init__()

        self.vbox = QVBoxLayout()

        self.info_label = QLabel()
        self.vbox.addWidget(self.info_label)

        self.localize()
        self.setLayout(self.vbox)

    def localize(self) -> None:
        self.setTitle(lo("wizard.conclusion.page"))
        self.info_label.setText(lo("wizard.conclusion.details"))

    def nextId(self) -> int:
        return -1


class SetupWizard(QWizard):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.addPage(WelcomePage())
        self.addPage(APISetupPage())
        self.addPage(LocationPromptPage())
        self.addPage(LocationManagePage())
        self.addPage(ConclusionPage())

        self.setStartId(PageId.WELCOME)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.NoCancelButton, True)

        self.currentIdChanged.connect(self.localize_on_visit)

    def localize_on_visit(self, page_id: int) -> None:
        page = self.page(page_id)
        if localize := getattr(page, "localize", None):
            localize()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            return

        return super().keyPressEvent(event)
