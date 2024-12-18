from __future__ import annotations

from typing import Never

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from atto_weather import icons_rc  # noqa: F401
from atto_weather._version import __version__ as app_version
from atto_weather.app import AttoWeather
from atto_weather.i18n import set_language
from atto_weather.store import load_secrets, load_settings, store, write_settings
from atto_weather.windows.creds_required import CredentialsRequiredDialog
from atto_weather.windows.settings import DEFAULT_SETTINGS


def run() -> Never:
    app = QApplication()
    app.setWindowIcon(QPixmap(":/app/app_icon.png"))

    # https://stackoverflow.com/a/1552105
    if app.platformName() == "windows":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"aescarias.atto.weather.{app_version}"
        )

    try:
        store.settings = load_settings()
    except FileNotFoundError:
        store.settings = DEFAULT_SETTINGS
        write_settings(store.settings)

    set_language(store.settings["language"])

    try:
        store.secrets = load_secrets()
    except FileNotFoundError:
        dlg = CredentialsRequiredDialog()

        if dlg.exec() == QDialog.DialogCode.Rejected:
            raise SystemExit()

    window = AttoWeather()
    window.show()

    raise SystemExit(app.exec())


if __name__ == "__main__":
    run()
