from __future__ import annotations

import json
from typing import Any

SETTINGS_FILE = "settings.json"
SECRETS_FILE = "secrets.json"


class Store:
    def __init__(
        self,
        settings: dict[str, Any] | None = None,
        secrets: dict[str, Any] | None = None,
    ) -> None:
        self._settings = settings
        self._secrets = secrets

    @property
    def settings(self) -> dict[str, Any]:
        if self._settings is None:
            raise RuntimeError("Application did not load settings.")
        return self._settings

    @settings.setter
    def settings(self, value: dict[str, Any]) -> None:
        self._settings = value

    @property
    def secrets(self) -> dict[str, Any]:
        if self._secrets is None:
            raise RuntimeError("Application did not load secrets.")

        return self._secrets

    @secrets.setter
    def secrets(self, value: dict[str, Any]) -> None:
        self._secrets = value


store = Store()


def load_settings() -> dict[str, Any]:
    with open(SETTINGS_FILE) as fp:
        return json.load(fp)


def load_secrets() -> dict[str, Any]:
    with open(SECRETS_FILE) as fp:
        return json.load(fp)


def write_settings(settings: dict[str, Any]) -> None:
    with open(SETTINGS_FILE, "w") as fp:
        json.dump(settings, fp, indent=4)


def write_secrets(secrets: dict[str, Any]) -> None:
    with open(SECRETS_FILE, "w") as fp:
        json.dump(secrets, fp, indent=4)
