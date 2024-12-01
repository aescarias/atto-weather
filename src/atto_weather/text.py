from __future__ import annotations

from typing import Any, Literal

from atto_weather.i18n import get_translation as lo
from atto_weather.store import store
from PySide6.QtCore import QDateTime, QTimeZone


def get_temperature(celsius: int, fahrenheit: int) -> dict[str, Any]:
    if store.settings["temperature"] == "fahrenheit":
        output = {"value": fahrenheit, "unit": "F"}
    else:
        output = {"value": celsius, "unit": "C"}

    if store.settings["round_temp_values"]:
        output["value"] = round(output["value"])

    return output


def get_distance(km: int, mi: int, *, speed: bool = False) -> dict[str, Any]:
    if store.settings["distance"] == "mi":
        output = {"distance": mi, "unit": "mi"}
    else:
        output = {"distance": km, "unit": "km"}

    if speed:
        output["speed"] = output.pop("distance")
        output["unit"] += "/h"

    return output


def get_height(mm: int, in_: int) -> dict[str, Any]:
    if store.settings["height"] == "in":
        return {"height": in_, "unit": "in"}

    return {"height": mm, "unit": "mm"}


def get_pressure(mbar: int, inhg: int) -> dict[str, Any]:
    if store.settings["pressure"] == "inhg":
        return {"pressure": inhg, "unit": "inHg"}

    return {"pressure": mbar, "unit": "mbar"}


def get_human_bool(boolean: bool) -> str:
    return lo("app.yes") if boolean else lo("app.no")


def format_datetime(
    epoch: int, timezone: str | Literal["UTC"], part: Literal["date", "time"]
) -> str:
    if timezone == "UTC":
        date = QDateTime.fromSecsSinceEpoch(epoch, QTimeZone.Initialization.UTC)
    else:
        date = QDateTime.fromSecsSinceEpoch(epoch, QTimeZone(timezone.encode()))

    if part == "date":
        return date.toString("dddd, MMMM dd, yyyy")
    elif part == "time":
        return date.toString("h:mm AP")
