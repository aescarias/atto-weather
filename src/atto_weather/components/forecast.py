from __future__ import annotations

from typing import Any

from atto_weather.components.common import WeatherFieldWidget
from atto_weather.components.current import CurrentWeatherWidget
from atto_weather.data_fields import (
    ASTRONOMY_FIELDS,
    DAILY_FORECAST_FIELDS,
    HOURLY_FORECAST_FIELDS,
    MOON_PHASE,
    estimate_uv_index,
)
from atto_weather.i18n import get_translation as lo
from atto_weather.text import get_distance, get_height, get_human_bool, get_temperature


class HourlyForecastWidget(WeatherFieldWidget):
    """Widget that contains details about the forecast for a specific hour"""

    def __init__(self) -> None:
        super().__init__(HOURLY_FORECAST_FIELDS, "form")

    def update_details(self, hour_forecast: dict[str, Any]) -> None:
        # Both current weather and hourly forecast use the same labels.
        # Hourly forecast includes two additional ones though and removes
        # the 'air quality' label as it's not included in the API response (free plan)
        CurrentWeatherWidget.update_details(self, hour_forecast, _aqi=False)  # pyright: ignore[reportArgumentType]

        self.set_label(
            "will_it_rain",
            value=get_human_bool(hour_forecast["will_it_rain"]),
            chance=hour_forecast["chance_of_rain"],
        )
        self.set_label(
            "will_it_snow",
            value=get_human_bool(hour_forecast["will_it_snow"]),
            chance=hour_forecast["chance_of_snow"],
        )


class DailyForecastWidget(WeatherFieldWidget):
    """Widget that contains details about the forecast for an entire day"""

    def __init__(self) -> None:
        super().__init__(DAILY_FORECAST_FIELDS, "form")

    def update_details(self, day_forecast: dict[str, Any]) -> None:
        min_temp = get_temperature(day_forecast["mintemp_c"], day_forecast["mintemp_f"])
        max_temp = get_temperature(day_forecast["maxtemp_c"], day_forecast["maxtemp_f"])

        self.set_label(
            "min_max_temp",
            mintemp=min_temp["value"],
            minunit=min_temp["unit"],
            maxtemp=max_temp["value"],
            maxunit=max_temp["unit"],
        )
        self.set_label(
            "max_wind",
            **get_distance(day_forecast["maxwind_kph"], day_forecast["maxwind_mph"], speed=True),
        )
        self.set_label(
            "precipitation",
            **get_height(day_forecast["totalprecip_mm"], day_forecast["totalprecip_in"]),
        )
        self.set_label("snowfall", height=day_forecast["totalsnow_cm"], unit="cm")
        self.set_label(
            "avg_visibility",
            **get_distance(day_forecast["avgvis_km"], day_forecast["avgvis_miles"]),
        )
        self.set_label(
            "will_it_rain",
            value=get_human_bool(day_forecast["daily_will_it_rain"]),
            chance=day_forecast["daily_chance_of_rain"],
        )
        self.set_label(
            "will_it_snow",
            value=get_human_bool(day_forecast["daily_will_it_snow"]),
            chance=day_forecast["daily_chance_of_snow"],
        )
        self.set_label(
            "uv_index",
            value=day_forecast["uv"],
            summary=estimate_uv_index(day_forecast["uv"]),
        )


class AstronomyWidget(WeatherFieldWidget):
    """Widget that contains details about astronomical events for this day"""

    def __init__(self) -> None:
        super().__init__(ASTRONOMY_FIELDS, "grid")

    def update_details(self, astro: dict[str, Any]) -> None:
        self.set_label("sunrise", value=astro["sunrise"])
        self.set_label("sunset", value=astro["sunset"])
        self.set_label("moonrise", value=astro["moonrise"])
        self.set_label("moonset", value=astro["moonset"])
        self.set_label("moon_phase", phase=lo(MOON_PHASE[astro["moon_phase"]]))
        self.set_label("moon_illum", illum=astro["moon_illumination"])
