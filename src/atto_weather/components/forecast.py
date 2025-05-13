from __future__ import annotations

from atto_weather.api.core import Astronomy, ForecastDay, ForecastHour
from atto_weather.components.common import WeatherFieldWidget
from atto_weather.components.current import CurrentWeatherWidget
from atto_weather.i18n import get_translation as lo
from atto_weather.utils.fields import (
    ASTRONOMY_FIELDS,
    DAILY_FORECAST_FIELDS,
    HOURLY_FORECAST_FIELDS,
    MOON_PHASE,
    estimate_uv_index,
)
from atto_weather.utils.text import (
    format_am_pm,
    format_boolean,
    format_distance,
    format_height,
    format_speed,
    format_temperature,
)


class HourlyForecastWidget(WeatherFieldWidget):
    """Widget that contains details about the forecast for a specific hour"""

    def __init__(self) -> None:
        super().__init__(HOURLY_FORECAST_FIELDS, "form")

    def update_details(self, hour_forecast: ForecastHour) -> None:
        # Both current weather and hourly forecast use the same labels.
        # Hourly forecast includes two additional ones though and removes
        # the 'air quality' label as it's not included in the API response (free plan)
        CurrentWeatherWidget.update_details(self, hour_forecast, _aqi=False)  # pyright: ignore[reportArgumentType]

        self.set_label(
            "will_it_rain",
            value=format_boolean(hour_forecast.will_it_rain),
            chance=hour_forecast.chance_of_rain,
        )
        self.set_label(
            "will_it_snow",
            value=format_boolean(hour_forecast.will_it_snow),
            chance=hour_forecast.chance_of_snow,
        )


class DailyForecastWidget(WeatherFieldWidget):
    """Widget that contains details about the forecast for an entire day"""

    def __init__(self) -> None:
        super().__init__(DAILY_FORECAST_FIELDS, "form")

    def update_details(self, day_forecast: ForecastDay) -> None:
        self.set_label(
            "min_max_temp",
            mintemp=format_temperature(day_forecast.min_temperature),
            maxtemp=format_temperature(day_forecast.max_temperature),
        )
        self.set_label(
            "max_wind",
            speed=format_speed(day_forecast.max_wind_speed),
        )
        self.set_label("precipitation", height=format_height(day_forecast.total_precipitation))
        self.set_label("snowfall", height=day_forecast.total_snowfall_cm)
        self.set_label("avg_visibility", distance=format_distance(day_forecast.avg_visibility))
        self.set_label(
            "will_it_rain",
            value=format_boolean(day_forecast.will_it_rain),
            chance=day_forecast.chance_of_rain,
        )
        self.set_label(
            "will_it_snow",
            value=format_boolean(day_forecast.will_it_snow),
            chance=day_forecast.chance_of_snow,
        )
        self.set_label(
            "uv_index",
            index=day_forecast.uv_index,
            summary=estimate_uv_index(day_forecast.uv_index),
        )


class AstronomyWidget(WeatherFieldWidget):
    """Widget that contains details about astronomical events for this day"""

    def __init__(self) -> None:
        super().__init__(ASTRONOMY_FIELDS, "grid")

    def update_details(self, astro: Astronomy) -> None:
        # According to the docs, these values should be provided in
        # 'hh:mm ap' format. e.g. "4:00 PM".
        self.set_label("sunrise", value=format_astro_value(astro.sunrise))
        self.set_label("sunset", value=format_astro_value(astro.sunset))
        self.set_label("moonrise", value=format_astro_value(astro.moonrise))
        self.set_label("moonset", value=format_astro_value(astro.moonset))

        self.set_label("moon_phase", phase=lo(MOON_PHASE[astro.moon_phase]))
        self.set_label("moon_illum", illum=astro.moon_illumination)


def format_astro_value(timestr: str) -> str:
    try:
        return format_am_pm(timestr)
    except ValueError:
        # the API likely returned a value such as "no moonrise"
        return lo("app.not_applicable")
