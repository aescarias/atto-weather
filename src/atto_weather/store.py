from __future__ import annotations

import json
from pathlib import Path

from atto_weather.utils.settings import Secrets, Settings

SETTINGS_FILE = Path("settings.json")
SECRETS_FILE = Path("secrets.json")


class Store:
    def __init__(
        self,
        settings: Settings | None = None,
        secrets: Secrets | None = None,
    ) -> None:
        self._settings = settings
        self._secrets = secrets

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            raise RuntimeError("Application did not load settings.")

        return self._settings

    @settings.setter
    def settings(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def secrets(self) -> Secrets:
        if self._secrets is None:
            raise RuntimeError("Application did not load secrets.")

        return self._secrets

    @secrets.setter
    def secrets(self, secrets: Secrets) -> None:
        self._secrets = secrets


store = Store()


def load_settings() -> Settings:
    with open(SETTINGS_FILE) as fp:
        return json.load(fp)


def load_secrets() -> Secrets:
    with open(SECRETS_FILE) as fp:
        return json.load(fp)


def write_settings(settings: Settings) -> None:
    with open(SETTINGS_FILE, "w") as fp:
        json.dump(settings, fp, indent=4)


def write_secrets(secrets: Secrets) -> None:
    with open(SECRETS_FILE, "w") as fp:
        json.dump(secrets, fp, indent=4)
