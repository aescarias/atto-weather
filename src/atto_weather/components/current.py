from __future__ import annotations

from atto_weather.api.core import AirQuality, CurrentWeather
from atto_weather.components.common import WeatherFieldWidget
from atto_weather.i18n import get_translation as lo
from atto_weather.utils.fields import (
    AIR_QUALITY_FIELDS,
    CURRENT_WEATHER_FIELDS,
    POINT16_COMPASS,
    US_EPA_INDEX,
    estimate_cloud_cover,
    estimate_uv_index,
    get_defra_index,
)
from atto_weather.utils.text import (
    format_distance,
    format_height,
    format_pressure,
    format_speed,
    format_temperature,
)


class CurrentWeatherWidget(WeatherFieldWidget):
    """Widget that contains details about the current weather"""

    def __init__(self) -> None:
        super().__init__(CURRENT_WEATHER_FIELDS, "grid")

    def update_details(self, current: CurrentWeather, *, _aqi: bool = True) -> None:
        self.set_label("feels_like", feels_like=format_temperature(current.temperature))
        self.set_label("windchill", windchill=format_temperature(current.windchill))
        self.set_label("heat_index", heat_index=format_temperature(current.heat_index))
        self.set_label("dew_point", dew_point=format_temperature(current.dew_point))
        self.set_label(
            "wind_speed",
            speed=format_speed(current.wind_speed),
            degree=current.wind_degree,
            shorthand=current.wind_direction,
            direction=lo(POINT16_COMPASS[current.wind_direction]),
        )
        self.set_label("wind_gust", speed=format_speed(current.gust_speed))
        self.set_label("humidity", humidity=current.humidity)
        self.set_label("precipitation", height=format_height(current.precipitation))
        self.set_label("pressure", pressure=format_pressure(current.pressure))
        self.set_label(
            "cloud_cover",
            cloud=current.cloud_cover,
            summary=estimate_cloud_cover(current.cloud_cover),
        )
        self.set_label("visibility", distance=format_distance(current.visibility))
        self.set_label(
            "uv_index", index=current.uv_index, summary=estimate_uv_index(current.uv_index)
        )

        if _aqi:
            self.set_label(
                "air_quality", summary=lo(US_EPA_INDEX[current.air_quality.us_epa_index])
            )


class AirQualityWidget(WeatherFieldWidget):
    """Widget that contains details about the air quality at this moment"""

    def __init__(self) -> None:
        super().__init__(AIR_QUALITY_FIELDS, "grid")

    def update_details(self, air_quality: AirQuality) -> None:
        self.set_label("co", value=air_quality.co)
        self.set_label("o3", value=air_quality.o3)
        self.set_label("no2", value=air_quality.no2)
        self.set_label("so2", value=air_quality.so2)
        self.set_label("pm2.5", value=air_quality.pm2_5)
        self.set_label("pm10", value=air_quality.pm10)
        self.set_label("epa", summary=lo(US_EPA_INDEX[air_quality.us_epa_index]))
        self.set_label("defra", summary=get_defra_index(air_quality.gb_defra_index))
