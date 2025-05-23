from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    QThreadPool,
    QTimer,
    Slot,
)
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QPushButton,
    QVBoxLayout,
)
from typing_extensions import TypeAlias

from atto_weather.api.core import AutocompleteResult
from atto_weather.api.worker import WeatherWorker
from atto_weather.i18n import get_translation as lo
from atto_weather.store import store, write_settings
from atto_weather.utils.settings import StoredLocation

ModelIndex: TypeAlias = "QModelIndex | QPersistentModelIndex"


class LocationModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.locations: list[AutocompleteResult] = []

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return

        if role == Qt.ItemDataRole.DisplayRole:
            return self.locations[index.row()].full_name

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return len(self.locations)


class AddLocationDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.pool = QThreadPool.globalInstance()

        self.setWindowTitle(lo("dialogs.add_location.title"))

        self.main_layout = QVBoxLayout()

        self.debounce_timer = QTimer()
        self.debounce_timer.setInterval(500)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.fetch_autocomplete)

        self.location_search_edit = QLineEdit()
        self.location_search_edit.setPlaceholderText(lo("app.location_input_placeholder"))
        self.location_search_edit.textChanged.connect(self.start_debounce)

        self.location_status_label = QLabel()
        self.location_status_label.setHidden(True)

        self.location_results_view = QListView()
        self.location_results_model = LocationModel()
        self.location_results_view.setModel(self.location_results_model)

        self.add_location_button = QPushButton(lo("dialogs.add_location.add_button"))
        self.add_location_button.setDisabled(True)
        self.add_location_button.clicked.connect(self.add_location)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(10)
        self.button_layout.addWidget(self.add_location_button)

        self.main_layout.addWidget(self.location_search_edit)
        self.main_layout.addWidget(self.location_status_label)
        self.main_layout.addWidget(self.location_results_view)
        self.main_layout.addLayout(self.button_layout)

        self.location_results_view.selectionModel().selectionChanged.connect(self.handle_selection)

        self.setLayout(self.main_layout)

    def start_debounce(self) -> None:
        self.debounce_timer.start()
        self.location_status_label.setHidden(True)

    def handle_selection(self) -> None:
        self.add_location_button.setDisabled(False)

    def add_location(self) -> None:
        idx = self.location_results_view.currentIndex().row()
        ac_result = self.location_results_model.locations[idx]

        stored = StoredLocation(ident=ac_result.ident, name=ac_result.full_name)

        if "locations" in store.settings:
            store.settings["locations"].append(stored)
        else:
            store.settings["locations"] = [stored]

        write_settings(store.settings)

        self.accept()

    @Slot()
    def fetch_autocomplete(self) -> None:
        text = self.location_search_edit.text().strip()
        if not text:
            return

        worker = WeatherWorker(
            "search", text, store.secrets["weatherapi"], store.settings["language"]
        )

        self.location_status_label.setHidden(False)
        self.location_status_label.setText(lo("dialogs.add_location.searching"))

        worker.signals.fetched.connect(self.handle_success)
        worker.signals.api_errored.connect(self.handle_api_failure)
        worker.signals.request_errored.connect(self.handle_request_failure)

        self.pool.tryStart(worker)

    @Slot(object)
    def handle_success(self, locations: list[dict[str, Any]]) -> None:
        self.location_results_model.locations = [
            AutocompleteResult.from_dict(location) for location in locations
        ]
        self.location_results_model.layoutChanged.emit()

        if len(locations) == 0:
            text = lo("dialogs.add_location.found_locations.zero")
        elif len(locations) == 1:
            text = lo("dialogs.add_location.found_locations.one")
        else:
            text = lo("dialogs.add_location.found_locations.many").format(number=len(locations))

        self.location_status_label.setText(text)

    @Slot(str, int)
    def handle_api_failure(self, message: str, code: int) -> None:
        self.location_status_label.setHidden(False)
        self.location_status_label.setText(
            lo("dialogs.add_location.error").format(message=message, code=code)
        )

    @Slot(str, str)
    def handle_request_failure(self, class_name: str, message: str) -> None:
        self.location_status_label.setHidden(False)
        self.location_status_label.setText(f"{class_name}: {message}")
