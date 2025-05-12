from __future__ import annotations

from typing import Literal

from PySide6.QtCore import QDateTime, QLocale, QTimeZone

from atto_weather.api.core import Distance, Height, Pressure, Speed, Temperature
from atto_weather.i18n import get_translation as lo
from atto_weather.store import store


def format_temperature(temp: Temperature) -> str:
    if store.settings["temperature"] == "fahrenheit":
        value, unit = temp.fahrenheit, "F"
    else:
        value, unit = temp.celsius, "C"

    if store.settings["round_temp_values"]:
        value = round(value)

    return f"{value} °{unit}"


def format_distance(dist: Distance) -> str:
    if store.settings["distance"] == "mi":
        return f"{dist.miles} mi"

    return f"{dist.kilometers} km"


def format_speed(speed: Speed) -> str:
    if store.settings["distance"] == "mi":
        return f"{speed.miles_per_hour} mi/h"

    return f"{speed.kilometers_per_hour} km/h"


def format_height(height: Height) -> str:
    if store.settings["height"] == "in":
        return f"{height.inches} in"

    return f"{height.millimeters} mm"


def format_pressure(pressure: Pressure) -> str:
    if store.settings["pressure"] == "inhg":
        return f"{pressure.inches_hg} inHg"

    return f"{pressure.millibars} mbar"


def format_boolean(boolean: bool) -> str:
    return lo("app.yes") if boolean else lo("app.no")


def format_datetime(
    epoch: int, timezone: str | Literal["UTC"], part: Literal["date", "time-12", "time-24"]
) -> str:
    if timezone == "UTC":
        date = QDateTime.fromSecsSinceEpoch(epoch, QTimeZone.Initialization.UTC)
    else:
        date = QDateTime.fromSecsSinceEpoch(epoch, QTimeZone(timezone.encode()))

    locale = QLocale(
        QLocale.codeToLanguage(store.settings["language"], QLocale.LanguageCodeType.ISO639Part1)
    )

    if part == "date":
        return locale.toString(date.date())
    elif part == "time-12":
        return locale.toString(date.time(), "hh:mm ap")
    elif part == "time-24":
        return locale.toString(date.time(), "hh:mm")
