from __future__ import annotations

from typing import Never

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QWidget

from atto_weather import icons_rc  # noqa: F401 -- resource file
from atto_weather._self import APP_VERSION
from atto_weather.app import AttoWeather
from atto_weather.i18n import LanguageError, set_language
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

    if secrets_loaded and locations:
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

    try:
        set_language(store.settings["language"])
    except LanguageError as err:
        QMessageBox.critical(QWidget(), "Error", str(err))
        raise SystemExit(1)

    run_wizard_if_setup_incomplete()

    window = AttoWeather()
    window.show()

    raise SystemExit(app.exec())


if __name__ == "__main__":
    run()
