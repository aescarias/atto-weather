from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TypedDict

import tomli

logging.basicConfig()

LOGGER = logging.getLogger(__name__)

LANG_PATH = Path("languages")


class InstalledLanguages(TypedDict):
    main: dict[str, Any] | None
    fallback: dict[str, Any] | None


class LanguageError(Exception):
    """Exception raised for anything related to the localizer"""

    pass


installed_languages = InstalledLanguages(main=None, fallback=None)


def load_language(lang: str) -> dict[str, Any]:
    """Loads a language file with code ``lang`` into memory"""
    lang_file = Path(LANG_PATH / f"{lang}.toml")
    return tomli.loads(lang_file.read_text("utf-8-sig"))


def get_language_map() -> dict[str, str]:
    """Returns a map of all available language codes to their respective names"""
    languages = {}

    for code in LANG_PATH.glob("*.toml"):
        locale = tomli.loads(code.read_text("utf-8-sig"))

        languages[code.stem] = locale["self"]["language"]

    return languages


def set_language(main: str, fallback: str = "en") -> None:
    """Installs language ``main`` with a ``fallback`` for use with the localizer."""
    try:
        installed_languages["main"] = load_language(main)
    except FileNotFoundError:
        LOGGER.warning(
            f"Requested language {main!r} is not available. Falling back to {fallback!r}"
        )
        installed_languages["main"] = None

    try:
        installed_languages["fallback"] = load_language(fallback)
    except FileNotFoundError:
        raise LanguageError("No fallback language available.")


def get_translation(identifier: str) -> str:
    """Returns the localized value of ``identifier`` (or its fallback if not available)"""

    main_i18n = installed_languages["main"]
    if main_i18n is None:
        main_i18n = {}
        LOGGER.warning("No language installed. Using fallback.")

    fallback = installed_languages["fallback"]
    if fallback is None:
        raise LanguageError("No fallback language available.")

    main_name = main_i18n["self"]["language"]
    fb_name = fallback["self"]["language"]

    for part in identifier.split("."):
        main_i18n = main_i18n.get(part)  # pyright: ignore[reportOptionalMemberAccess]
        fallback = fallback.get(part)  # pyright: ignore[reportOptionalMemberAccess]

        if main_i18n is None:
            LOGGER.warning(
                f"No translation available for string {identifier!r} in lang {main_name!r}. Falling back to {fb_name}."
            )

            main_i18n = fallback
            if fallback is None:
                LOGGER.error(
                    f"Unable to provide translation for string {identifier!r}. Will use empty string!"
                )
                return ""

    return main_i18n  # pyright: ignore[reportReturnType]
