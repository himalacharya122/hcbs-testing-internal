"""
desktop/ui/windows/booking_staff/film_listings.py
Film Listing GUI — browse films at a cinema for a chosen date.
Shows film cards with showings, prices, and seat availability.
"""

from datetime import date, timedelta
from PyQt6.QtCore import Qt, QDate # type: ignore
from PyQt6.QtWidgets import ( # type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QComboBox, QDateEdit, QFrame, QSizePolicy,
)

from desktop.ui.theme import (
    ACCENT, ACCENT_LIGHT, WHITE, SNOW, SILVER, CHARCOAL, SMOKE, BLACK, SUCCESS,
    heading_font, body_font, SPACING_SM, SPACING_MD, SPACING_LG,
)
from desktop.ui.widgets import (
    heading_label, subheading_label, muted_label, badge_label,
    primary_button, secondary_button, Card, separator, show_toast,
)
from desktop.api_client import api


class FilmListingsView(QWidget):

    def __init__(self):
        super().__init__()
        self._build_ui()
        self._load_cinemas()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        # Header
        header = QHBoxLayout()
        header.addWidget(heading_label("Film Listings"))
        header.addStretch()

        # Cinema selector
        self.cinema_combo = QComboBox()
        self.cinema_combo.setFixedWidth(260)
        self.cinema_combo.currentIndexChanged.connect(self._on_filters_changed)
        header.addWidget(QLabel("Cinema:"))
        header.addWidget(self.cinema_combo)

        # Date selector
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setMaximumDate(QDate.currentDate().addDays(7))
        self.date_edit.setFixedWidth(140)
        self.date_edit.dateChanged.connect(self._on_filters_changed)
        header.addWidget(QLabel("Date:"))
        header.addWidget(self.date_edit)

        # Nav buttons
        prev_btn = secondary_button("◀  Previous Day")
        prev_btn.setFixedWidth(130)
        prev_btn.clicked.connect(self._prev_day)
        next_btn = secondary_button("Next Day  ▶")
        next_btn.setFixedWidth(130)
        next_btn.clicked.connect(self._next_day)
        header.addWidget(prev_btn)
        header.addWidget(next_btn)

        layout.addLayout(header)
        layout.addWidget(separator())

        # Scrollable film cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(SPACING_MD)
        self.cards_layout.addStretch()

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll, 1)

    def _load_cinemas(self):
        try:
            cinemas = api.get_cinemas()
            self.cinema_combo.blockSignals(True)
            self.cinema_combo.clear()
            for c in cinemas:
                label = f"{c['cinema_name']} ({c['city_name']})" if c.get('city_name') else c['cinema_name']
                self.cinema_combo.addItem(label, c['cinema_id'])

            # Pre-select the user's home cinema
            for i in range(self.cinema_combo.count()):
                if self.cinema_combo.itemData(i) == api.cinema_id:
                    self.cinema_combo.setCurrentIndex(i)
                    break

            self.cinema_combo.blockSignals(False)
            self._load_listings()
        except Exception as e:
            show_toast(self, f"Failed to load cinemas: {e}", success=False)

    def _on_filters_changed(self):
        self._load_listings()

    def _prev_day(self):
        current = self.date_edit.date()
        new_date = current.addDays(-1)
        if new_date >= QDate.currentDate():
            self.date_edit.setDate(new_date)

    def _next_day(self):
        current = self.date_edit.date()
        new_date = current.addDays(1)
        if new_date <= QDate.currentDate().addDays(7):
            self.date_edit.setDate(new_date)

    def _load_listings(self):
        # Clear existing cards
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cinema_id = self.cinema_combo.currentData()
        if not cinema_id:
            return

        target_date = self.date_edit.date().toPyDate().isoformat()

        try:
            listings = api.get_film_listings(cinema_id, target_date)
        except Exception as e:
            show_toast(self, f"Failed to load listings: {e}", success=False)
            return

        if not listings:
            empty = QLabel("No films listed for this cinema on the selected date.")
            empty.setFont(body_font(12))
            empty.setStyleSheet(f"color: {SMOKE}; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.insertWidget(0, empty)
            return

        for film_data in listings:
            card = self._build_film_card(film_data)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _build_film_card(self, data: dict) -> Card:
        card = Card()

        # Title row
        title_row = QHBoxLayout()
        title_lbl = subheading_label(data["title"], 14)
        title_row.addWidget(title_lbl)
        title_row.addStretch()

        if data.get("imdb_rating"):
            rating = badge_label(f"★ {data['imdb_rating']}", "#F59E0B")
            title_row.addWidget(rating)

        genre_badge = badge_label(data["genre"], ACCENT)
        title_row.addWidget(genre_badge)

        age_badge = badge_label(data["age_rating"], CHARCOAL)
        title_row.addWidget(age_badge)

        card.add_layout(title_row)

        # Meta line
        meta_parts = []
        if data.get("duration_display"):
            meta_parts.append(data["duration_display"])
        if data.get("director"):
            meta_parts.append(f"Dir: {data['director']}")
        meta_parts.append(f"Screen {data['screen_number']}")

        meta = muted_label(" · ".join(meta_parts))
        card.add(meta)

        # Description
        if data.get("description"):
            desc = QLabel(data["description"])
            desc.setFont(body_font(10))
            desc.setStyleSheet(f"color: {CHARCOAL}; margin-top: 4px;")
            desc.setWordWrap(True)
            desc.setMaximumHeight(60)
            card.add(desc)

        # Cast
        if data.get("cast_list"):
            cast = muted_label(f"Cast: {data['cast_list']}")
            cast.setWordWrap(True)
            card.add(cast)

        card.add(separator())

        # Showings row
        showings_row = QHBoxLayout()
        showings_row.setSpacing(SPACING_SM)

        show_label = QLabel("Showings:")
        show_label.setFont(body_font(10))
        show_label.setStyleSheet(f"color: {SMOKE}; font-weight: 600;")
        showings_row.addWidget(show_label)

        for s in data.get("showings", []):
            show_time = s["show_time"]
            if isinstance(show_time, str) and len(show_time) > 5:
                show_time = show_time[:5]

            show_widget = QFrame()
            show_widget.setStyleSheet(
                f"background: {SNOW}; border: 1px solid {SILVER}; border-radius: 4px; padding: 4px;"
            )
            sw_layout = QVBoxLayout(show_widget)
            sw_layout.setContentsMargins(12, 6, 12, 6)
            sw_layout.setSpacing(2)

            time_lbl = QLabel(str(show_time))
            time_lbl.setFont(heading_font(12, bold=True))
            time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_lbl.setStyleSheet(f"color: {CHARCOAL}; border: none;")
            sw_layout.addWidget(time_lbl)

            type_lbl = QLabel(s["show_type"].capitalize())
            type_lbl.setFont(body_font(8))
            type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_lbl.setStyleSheet(f"color: {SMOKE}; border: none;")
            sw_layout.addWidget(type_lbl)

            price_lbl = QLabel(f"from £{s['lower_hall_price']:.2f}")
            price_lbl.setFont(body_font(9))
            price_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            price_lbl.setStyleSheet(f"color: {ACCENT}; font-weight: 600; border: none;")
            sw_layout.addWidget(price_lbl)

            showings_row.addWidget(show_widget)

        showings_row.addStretch()
        card.add_layout(showings_row)

        return card