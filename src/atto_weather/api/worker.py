from __future__ import annotations

import logging
from json import JSONDecodeError
from typing import Literal

import httpx
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from atto_weather._self import APP_VERSION

USER_AGENT = f"aescarias/atto-weather {APP_VERSION}"

LOGGER = logging.getLogger(__name__)


class WeatherWorkerSignals(QObject):
    api_errored = Signal(str, int)
    request_errored = Signal(str, str)
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
                "days": 14,  # max allowed, api should take care of this according to plan
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
        try:
            if self.kind == "forecast":
                weather_rs = self.run_forecast_request()
            elif self.kind == "search":
                weather_rs = self.run_search_request()
            else:
                raise ValueError(f"Invalid request kind: {self.kind!r}")
        except httpx.RequestError as exc:
            LOGGER.exception(exc)
            self.signals.request_errored.emit(exc.__class__.__name__, str(exc))
            return

        if weather_rs.is_error:
            exc = weather_rs.json()["error"]
            self.signals.api_errored.emit(exc["message"], exc["code"])
            return

        quota_left = int(weather_rs.headers["x-weatherapi-qpm-left"])
        try:
            self.signals.fetched.emit(weather_rs.json(), quota_left)
        except JSONDecodeError as exc:
            LOGGER.exception(exc)
            self.signals.request_errored.emit(exc.__class__.__name__, str(exc))
