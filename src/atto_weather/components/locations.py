from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, QPersistentModelIndex, Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QListView, QMessageBox, QPushButton, QVBoxLayout, QWidget
from typing_extensions import TypeAlias

from atto_weather.i18n import get_translation as lo
from atto_weather.store import store, write_settings
from atto_weather.utils.settings import StoredLocation
from atto_weather.windows.add_location import AddLocationDialog

ModelIndex: TypeAlias = "QModelIndex | QPersistentModelIndex"


class StoredLocationModel(QAbstractListModel):
    def __init__(
        self, locations: list[StoredLocation] | None = None, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)

        self.locations = locations or []

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return

        if role == Qt.ItemDataRole.DisplayRole:
            return self.locations[index.row()]["name"]

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return len(self.locations)


class LocationManager(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.vbox = QVBoxLayout()

        self.locations_view = QListView()
        self.locations_model = StoredLocationModel(store.settings.get("locations", []))
        self.locations_view.setModel(self.locations_model)

        self.add_location_button = QPushButton()
        self.delete_location_button = QPushButton()
        self.move_up_button = QPushButton()
        self.move_down_button = QPushButton()

        self.hbox = QHBoxLayout()
        self.hbox.addStretch(10)
        self.hbox.addWidget(self.add_location_button)
        self.hbox.addWidget(self.delete_location_button)
        self.hbox.addWidget(self.move_up_button)
        self.hbox.addWidget(self.move_down_button)

        self.vbox.addWidget(self.locations_view)
        self.vbox.addLayout(self.hbox)

        self.add_location_button.clicked.connect(self.open_location_finder)
        self.delete_location_button.clicked.connect(self.delete_selected_item)
        self.move_up_button.clicked.connect(self.move_selected_up)
        self.move_down_button.clicked.connect(self.move_selected_down)

        self.locations_view.selectionModel().selectionChanged.connect(self.update_button_state)

        self.setLayout(self.vbox)
        self.update_button_state()
        self.localize()

    def localize(self) -> None:
        self.add_location_button.setText(lo("dialogs.location_manager.add_button"))
        self.delete_location_button.setText(lo("dialogs.location_manager.delete_button"))
        self.move_up_button.setText(lo("dialogs.location_manager.up_button"))
        self.move_down_button.setText(lo("dialogs.location_manager.down_button"))

    def update_button_state(self) -> None:
        current_row = self.locations_view.currentIndex().row()

        has_no_selection = current_row == -1
        met_up_bound = current_row <= 0
        met_down_bound = current_row >= self.locations_view.model().rowCount() - 1

        self.delete_location_button.setDisabled(has_no_selection)
        self.move_up_button.setDisabled(has_no_selection or met_up_bound)
        self.move_down_button.setDisabled(has_no_selection or met_down_bound)

    def delete_selected_item(self) -> None:
        if self.locations_model.rowCount() <= 1:
            QMessageBox.critical(
                self,
                lo("dialogs.location_manager.required_title"),
                lo("dialogs.location_manager.required_keep_message"),
            )
            return

        row = self.locations_view.currentIndex().row()

        self.locations_model.locations.pop(row)
        self.locations_model.layoutChanged.emit()

        store.settings["locations"] = self.locations_model.locations
        write_settings(store.settings)

    def move_selected_up(self) -> None:
        row = self.locations_view.currentIndex().row()
        if row <= 0:
            return

        above = self.locations_model.locations[row - 1]
        current = self.locations_model.locations[row]

        self.locations_model.locations[row - 1] = current
        self.locations_model.locations[row] = above

        self.locations_view.setCurrentIndex(self.locations_model.index(row - 1))

        store.settings["locations"] = self.locations_model.locations
        write_settings(store.settings)

    def move_selected_down(self) -> None:
        row = self.locations_view.currentIndex().row()
        if row == -1 or row >= self.locations_model.rowCount():
            return

        below = self.locations_model.locations[row + 1]
        current = self.locations_model.locations[row]

        self.locations_model.locations[row + 1] = current
        self.locations_model.locations[row] = below

        self.locations_view.setCurrentIndex(self.locations_model.index(row + 1))

        store.settings["locations"] = self.locations_model.locations
        write_settings(store.settings)

    def update_locations(self) -> None:
        self.locations_model.locations = store.settings.get("locations", [])
        self.locations_model.layoutChanged.emit()

    @Slot()
    def open_location_finder(self) -> None:
        dlg = AddLocationDialog()
        dlg.accepted.connect(self.update_locations)
        dlg.exec()
