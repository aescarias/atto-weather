from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Protocol, TypeVar

from typing_extensions import Self


class SupportsFromDict(Protocol):
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self: ...


T = TypeVar("T", bound=SupportsFromDict)


def map_to_dataclass(cls: type[T], data: dict[str, Any]) -> T:
    if not is_dataclass(cls):
        raise ValueError("object not dataclass")

    mapped: dict[str, Any] = {}

    for field in fields(cls):
        if field.name in data:
            mapped[field.name] = data[field.name]

    return cls(**data)


@dataclass
class Location:
    latitude: float
    longitude: float
    name: str
    region: str
    country: str
    timezone_id: str
    localtime_epoch: int
    localtime_formatted: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        data = deepcopy(data)

        data["timezone_id"] = data.pop("tz_id")
        data["latitude"] = data.pop("lat")
        data["longitude"] = data.pop("lon")
        data["localtime_formatted"] = data.pop("localtime")

        return map_to_dataclass(cls, data)

    @property
    def full_name(self) -> str:
        return ", ".join(comp for comp in [self.name, self.region, self.country] if comp)


@dataclass
class Temperature:
    celsius: float
    fahrenheit: float


@dataclass
class Distance:
    miles: float
    kilometers: float


@dataclass
class Speed:
    miles_per_hour: float
    kilometers_per_hour: float


@dataclass
class Pressure:
    millibars: float
    inches_hg: float


@dataclass
class Height:
    millimeters: float
    inches: float


@dataclass
class AirQuality:
    co: float
    o3: float
    no2: float
    so2: float
    pm2_5: float
    pm10: float
    us_epa_index: int
    gb_defra_index: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        data = deepcopy(data)

        data["us_epa_index"] = data.pop("us-epa-index")
        data["gb_defra_index"] = data.pop("gb-defra-index")

        return map_to_dataclass(cls, data)


@dataclass
class Condition:
    text: str
    icon: str
    code: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return map_to_dataclass(cls, data)


@dataclass
class CurrentWeather:
    last_updated_formatted: str
    last_updated_epoch: int
    temperature: Temperature
    feels_like: Temperature
    windchill: Temperature
    heat_index: Temperature
    dew_point: Temperature
    visibility: Distance
    condition: Condition
    wind_speed: Speed
    wind_degree: int
    wind_direction: str
    pressure: Pressure
    precipitation: Height
    humidity: int
    cloud_cover: int
    is_day: bool
    uv_index: float
    gust_speed: Speed
    air_quality: AirQuality

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            last_updated_formatted=data["last_updated"],
            last_updated_epoch=data["last_updated_epoch"],
            temperature=Temperature(data["temp_c"], data["temp_f"]),
            feels_like=Temperature(data["feelslike_c"], data["feelslike_f"]),
            windchill=Temperature(data["windchill_c"], data["windchill_f"]),
            heat_index=Temperature(data["heatindex_c"], data["heatindex_f"]),
            dew_point=Temperature(data["dewpoint_c"], data["dewpoint_f"]),
            visibility=Distance(data["vis_miles"], data["vis_km"]),
            condition=Condition.from_dict(data["condition"]),
            wind_speed=Speed(data["wind_mph"], data["wind_kph"]),
            wind_degree=data["wind_degree"],
            wind_direction=data["wind_dir"],
            pressure=Pressure(data["pressure_mb"], data["pressure_in"]),
            precipitation=Height(data["precip_mm"], data["precip_in"]),
            humidity=data["humidity"],
            cloud_cover=data["cloud"],
            is_day=bool(data["is_day"]),
            uv_index=data["uv"],
            gust_speed=Speed(data["gust_mph"], data["gust_kph"]),
            air_quality=AirQuality.from_dict(data["air_quality"]),
        )


@dataclass
class Forecast:
    date_formatted: str
    date_epoch: int
    day: ForecastDay
    astronomy: Astronomy
    hours: list[ForecastHour]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            date_formatted=data["date"],
            date_epoch=data["date_epoch"],
            day=ForecastDay.from_dict(data["day"]),
            astronomy=Astronomy.from_dict(data["astro"]),
            hours=[ForecastHour.from_dict(hour) for hour in data["hour"]],
        )


