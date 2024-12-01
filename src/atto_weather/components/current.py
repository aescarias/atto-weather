from __future__ import annotations

from typing import Any

from atto_weather.components.common import WeatherFieldWidget
from atto_weather.data_fields import (
    AIR_QUALITY_FIELDS,
    CURRENT_WEATHER_FIELDS,
    POINT16_COMPASS,
    US_EPA_INDEX,
    estimate_cloud_cover,
    estimate_uv_index,
    get_defra_index,
)
from atto_weather.i18n import get_translation as lo
from atto_weather.text import get_distance, get_height, get_pressure, get_temperature


class CurrentWeatherWidget(WeatherFieldWidget):
    """Widget that contains details about the current weather"""

    def __init__(self) -> None:
        super().__init__(CURRENT_WEATHER_FIELDS, "form")

    def update_details(self, current: dict[str, Any], *, _aqi: bool = True) -> None:
        self.set_label(
            "feels_like",
            **get_temperature(current["feelslike_c"], current["feelslike_f"]),
        )
        self.set_label(
            "windchill",
            **get_temperature(current["windchill_c"], current["windchill_f"]),
        )
        self.set_label(
            "heat_index",
            **get_temperature(current["heatindex_c"], current["heatindex_f"]),
        )
        self.set_label(
            "dew_point", **get_temperature(current["dewpoint_c"], current["dewpoint_f"])
        )
        self.set_label(
            "wind_speed",
            **get_distance(current["wind_kph"], current["wind_mph"], speed=True),
            degree=current["wind_degree"],
            dir_short=current["wind_dir"],
            direction=lo(POINT16_COMPASS[current["wind_dir"]]),
        )
        self.set_label(
            "wind_gust",
            **get_distance(current["gust_kph"], current["gust_mph"], speed=True),
        )
        self.set_label("humidity", value=current["humidity"])
        self.set_label(
            "precipitation", **get_height(current["precip_mm"], current["precip_in"])
        )
        self.set_label(
            "pressure", **get_pressure(current["pressure_mb"], current["pressure_in"])
        )
        self.set_label(
            "cloud_cover",
            value=current["cloud"],
            summary=estimate_cloud_cover(current["cloud"]),
        )
        self.set_label(
            "visibility", **get_distance(current["vis_km"], current["vis_miles"])
        )
        self.set_label(
            "uv_index", value=current["uv"], summary=estimate_uv_index(current["uv"])
        )

        if _aqi:
            print(current)
            self.set_label(
                "air_quality",
                summary=lo(US_EPA_INDEX[current["air_quality"]["us-epa-index"]]),
            )


class CurrentAQIWidget(WeatherFieldWidget):
    """Widget that contains details about the air quality at this moment"""

    def __init__(self) -> None:
        super().__init__(AIR_QUALITY_FIELDS, "grid")

    def update_details(self, air_quality: dict[str, Any]) -> None:
        self.set_label("co", value=air_quality["co"])
        self.set_label("o3", value=air_quality["o3"])
        self.set_label("no2", value=air_quality["no2"])
        self.set_label("so2", value=air_quality["so2"])
        self.set_label("pm2.5", value=air_quality["pm2_5"])
        self.set_label("pm10", value=air_quality["pm10"])
        self.set_label("epa", summary=lo(US_EPA_INDEX[air_quality["us-epa-index"]]))
        self.set_label("defra", summary=get_defra_index(air_quality["gb-defra-index"]))
