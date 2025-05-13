from typing import Mapping, TypedDict

from typing_extensions import NotRequired

from atto_weather.i18n import get_translation as lo


class WeatherFieldTemplate(TypedDict):
    value: str
    """Python-style template which is later populated by its corresponding values.
    
    If ``tr`` is True, then this property is the localizable identifier that 
    contains the template."""

    tr: NotRequired[bool]
    """Whether the template is loaded from a language file. Defaults to False."""


class WeatherField(TypedDict):
    label: str
    """The localizable identifier for this property."""
    template: WeatherFieldTemplate
    """The Python-style template that is later populated by its corresponding values."""


def estimate_cloud_cover(cover: int) -> str:
    tenths = cover // 10
    if tenths == 0:
        return lo("weather.cloud_cover.clear")
    elif 1 <= tenths <= 3:
        return lo("weather.cloud_cover.few_clouds")
    elif 4 <= tenths <= 5:
        return lo("weather.cloud_cover.scattered_clouds")
    elif 6 <= tenths <= 9:
        return lo("weather.cloud_cover.broken_clouds")
    elif tenths == 10:
        return lo("weather.cloud_cover.overcast")

    raise ValueError("Cloud cover out of range")


def get_defra_index(index: int) -> str:
    if 0 <= index <= 3:
        typ_ = lo("air_quality.defra.low")
    elif 4 <= index <= 6:
        typ_ = lo("air_quality.defra.moderate")
    elif 7 <= index <= 9:
        typ_ = lo("air_quality.defra.high")
    elif index == 10:
        typ_ = lo("air_quality.defra.very_high")
    else:
        raise ValueError("DEFRA index out of range")

    return f"{typ_} ({UK_DEFRA_BANDS[index]})"


def estimate_uv_index(index: float) -> str:
    if 0 <= index < 3:
        return lo("weather.uv_index.low")
    elif 3 <= index < 6:
        return lo("weather.uv_index.moderate")
    elif 6 <= index < 8:
        return lo("weather.uv_index.high")
    elif 8 <= index <= 10:
        return lo("weather.uv_index.very_high")
    elif 10 < index <= 11:
        return lo("weather.uv_index.extreme")

    raise ValueError("UV index out of range")


# shorthand -> lo. identifier
POINT16_COMPASS = {
    "N": "point16.north",
    "E": "point16.east",
    "S": "point16.south",
    "W": "point16.west",
    "NE": "point16.northeast",
    "SE": "point16.southeast",
    "SW": "point16.southwest",
    "NW": "point16.northwest",
    "NNE": "point16.north_northeast",
    "ENE": "point16.east_northeast",
    "ESE": "point16.east_southeast",
    "SSE": "point16.south_southeast",
    "SSW": "point16.south_southwest",
    "WSW": "point16.west_southwest",
    "WNW": "point16.west_northwest",
    "NNW": "point16.north_northwest",
}

CURRENT_WEATHER_FIELDS: Mapping[str, WeatherField] = {
    "feels_like": {"label": "weather.feels_like", "template": {"value": "{feels_like}"}},
    "windchill": {"label": "weather.windchill", "template": {"value": "{windchill}"}},
    "heat_index": {"label": "weather.heat_index", "template": {"value": "{heat_index}"}},
    "dew_point": {"label": "weather.dew_point", "template": {"value": "{dew_point}"}},
    "wind_speed": {
        "label": "weather.wind_speed",
        "template": {"value": "{speed} @ {degree}° {shorthand}\n({direction})"},
    },
    "wind_gust": {"label": "weather.wind_gust", "template": {"value": "{speed}"}},
    "humidity": {"label": "weather.humidity", "template": {"value": "{humidity}%"}},
    "precipitation": {"label": "weather.precipitation", "template": {"value": "{height}"}},
    "pressure": {"label": "weather.pressure", "template": {"value": "{pressure}"}},
    "cloud_cover": {
        "label": "weather.cloud_cover.label",
        "template": {"value": "{cloud}% ({summary})"},
    },
    "visibility": {"label": "weather.visibility", "template": {"value": "{distance}"}},
    "uv_index": {"label": "weather.uv_index.label", "template": {"value": "{index} ({summary})"}},
    "air_quality": {"label": "air_quality.label", "template": {"value": "{summary}"}},
}

