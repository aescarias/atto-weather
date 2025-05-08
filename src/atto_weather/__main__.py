from __future__ import annotations

from typing import Never

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from atto_weather import icons_rc  # noqa: F401 -- resource file
from atto_weather._self import APP_VERSION
from atto_weather.app import AttoWeather
from atto_weather.i18n import set_language
from atto_weather.store import load_secrets, load_settings, store, write_settings
from atto_weather.utils.settings import DEFAULT_SETTINGS
from atto_weather.windows.setup_wizard import SetupWizard


def run_wizard_if_setup_incomplete() -> None:
    try:
        store.secrets = load_secrets()
        secrets_loaded = True
    except FileNotFoundError:
        secrets_loaded = False

    locations = store.settings.get("locations", [])

    if secrets_loaded and bool(locations):
        return

    wizard = SetupWizard()
    code = wizard.exec()

    if code == QDialog.DialogCode.Rejected:
        raise SystemExit()


def run() -> Never:
    app = QApplication()
    app.setWindowIcon(QPixmap(":/app/app_icon.png"))

    # https://stackoverflow.com/a/1552105
    if app.platformName() == "windows":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"aescarias.atto.weather.{APP_VERSION}"
        )

    try:
        store.settings = load_settings()
    except FileNotFoundError:
        store.settings = DEFAULT_SETTINGS
        write_settings(store.settings)

    set_language(store.settings["language"])
    run_wizard_if_setup_incomplete()

    window = AttoWeather()
    window.show()

    raise SystemExit(app.exec())


if __name__ == "__main__":
    run()