@dataclass
class ForecastDay:
    max_temperature: Temperature
    min_temperature: Temperature
    avg_temperature: Temperature
    max_wind_speed: Speed
    total_precipitation: Height
    total_snowfall_cm: float
    avg_visibility: Distance
    avg_humidity: int
    condition: Condition
    uv_index: float
    will_it_rain: bool
    will_it_snow: bool
    chance_of_rain: int
    chance_of_snow: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            max_temperature=Temperature(data["maxtemp_c"], data["maxtemp_f"]),
            min_temperature=Temperature(data["mintemp_c"], data["mintemp_f"]),
            avg_temperature=Temperature(data["avgtemp_c"], data["avgtemp_f"]),
            max_wind_speed=Speed(data["maxwind_mph"], data["maxwind_kph"]),
            total_precipitation=Height(data["totalprecip_mm"], data["totalprecip_in"]),
            total_snowfall_cm=data["totalsnow_cm"],
            avg_visibility=Distance(data["avgvis_miles"], data["avgvis_km"]),
            avg_humidity=data["avghumidity"],
            condition=Condition.from_dict(data["condition"]),
            uv_index=data["uv"],
            will_it_rain=bool(data["daily_will_it_rain"]),
            will_it_snow=bool(data["daily_will_it_snow"]),
            chance_of_rain=data["daily_chance_of_rain"],
            chance_of_snow=data["daily_chance_of_snow"],
        )


@dataclass
class ForecastHour:
    time_epoch: int
    time_formatted: str
    temperature: Temperature
    condition: Condition
    wind_speed: Speed
    wind_degree: int
    wind_direction: str
    pressure: Pressure
    precipitation: Height
    snowfall_cm: int
    humidity: int
    cloud_cover: int
    feels_like: Temperature
    windchill: Temperature
    heat_index: Temperature
    dew_point: Temperature
    will_it_rain: bool
    will_it_snow: bool
    chance_of_rain: int
    chance_of_snow: int
    is_day: int
    visibility: Distance
    gust_speed: Speed
    uv_index: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            time_epoch=data["time_epoch"],
            time_formatted=data["time"],
            temperature=Temperature(data["temp_c"], data["temp_f"]),
            condition=Condition.from_dict(data["condition"]),
            wind_speed=Speed(data["wind_mph"], data["wind_kph"]),
            wind_degree=data["wind_degree"],
            wind_direction=data["wind_dir"],
            pressure=Pressure(data["pressure_mb"], data["pressure_in"]),
            precipitation=Height(data["precip_mm"], data["precip_in"]),
            snowfall_cm=data["snow_cm"],
            humidity=data["humidity"],
            cloud_cover=data["cloud"],
            feels_like=Temperature(data["feelslike_c"], data["feelslike_f"]),
            windchill=Temperature(data["windchill_c"], data["windchill_f"]),
            heat_index=Temperature(data["heatindex_c"], data["heatindex_f"]),
            dew_point=Temperature(data["dewpoint_c"], data["dewpoint_f"]),
            will_it_rain=bool(data["will_it_rain"]),
            will_it_snow=bool(data["will_it_snow"]),
            is_day=bool(data["is_day"]),
            visibility=Distance(data["vis_miles"], data["vis_km"]),
            chance_of_rain=data["chance_of_rain"],
            chance_of_snow=data["chance_of_snow"],
            gust_speed=Speed(data["gust_mph"], data["gust_kph"]),
            uv_index=data["uv"],
        )


@dataclass
class Astronomy:
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: int
    is_moon_up: bool
    is_sun_up: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        data = deepcopy(data)

        data["is_moon_up"] = bool(data.pop("is_moon_up"))
        data["is_sun_up"] = bool(data.pop("is_sun_up"))

        return map_to_dataclass(cls, data)


@dataclass
class WeatherInfo:
    location: Location
    current: CurrentWeather
    forecasts: list[Forecast]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            location=Location.from_dict(data["location"]),
            current=CurrentWeather.from_dict(data["current"]),
            forecasts=[
                Forecast.from_dict(forecast) for forecast in data["forecast"]["forecastday"]
            ],
        )
