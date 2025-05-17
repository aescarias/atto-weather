from __future__ import annotations

from typing import Literal

from PySide6.QtCore import QDateTime, QLocale, Qt, QTimeZone

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


def format_unix_datetime(
    unix: int, timezone: str | Literal["UTC"], part: Literal["date", "time"]
) -> str:
    if timezone == "UTC":
        date = QDateTime.fromSecsSinceEpoch(unix, QTimeZone.Initialization.UTC)
    else:
        date = QDateTime.fromSecsSinceEpoch(unix, QTimeZone(timezone.encode()))

    locale = QLocale(
        QLocale.codeToLanguage(store.settings["language"], QLocale.LanguageCodeType.ISO639Part1)
    )

    if part == "date":
        return locale.toString(date.date())
    elif part == "time":
        if store.settings.get("time_24_hour"):
            return locale.toString(date.time(), "hh:mm")

        return locale.toString(date.time(), "hh:mm ap")


def format_am_pm(timestr: str) -> str:
    date = QDateTime.fromString(timestr, "hh:mm ap")

    if not date.isValid():
        raise ValueError(f"Invalid time string: {timestr!r}")

    return format_unix_datetime(date.toSecsSinceEpoch(), date.timeZone().id().toStdString(), "time")


def format_iso8601(datestr: str, part: Literal["date", "time"]) -> str:
    date = QDateTime.fromString(datestr, Qt.DateFormat.ISODate)

    if not date.isValid():
        raise ValueError(f"Invalid date string: {datestr!r}")

    return format_unix_datetime(date.toSecsSinceEpoch(), date.timeZone().id().toStdString(), part)


CODES = {
    2006: "api_errors.key_invalid",
    2007: "api_errors.exceeded_quota",
    2008: "api_errors.key_disabled",
    2009: "api_errors.missing_access",
    9999: "api_errors.internal_error",
}


def format_api_error(
    code: int, fallback_message: str, *, template: str = "api_errors.error_format"
) -> str:
    if (localizer := CODES.get(code)) is not None:
        return lo(template).format(code=code, message=lo(localizer))

    return lo(template).format(code=code, message=fallback_message)
