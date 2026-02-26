"""
desktop/ui/windows/admin/reports.py
Admin reports: monthly revenue, bookings per listing, top films, staff leaderboard.
"""

from datetime import date
from PyQt6.QtCore import Qt # type: ignore
from PyQt6.QtWidgets import ( # type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QSpinBox, QLabel, QFrame, QScrollArea,
)

from desktop.ui.theme import (
    SPACING_MD, SPACING_LG, SPACING_XL, PRIMARY, SUCCESS, TEXT, MUTED, HEADING, OFFWHITE, WHITE, SURFACE, DIVIDER,
    heading_font, body_font,
)
from desktop.ui.widgets import (
    heading_label, primary_button, separator, error_dialog, Card,
)
from desktop.api_client import api


class ReportsView(QWidget):

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Hero section
        hero = QFrame()
        hero.setStyleSheet(
            f"background: linear-gradient(135deg, {PRIMARY}, #EE2A7B); padding: 40px;"
        )
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(SPACING_LG, SPACING_XL, SPACING_LG, SPACING_XL)
        hero_layout.setSpacing(SPACING_MD)

        hero_title = QLabel("Business Reports")
        hero_title.setFont(heading_font(28, bold=True))
        hero_title.setStyleSheet("color: white; border: none; letter-spacing: -1px;")
        hero_layout.addWidget(hero_title)

        hero_subtitle = QLabel("Analyze revenue, bookings, and performance metrics")
        hero_subtitle.setFont(body_font(12))
        hero_subtitle.setStyleSheet("color: rgba(255,255,255,0.9); border: none; font-weight: 500;")
        hero_layout.addWidget(hero_subtitle)

        layout.addWidget(hero)

        # Main content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {OFFWHITE}; }}")

        content = QWidget()
        content.setStyleSheet(f"background-color: {OFFWHITE};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        content_layout.setSpacing(SPACING_MD)

        # Filters
        filters_card = Card()
        filters = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(date.today().year)
        filters.addWidget(QLabel("Year:"))
        filters.addWidget(self.year_spin)

        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(date.today().month)
        filters.addWidget(QLabel("Month:"))
        filters.addWidget(self.month_spin)

        gen_btn = primary_button("Generate Reports")
        gen_btn.setMinimumWidth(140)
        gen_btn.clicked.connect(self._generate_all)
        filters.addWidget(gen_btn)
        filters.addStretch()
        filters_card.add_layout(filters)
        content_layout.addWidget(filters_card)

        # Tabs
        self.tabs = QTabWidget()
        self.rev_table = self._make_table(["City", "Cinema", "Bookings", "Revenue", "Cancellations", "Cancel Fees"])
        self.tabs.addTab(self.rev_table, "Monthly Revenue")

        self.listing_table = self._make_table(["Film", "Screen", "Cinema", "Start", "End", "Bookings", "Tickets"])
        self.tabs.addTab(self.listing_table, "Bookings per Listing")

        self.top_table = self._make_table(["Film", "Revenue", "Bookings"])
        self.tabs.addTab(self.top_table, "Top Films")

        self.staff_table = self._make_table(["Staff", "Username", "Cinema", "Bookings", "Revenue"])
        self.tabs.addTab(self.staff_table, "Staff Bookings")

        content_layout.addWidget(self.tabs, 1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _make_table(self, headers: list) -> QTableWidget:
        t = QTableWidget()
        t.setAlternatingRowColors(True)
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setStretchLastSection(True)
        t.verticalHeader().setVisible(False)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        return t

    def _fill_table(self, table: QTableWidget, rows: list[list]):
        table.setRowCount(len(rows))
        for r, row_data in enumerate(rows):
            for c, val in enumerate(row_data):
                table.setItem(r, c, QTableWidgetItem(str(val)))

    def _generate_all(self):
        y = self.year_spin.value()
        m = self.month_spin.value()
        try:
            # Revenue
            data = api.report_revenue(y, m)
            self._fill_table(self.rev_table, [
                [d["city_name"], d["cinema_name"], d["total_bookings"],
                 f"£{d['total_revenue']:.2f}", d["cancellations"],
                 f"£{d['cancellation_fees']:.2f}"]
                for d in data
            ])

            # Bookings per listing
            data = api.report_bookings_per_listing()
            self._fill_table(self.listing_table, [
                [d["film_title"], d["screen_number"], d["cinema_name"],
                 d["start_date"], d["end_date"], d["booking_count"], d["tickets_sold"]]
                for d in data
            ])

            # Top films
            data = api.report_top_films(y, m)
            self._fill_table(self.top_table, [
                [d["film_title"], f"£{d['revenue']:.2f}", d["bookings"]]
                for d in data
            ])

            # Staff
            data = api.report_staff_bookings(y, m)
            self._fill_table(self.staff_table, [
                [d["staff_name"], d["username"], d["cinema_name"],
                 d["total_bookings"], f"£{d['total_revenue']:.2f}"]
                for d in data
            ])

        except Exception as e:
            error_dialog(self, str(e))
