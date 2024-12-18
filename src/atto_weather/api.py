from __future__ import annotations

import httpx
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from ._version import __version__ as app_version

USER_AGENT = f"aescarias/atto-weather {app_version}"


class WeatherWorkerSignals(QObject):
    errored = Signal(str, int)
    fetched = Signal(dict)


class WeatherWorker(QRunnable):
    """Runnable that fetches weather information from https://weatherapi.com"""

    def __init__(self, query: str, api_key: str, lang: str) -> None:
        super().__init__()

        self.signals = WeatherWorkerSignals()

        self.query = query
        self.api_key = api_key
        self.lang = lang

    @Slot()
    def run(self) -> None:
        weather_rs = httpx.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={
                "key": self.api_key,
                "q": self.query,
                "days": 3,
                "aqi": "yes",
                "lang": self.lang,
            },
            headers={"User-Agent": USER_AGENT},
        )

        if weather_rs.is_error:
            error = weather_rs.json()["error"]
            self.signals.errored.emit(error["message"], error["code"])
            return

        self.signals.fetched.emit(weather_rs.json())
