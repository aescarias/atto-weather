from __future__ import annotations

from functools import partial
from typing import Any

from PySide6.QtCore import QThreadPool, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

from atto_weather._version import __version__ as APP_VERSION
from atto_weather.api import WeatherWorker
from atto_weather.components.panels import (
    CurrentWeatherPanel,
    ForecastOverviewPanel,
    TimeForecastPanel,
)
from atto_weather.i18n import get_translation as lo
from atto_weather.store import store
from atto_weather.text import format_datetime
from atto_weather.windows.settings import SettingsDialog


class AttoWeather(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.pool = QThreadPool()
        self.weather = None

        self.setWindowTitle("Atto Weather")

        self.main_widget = QWidget()

        self.main_layout = QVBoxLayout()

        # * Search Layout
        self.search_layout = QHBoxLayout()

        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText(lo("app.location_input_placeholder"))
        self.weather_fetch_button = QPushButton(lo("app.find_button"))
        self.weather_fetch_button.clicked.connect(self.fetch_weather)

        self.search_layout.addWidget(self.location_edit)
        self.search_layout.addWidget(self.weather_fetch_button)

        # * Location Details
        self.location_layout = QHBoxLayout()

        self.location_name_label = QLabel()
        self.location_time_label = QLabel()

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

        self.settings_button = QPushButton(lo("app.settings"))
        self.settings_button.clicked.connect(self.open_settings)
        self.statusbar.addWidget(self.settings_button)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(self.statusbar)

    @Slot()
    def open_settings(self) -> None:
        dlg = SettingsDialog()
        dlg.exec()

    @Slot(str, int)
    def handle_fetch_error(self, message: str, code: int) -> None:
        QMessageBox.critical(self, lo("app.weather_fetch_error"), f"WeatherAPI: {message} ({code})")
        self.weather_fetch_button.setEnabled(True)

    @Slot()
    def update_forecast(self) -> None:
        if self.weather is None:
            return

        idx = self.forecast.currentIndex().row()
        forecast = self.weather["forecast"]["forecastday"][idx]

        self.app_stack.setCurrentWidget(self.day_forecast)

        self.day_forecast.update_daily_details(forecast)
        # API provides no docs on this, but as far as I can tell, this value is UTC.
        self.location_time_label.setText(format_datetime(forecast["date_epoch"], "UTC", "date"))
        self.location_hour_select.setVisible(True)
        self.location_hour_select.clear()

        items = [lo("app.average")] + [
            format_datetime(hour["time_epoch"], self.weather["location"]["tz_id"], "time")
            for hour in forecast["hour"]
        ]

        self.location_hour_select.currentIndexChanged.connect(
            partial(self.update_hour_forecast, forecast)
        )
        self.location_hour_select.addItems(items)

    @Slot(dict)
    def update_weather(self, weather: dict[str, Any]) -> None:
        self.weather_fetch_button.setEnabled(True)

        self.weather = weather
        self.app_stack.setCurrentWidget(self.current_weather)

        location = ", ".join(
            val
            for val in [
                weather["location"]["name"],
                weather["location"]["region"],
                weather["location"]["country"],
            ]
            if val.strip()
        )
        self.location_name_label.setText(location)

        self.location_time_label.setText(
            format_datetime(
                weather["location"]["localtime_epoch"],
                weather["location"]["tz_id"],
                "date",
            )
        )

        self.current_weather.update_details(
            weather["current"], weather["forecast"]["forecastday"][0]["astro"]
        )

    @Slot()
    def update_hour_forecast(self, forecast: dict[str, Any], idx: int) -> None:
        if idx == 0:  # average
            self.app_stack.setCurrentWidget(self.day_forecast)
            return

        self.hour_forecast.update_hourly_details(forecast, idx - 1)
        self.app_stack.setCurrentWidget(self.hour_forecast)

    @Slot()
    def show_current(self) -> None:
        if self.weather is None:
            return

        self.location_hour_select.setVisible(False)
        self.app_stack.setCurrentWidget(self.current_weather)
        self.location_time_label.setText(
            format_datetime(
                self.weather["location"]["localtime_epoch"],
                self.weather["location"]["tz_id"],
                "date",
            )
        )

    @Slot()
    def show_forecast(self) -> None:
        if self.weather is None:
            return

        self.location_hour_select.setVisible(False)
        self.app_stack.setCurrentWidget(self.forecast)
        self.forecast.update_details(self.weather["forecast"]["forecastday"])

    @Slot()
    def fetch_weather(self) -> None:
        self.weather_fetch_button.setEnabled(False)

        worker = WeatherWorker(
            self.location_edit.text(),
            store.secrets["weatherapi"],
            store.settings["language"],
        )
        worker.signals.fetched.connect(self.update_weather)
        worker.signals.errored.connect(self.handle_fetch_error)

        self.pool.start(worker)
