from __future__ import annotations

from functools import partial
from typing import Any

from PySide6.QtCore import QThreadPool, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from atto_weather._self import APP_NAME, APP_VERSION
from atto_weather.api.core import Forecast, WeatherInfo
from atto_weather.api.worker import WeatherWorker
from atto_weather.components.common import LocationLabel
from atto_weather.components.locations import LocationManager, StoredLocationModel
from atto_weather.components.panels import (
    CurrentWeatherPanel,
    ForecastOverviewPanel,
    TimeForecastPanel,
)
from atto_weather.i18n import get_translation as lo
from atto_weather.store import store
from atto_weather.utils.text import format_datetime
from atto_weather.windows.settings import SettingsDialog


class AttoWeather(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.pool = QThreadPool()
        self.weather_data: WeatherInfo | None = None

        self.setWindowTitle(APP_NAME)

        self.main_widget = QWidget()

        self.main_layout = QVBoxLayout()

        # * Search Layout
        self.search_layout = QHBoxLayout()

        self.location_select = QComboBox()
        self.location_model = StoredLocationModel()
        self.location_select.setModel(self.location_model)

        self.manage_locations_button = QPushButton(lo("app.manage_locations"))
        self.manage_locations_button.clicked.connect(self.open_location_manager)

        self.fetch_weather_button = QPushButton(lo("app.fetch_weather"))
        self.fetch_weather_button.clicked.connect(self.fetch_weather)

        self.search_layout.addWidget(self.location_select, 1)
        self.search_layout.addWidget(self.manage_locations_button)
        self.search_layout.addWidget(self.fetch_weather_button)

        # * Location Details
        self.location_layout = QHBoxLayout()

        self.location_name_label = LocationLabel()
        self.location_time_label = LocationLabel()

        # Only visible with hourly forecasts
        self.location_hour_select = QComboBox()
        self.location_hour_select.setVisible(False)

        self.location_layout.addWidget(self.location_name_label)
        self.location_layout.addSpacerItem(
            QSpacerItem(50, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.location_layout.addWidget(self.location_time_label)
        self.location_layout.addWidget(self.location_hour_select)

        # * Tab-Like Button Actions
        self.actions_layout = QHBoxLayout()
        self.show_current_button = QPushButton(lo("app.current_weather"))
        self.show_forecast_button = QPushButton(lo("app.forecast"))
        self.show_current_button.clicked.connect(self.show_current)
        self.show_forecast_button.clicked.connect(self.show_forecast)

        self.actions_layout.addWidget(self.show_current_button)
        self.actions_layout.addWidget(self.show_forecast_button)
        self.actions_layout.addSpacerItem(
            QSpacerItem(50, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum),
        )

        # * App Info Stack
        self.app_stack = QStackedWidget()

        self.current_weather = CurrentWeatherPanel()
        self.forecast = ForecastOverviewPanel()
        self.forecast.itemActivated.connect(self.update_forecast)
        self.forecast.itemClicked.connect(self.update_forecast)
        self.day_forecast = TimeForecastPanel("daily")
        self.hour_forecast = TimeForecastPanel("hourly")

        self.app_stack.addWidget(self.current_weather)
        self.app_stack.addWidget(self.forecast)
        self.app_stack.addWidget(self.day_forecast)
        self.app_stack.addWidget(self.hour_forecast)

        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addLayout(self.actions_layout)
        self.main_layout.addLayout(self.location_layout)
        self.main_layout.addWidget(self.app_stack)

        # * Statusbar
        self.statusbar = QStatusBar()
        self.attrib_label = QLabel(f"{lo('app.powered_by')} · version {APP_VERSION}")
        self.attrib_label.setOpenExternalLinks(True)
        self.statusbar.addWidget(self.attrib_label, 1)

        self.quota_label = QLabel()
        self.statusbar.addWidget(self.quota_label)

        self.settings_button = QPushButton(lo("app.settings"))
        self.settings_button.clicked.connect(self.open_settings)
        self.statusbar.addWidget(self.settings_button)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(self.statusbar)

        self.update_locations()

    @Slot()
    def open_settings(self) -> None:
        dlg = SettingsDialog()
        dlg.exec()

    @Slot()
    def open_location_manager(self) -> None:
        dlg = QDialog()
        dlg.setWindowTitle(lo("dialogs.location_manager.title"))

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        manager = LocationManager()
        vbox.addWidget(manager)
        dlg.setLayout(vbox)

        dlg.exec()
        self.update_locations(self.location_select.currentIndex())

    @Slot()
    def update_locations(self, index_to_select: int = 0) -> None:
        self.location_model.locations = store.settings.get("locations", [])
        self.location_model.layoutChanged.emit()

        if index_to_select < 0:
            index_to_select %= self.location_model.rowCount()

        self.location_select.setCurrentIndex(index_to_select)

    @Slot(str, int)
    def handle_fetch_error(self, message: str, code: int) -> None:
        QMessageBox.critical(self, lo("app.fetch_error_title"), f"WeatherAPI: {message} ({code})")

    @Slot()
    def update_forecast(self) -> None:
        if self.weather_data is None:
            return

        idx = self.forecast.currentIndex().row()
        forecast = self.weather_data.forecasts[idx]

        self.app_stack.setCurrentWidget(self.day_forecast)

        self.day_forecast.update_daily_details(forecast)

        self.location_time_label.setText(format_datetime(forecast.date_epoch, "UTC", "date"))
        self.location_hour_select.setVisible(True)
        self.location_hour_select.clear()

        items = [lo("app.average")] + [
            format_datetime(hour.time_epoch, self.weather_data.location.timezone_id, "time")
            for hour in forecast.hours
        ]

        self.location_hour_select.currentIndexChanged.connect(
            partial(self.update_hour_forecast, forecast)
        )
        self.location_hour_select.addItems(items)

    @Slot(dict)
    def update_weather(self, weather: dict[str, Any], quota_left: int) -> None:
        self.weather_data = WeatherInfo.from_dict(weather)
        self.app_stack.setCurrentWidget(self.current_weather)

        if store.settings["show_quota"]:
            self.quota_label.setVisible(True)
            self.quota_label.setText(lo("app.quota_left").format(quota=quota_left))
        else:
            self.quota_label.setVisible(False)
            self.quota_label.setText("")

        self.location_name_label.update_location(self.weather_data.location)
        self.location_time_label.update_time(self.weather_data.location)

        self.location_time_label.setText(
            format_datetime(
                self.weather_data.location.localtime_epoch,
                self.weather_data.location.timezone_id,
                "date",
            )
        )

        self.current_weather.update_details(
            self.weather_data.current, self.weather_data.forecasts[0].astronomy
        )

    @Slot()
    def update_hour_forecast(self, forecast: Forecast, idx: int) -> None:
        if idx == 0:  # average
            self.app_stack.setCurrentWidget(self.day_forecast)
            return

        self.hour_forecast.update_hourly_details(forecast, idx - 1)
        self.app_stack.setCurrentWidget(self.hour_forecast)

    @Slot()
    def show_current(self) -> None:
        if self.weather_data is None:
            return

        self.location_hour_select.setVisible(False)
        self.app_stack.setCurrentWidget(self.current_weather)
        self.location_time_label.setText(
            format_datetime(
                self.weather_data.location.localtime_epoch,
                self.weather_data.location.timezone_id,
                "date",
            )
        )

    @Slot()
    def show_forecast(self) -> None:
        if self.weather_data is None:
            return

        self.location_hour_select.setVisible(False)
        self.app_stack.setCurrentWidget(self.forecast)
        self.forecast.update_details(self.weather_data.forecasts)

    @Slot()
    def fetch_weather(self) -> None:
        ident = self.location_model.locations[self.location_select.currentIndex()]

        worker = WeatherWorker(
            "forecast", f"id:{ident}", store.secrets["weatherapi"], store.settings["language"]
        )
        worker.signals.fetched.connect(self.update_weather)
        worker.signals.errored.connect(self.handle_fetch_error)

        self.pool.start(worker)
