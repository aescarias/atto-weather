from typing import Literal, TypeAlias, TypedDict

from atto_weather.i18n import get_language_map
from typing_extensions import NotRequired


class Settings(TypedDict):
    language: str
    temperature: Literal["celsius", "fahrenheit"]
    distance: Literal["km", "mi"]
    pressure: Literal["mbar", "inhg"]
    height: Literal["mm", "in"]
    round_temp_values: bool


class Secrets(TypedDict):
    weatherapi: str


DEFAULT_SETTINGS = Settings(
    language="en",
    temperature="celsius",
    distance="km",
    pressure="mbar",
    height="mm",
    round_temp_values=True,
)


class BaseUISetting(TypedDict):
    label: str
    """The localizable identifier for this field."""


class SelectUISetting(BaseUISetting):
    kind: Literal["select"]

    options: dict[str, str]
    """A mapping of option values to their localizable string identifier."""

    options_preloc: NotRequired[bool]
    """Whether the options have been already localized."""


class CheckUISetting(BaseUISetting):
    kind: Literal["check"]


class PasswordUISetting(BaseUISetting):
    kind: Literal["password"]


UISetting: TypeAlias = "SelectUISetting | CheckUISetting | PasswordUISetting"

SETTINGS_FIELDS: dict[str, UISetting] = {
    "language": {
        "label": "settings.language",
        "kind": "select",
        "options": get_language_map(),
        "options_preloc": True,
    },
    "temperature": {
        "label": "settings.temperature.label",
        "kind": "select",
        "options": {
            "celsius": "settings.temperature.celsius",
            "fahrenheit": "settings.temperature.fahrenheit",
        },
    },
    "pressure": {
        "label": "settings.pressure.label",
        "kind": "select",
        "options": {
            "mbar": "settings.pressure.millibars",
            "inhg": "settings.pressure.inhg",
        },
    },
    "height": {
        "label": "settings.height.label",
        "kind": "select",
        "options": {
            "mm": "settings.height.millimeters",
            "in": "settings.height.inches",
        },
    },
    "distance": {
        "label": "settings.distance.label",
        "kind": "select",
        "options": {
            "km": "settings.distance.kilometers",
            "mi": "settings.distance.miles",
        },
    },
    "round_temp_values": {"label": "settings.round_temp_values", "kind": "check"},
}

SECRETS_FIELDS: dict[str, UISetting] = {
    "weatherapi": {"label": "settings.weather_api_key", "kind": "password"}
}
