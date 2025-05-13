from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QListWidget, QListWidgetItem, QWidget

from atto_weather.api.core import Astronomy, CurrentWeather, Forecast
from atto_weather.components.common import WeatherOverview, get_weather_icon
from atto_weather.components.current import AirQualityWidget, CurrentWeatherWidget
from atto_weather.components.forecast import (
    AstronomyWidget,
    DailyForecastWidget,
    HourlyForecastWidget,
)
from atto_weather.utils.text import format_iso8601, format_temperature


class CurrentWeatherPanel(QWidget):
    """Panel that displays the current weather (plus astronomy & air quality)"""

    def __init__(self) -> None:
        super().__init__()

        self.grid = QGridLayout()

        self.overview_wgt = WeatherOverview()
        self.weather_wgt = CurrentWeatherWidget()

        self.astronomy_group = AstronomyWidget()
        self.air_quality_group = AirQualityWidget()

        self.grid.addWidget(self.overview_wgt, 0, 0, 1, 2)
        self.grid.addWidget(self.weather_wgt, 1, 0, 2, 1)
        self.grid.addWidget(self.astronomy_group, 1, 1)
        self.grid.addWidget(self.air_quality_group, 2, 1)

        self.grid.setAlignment(Qt.AlignmentFlag.AlignBaseline)

        self.setLayout(self.grid)

    def update_details(self, current: CurrentWeather, astronomy: Astronomy) -> None:
        self.overview_wgt.update_details(
            format_temperature(current.temperature),
            current.condition.text,
            get_weather_icon(current.condition.code, current.is_day),
        )

        self.weather_wgt.update_details(current)
        self.air_quality_group.update_details(current.air_quality)
        self.astronomy_group.update_details(astronomy)


class ForecastOverviewPanel(QListWidget):
    """List widget including forecasts for the next ``n`` days (in the free plan, 3)"""

    def __init__(self) -> None:
        super().__init__()

        self.setStyleSheet("QListWidget { border: none; }")

    def update_details(self, forecasts: list[Forecast]) -> None:
        self.clear()

        for date in forecasts:
            overview = WeatherOverview(show_date=True)

            overview.update_details(
                format_temperature(date.day.avg_temperature),
                date.day.condition.text,
                get_weather_icon(date.day.condition.code, True),
                format_iso8601(date.date_formatted, "date"),
            )

            item = QListWidgetItem()
            item.setSizeHint(overview.sizeHint())

            self.addItem(item)
            self.setItemWidget(item, overview)


class TimeForecastPanel(QWidget):
    """Panel that displays forecasts for either the entire day or a specific hour"""

    def __init__(self, type_: Literal["daily", "hourly"]) -> None:
        super().__init__()

        self.type_ = type_
        self.grid = QGridLayout()

        self.overview_wgt = WeatherOverview()
        if self.type_ == "daily":
            self.forecast_wgt = DailyForecastWidget()
        elif self.type_ == "hourly":
            self.forecast_wgt = HourlyForecastWidget()
        else:
            raise ValueError("Bad argument for forecast panel: must be 'daily' or 'hourly'")

        self.astronomy_wgt = AstronomyWidget()

        self.grid.addWidget(self.overview_wgt, 0, 0, 1, 2)
        self.grid.addWidget(self.forecast_wgt, 1, 0, 2, 1)
        self.grid.addWidget(self.astronomy_wgt, 1, 1)

        self.setLayout(self.grid)

    def update_hourly_details(self, forecast: Forecast, hour_index: int) -> None:
        hour = forecast.hours[hour_index]

        self.overview_wgt.update_details(
            format_temperature(hour.temperature),
            hour.condition.text,
            get_weather_icon(hour.condition.code, True),
        )

        self.forecast_wgt.update_details(hour)  # type: ignore
        self.astronomy_wgt.update_details(forecast.astronomy)

    def update_daily_details(self, forecast: Forecast) -> None:
        self.overview_wgt.update_details(
            format_temperature(forecast.day.avg_temperature),
            forecast.day.condition.text,
            get_weather_icon(forecast.day.condition.code, True),
        )

        self.forecast_wgt.update_details(forecast.day)  # type: ignore
        self.astronomy_wgt.update_details(forecast.astronomy)
