from __future__ import annotations

from typing import Literal

import httpx
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from atto_weather._self import APP_VERSION

USER_AGENT = f"aescarias/atto-weather {APP_VERSION}"


class WeatherWorkerSignals(QObject):
    errored = Signal(str, int)
    fetched = Signal(object, int)


RequestKind = Literal["forecast", "search"]


class WeatherWorker(QRunnable):
    """Runnable that fetches weather information from https://weatherapi.com"""

    def __init__(self, kind: RequestKind, query: str, api_key: str, lang: str) -> None:
        super().__init__()

        self.signals = WeatherWorkerSignals()

        self.kind = kind
        self.query = query
        self.api_key = api_key
        self.lang = lang

    def run_forecast_request(self) -> httpx.Response:
        return httpx.get(
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

    def run_search_request(self) -> httpx.Response:
        return httpx.get(
            "https://api.weatherapi.com/v1/search.json",
            params={"key": self.api_key, "query": self.query},
            headers={"User-Agent": USER_AGENT},
        )

    @Slot()
    def run(self) -> None:
        if self.kind == "forecast":
            weather_rs = self.run_forecast_request()
        elif self.kind == "search":
            weather_rs = self.run_search_request()
        else:
            raise ValueError(f"Invalid request kind: {self.kind!r}")

        if weather_rs.is_error:
            error = weather_rs.json()["error"]
            self.signals.errored.emit(error["message"], error["code"])
            return

        quota_left = int(weather_rs.headers["x-weatherapi-qpm-left"])
        self.signals.fetched.emit(weather_rs.json(), quota_left)
