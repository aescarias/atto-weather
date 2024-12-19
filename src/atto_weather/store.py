from __future__ import annotations

import json

from atto_weather.utils.settings import Secrets, Settings

SETTINGS_FILE = "settings.json"
SECRETS_FILE = "secrets.json"


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
    def settings(self, value: Settings) -> None:
        self._settings = value

    @property
    def secrets(self) -> Secrets:
        if self._secrets is None:
            raise RuntimeError("Application did not load secrets.")

        return self._secrets

    @secrets.setter
    def secrets(self, value: Secrets) -> None:
        self._secrets = value


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
