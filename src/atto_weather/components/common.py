from __future__ import annotations

from typing import Any, Literal, Mapping, cast

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from atto_weather.api.core import Location
from atto_weather.i18n import get_translation as lo
from atto_weather.utils.fields import WeatherField
from atto_weather.utils.text import format_unix_datetime


class LocationLabel(QLabel):
    def __init__(self) -> None:
        super().__init__()

    def update_location(self, location: Location) -> None:
        self.setText(location.full_name)

        lat = round(location.latitude, 5)
        lon = round(location.longitude, 5)

        elements = {
            lo("app.name"): location.name,
            lo("app.region"): location.region,
            lo("app.country"): location.country,
            lo("app.lat_lon"): f"{lat}, {lon}",
        }

        self.setToolTip(
            "<br>".join(f"<b>{key}:</b> {val}\n" for key, val in elements.items() if val)
        )

    def update_time(self, location: Location) -> None:
        date = format_unix_datetime(location.localtime_epoch, location.timezone_id, "date")
        time = format_unix_datetime(location.localtime_epoch, location.timezone_id, "time")

        self.setText(date)
        self.setToolTip(f"{date}\n{time}\n{location.timezone_id}")


class WeatherFieldWidget(QWidget):
    def __init__(self, fields: Mapping[str, WeatherField], type_: Literal["form", "grid"]) -> None:
        super().__init__()

        self.fields = fields

        if type_ == "form":
            self.wgt_layout = QFormLayout()
            populate_form(self.wgt_layout, self.fields)
        elif type_ == "grid":
            self.wgt_layout = QGridLayout()
            populate_grid(self.wgt_layout, self.fields, 3)
        else:
            raise ValueError("Bad argument for layout type: must be 'form' or 'grid'")

        self.wgt_layout.setAlignment(Qt.AlignmentFlag.AlignBaseline)

        self.setLayout(self.wgt_layout)

    def set_label(self, name: str, **values: Any) -> None:
        template = self.fields[name]["template"]
        text = lo(template["value"]) if template.get("tr") else template["value"]

        label = cast(QLabel, self.findChild(QLabel, name + "_label"))
        label.setText(text.format(**values))


class WeatherOverview(QWidget):
    """Widget that displays the time's weather condition, temperature, and a related icon"""

    def __init__(self, *, show_date: bool = False) -> None:
        super().__init__()

        self.show_date = show_date

        self.wgt_layout = QGridLayout()
        self.wgt_layout.setSpacing(10)

        self.date_label = QLabel()

        self.icon_label = QLabel()
        self.temp_label = create_label(weight=QFont.Weight.Bold, point_size=18)
        self.condition_label = create_label(point_size=14)

        self.wgt_layout.addWidget(self.icon_label, 0, 0, 2, 1)
        self.wgt_layout.addWidget(self.temp_label, 0, 1)
        self.wgt_layout.addWidget(self.date_label, 0, 2)
        self.wgt_layout.addWidget(self.condition_label, 1, 1)
        self.wgt_layout.addItem(
            QSpacerItem(50, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum),
            0,
            2,
            1,
            1,
        )
        self.wgt_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(self.wgt_layout)
        self.date_label.setVisible(self.show_date)

    def update_details(
        self, temperature: str, condition: str, icon: QPixmap, date: str | None = None
    ) -> None:
        self.icon_label.setPixmap(icon)
        self.temp_label.setText(temperature)
        self.condition_label.setText(condition)

        if self.show_date and date:
            self.date_label.setText(date)


def populate_form(layout: QFormLayout, label_map: Mapping[str, WeatherField]) -> None:
    """Prepares a form layout with ``label_map`` so that it can later be populated."""
    for ident, prop in label_map.items():
        ind_label = create_label(lo(prop["label"]), weight=QFont.Weight.Bold)

        val_label = QLabel()
        val_label.setObjectName(ident + "_label")

        layout.addRow(ind_label, val_label)


def populate_grid(layout: QGridLayout, label_map: Mapping[str, WeatherField], columns: int) -> None:
    """Prepares a grid layout with ``label_map`` so that it can later be populated."""
    row, col = 0, 0

    for ident, prop in label_map.items():
        ind_label = create_label(lo(prop["label"]), weight=QFont.Weight.Bold)
        val_label = QLabel()
        val_label.setObjectName(ident + "_label")
        layout.addWidget(ind_label, row, col)
        layout.addWidget(val_label, row + 1, col)

        col += 1
        if col >= columns:
            col = 0
            row += 2


def create_label(
    text: str | None = None,
    *,
    weight: QFont.Weight | None = None,
    point_size: int | None = None,
) -> QLabel:
    """Creates a label with ``text``, a font ``weight``, and a font ``point_size``."""
    label = QLabel(text)
    font = label.font()
    if weight is not None:
        font.setWeight(weight)
    if point_size is not None:
        font.setPointSize(point_size)
    label.setFont(font)
    return label


def get_weather_icon(code: int, is_day: bool) -> QPixmap:
    """Returns the day/night (``is_day``) weather icon associated with ``code``"""

    if is_day:
        return QPixmap(f":/day_icons/{code}.png").scaled(64, 64)
    return QPixmap(f":/night_icons/{code}.png").scaled(64, 64)