AIR_QUALITY_FIELDS: Mapping[str, WeatherField] = {
    "co": {"label": "air_quality.co", "template": {"value": "{value} μg/m³"}},
    "o3": {"label": "air_quality.o3", "template": {"value": "{value} μg/m³"}},
    "no2": {"label": "air_quality.no2", "template": {"value": "{value} μg/m³"}},
    "so2": {"label": "air_quality.so2", "template": {"value": "{value} μg/m³"}},
    "pm2.5": {"label": "air_quality.pm2_5", "template": {"value": "{value} μg/m³"}},
    "pm10": {"label": "air_quality.pm10", "template": {"value": "{value} μg/m³"}},
    "epa": {"label": "air_quality.epa.label", "template": {"value": "{summary}"}},
    "defra": {"label": "air_quality.defra.label", "template": {"value": "{summary}"}},
}

ASTRONOMY_FIELDS: Mapping[str, WeatherField] = {
    "sunrise": {"label": "astronomy.sunrise", "template": {"value": "{value}"}},
    "sunset": {"label": "astronomy.sunset", "template": {"value": "{value}"}},
    "moonrise": {"label": "astronomy.moonrise", "template": {"value": "{value}"}},
    "moonset": {"label": "astronomy.moonset", "template": {"value": "{value}"}},
    "moon_phase": {
        "label": "astronomy.moon_phase.label",
        "template": {"value": "{phase}"},
    },
    "moon_illum": {
        "label": "astronomy.moon_illumination",
        "template": {"value": "{illum}%"},
    },
}

RAIN_SNOW_FIELDS: Mapping[str, WeatherField] = {
    "will_it_rain": {
        "label": "forecast.will_it_rain",
        "template": {"tr": True, "value": "forecast.will_it_rain_template"},
    },
    "will_it_snow": {
        "label": "forecast.will_it_snow",
        "template": {"tr": True, "value": "forecast.will_it_snow_template"},
    },
}

DAILY_FORECAST_FIELDS: Mapping[str, WeatherField] = {
    "min_max_temp": {
        "label": "forecast.min_max_temp",
        "template": {"value": "{mintemp} - {maxtemp}"},
    },
    "max_wind": {"label": "forecast.max_wind", "template": {"value": "{speed}"}},
    "precipitation": {"label": "weather.precipitation", "template": {"value": "{height}"}},
    "snowfall": {"label": "forecast.snowfall", "template": {"value": "{height} cm"}},
    "avg_visibility": {
        "label": "forecast.avg_visibility",
        "template": {"value": "{distance}"},
    },
    **RAIN_SNOW_FIELDS,
    "uv_index": {
        "label": "weather.uv_index.label",
        "template": {"value": "{index} ({summary})"},
    },
}

_hour_fields = CURRENT_WEATHER_FIELDS.copy()
_hour_fields.pop("air_quality")

HOURLY_FORECAST_FIELDS: Mapping[str, WeatherField] = {
    **_hour_fields,
    **RAIN_SNOW_FIELDS,
}

UK_DEFRA_BANDS = {
    1: "0-11 µgm⁻³",
    2: "12-23 µgm⁻³",
    3: "24-35 µgm⁻³",
    4: "36-41 µgm⁻³",
    5: "42-47 µgm⁻³",
    6: "48-53 µgm⁻³",
    7: "54-58 µgm⁻³",
    8: "59-64 µgm⁻³",
    9: "65-70 µgm⁻³",
    10: ">71 µgm⁻³",
}

US_EPA_INDEX = {
    1: "air_quality.epa.good",
    2: "air_quality.epa.moderate",
    3: "air_quality.epa.unhealthy_sensitive",
    4: "air_quality.epa.unhealthy",
    5: "air_quality.epa.very_unhealthy",
    6: "air_quality.epa.hazardous",
}

MOON_PHASE = {
    "New Moon": "astronomy.moon_phase.new_moon",
    "Waxing Crescent": "astronomy.moon_phase.waxing_crescent",
    "First Quarter": "astronomy.moon_phase.first_quarter",
    "Waxing Gibbous": "astronomy.moon_phase.waxing_gibbous",
    "Full Moon": "astronomy.moon_phase.full_moon",
    "Waning Gibbous": "astronomy.moon_phase.waning_gibbous",
    "Last Quarter": "astronomy.moon_phase.last_quarter",
    "Waning Crescent": "astronomy.moon_phase.waning_crescent",
}
