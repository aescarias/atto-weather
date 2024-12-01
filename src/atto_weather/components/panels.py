from __future__ import annotations

from typing import Any, Literal

from atto_weather.components.common import WeatherOverview, get_weather_icon
from atto_weather.components.current import CurrentAQIWidget, CurrentWeatherWidget
from atto_weather.components.forecast import (
    AstronomyWidget,
    DailyForecastWidget,
    HourlyForecastWidget,
)
from atto_weather.text import get_temperature
from PySide6.QtWidgets import QGridLayout, QListWidget, QListWidgetItem, QWidget


class CurrentWeatherPanel(QWidget):
    """Panel that displays the current weather (plus astronomy & air quality)"""

    def __init__(self) -> None:
        super().__init__()

        self.grid = QGridLayout()

        self.overview_wgt = WeatherOverview()
        self.weather_wgt = CurrentWeatherWidget()

        self.astronomy_group = AstronomyWidget()
        self.air_quality_group = CurrentAQIWidget()

        self.grid.addWidget(self.overview_wgt, 0, 0, 1, 2)
        self.grid.addWidget(self.weather_wgt, 1, 0, 2, 1)
        self.grid.addWidget(self.astronomy_group, 1, 1)
        self.grid.addWidget(self.air_quality_group, 2, 1)

        self.setLayout(self.grid)

    def update_details(
        self, current: dict[str, Any], astronomy: dict[str, Any]
    ) -> None:
        temp = get_temperature(current["temp_c"], current["temp_f"])
        condition = current["condition"]["text"]

        self.overview_wgt.update_details(
            f"{temp['value']}°{temp['unit']}",
            condition,
            get_weather_icon(current["condition"]["code"], bool(current["is_day"])),
        )

        self.weather_wgt.update_details(current)
        self.air_quality_group.update_details(current["air_quality"])
        self.astronomy_group.update_details(astronomy)


class ForecastOverviewPanel(QListWidget):
    """List widget including forecasts for the next ``n`` days (in the free plan, 3)"""

    def __init__(self) -> None:
        super().__init__()

        self.setStyleSheet("QListWidget { border: none; }")

    def update_details(self, forecasts: list[dict[str, Any]]) -> None:
        self.clear()

        for date in forecasts:
            overview = WeatherOverview(show_date=True)

            avgtemp = get_temperature(
                date["day"]["avgtemp_c"], date["day"]["avgtemp_f"]
            )

            overview.update_details(
                f"{avgtemp['value']}°{avgtemp['unit']}",
                date["day"]["condition"]["text"],
                get_weather_icon(date["day"]["condition"]["code"], True),
                # FIXME: Show a formatted value from the epoch here
                date["date"],
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
            raise ValueError(
                "Bad argument for forecast panel: must be 'daily' or 'hourly'"
            )

        self.astronomy_wgt = AstronomyWidget()

        self.grid.addWidget(self.overview_wgt, 0, 0, 1, 2)
        self.grid.addWidget(self.forecast_wgt, 1, 0, 2, 1)
        self.grid.addWidget(self.astronomy_wgt, 1, 1)

        self.setLayout(self.grid)

    def update_hourly_details(self, forecast: dict[str, Any], hour: int) -> None:
        hour_data = forecast["hour"][hour]

        temp = get_temperature(hour_data["temp_c"], hour_data["temp_f"])
        condition = hour_data["condition"]["text"]

        self.overview_wgt.update_details(
            f"{temp['value']}°{temp['unit']}",
            condition,
            get_weather_icon(hour_data["condition"]["code"], True),
        )
        self.forecast_wgt.update_details(hour_data)
        self.astronomy_wgt.update_details(forecast["astro"])

    def update_daily_details(self, forecast: dict[str, Any]) -> None:
        temp = get_temperature(
            forecast["day"]["avgtemp_c"], forecast["day"]["avgtemp_f"]
        )
        condition = forecast["day"]["condition"]["text"]

        self.overview_wgt.update_details(
            f"{temp['value']}°{temp['unit']}",
            condition,
            get_weather_icon(forecast["day"]["condition"]["code"], True),
        )
        self.forecast_wgt.update_details(forecast["day"])
        self.astronomy_wgt.update_details(forecast["astro"])
