"""
desktop/ui/windows/main_window.py
Main application shell after login.
Left sidebar navigation + stacked content panel.
Sidebar items are role-gated.
"""

from PyQt6.QtCore import Qt, QSize # type: ignore
from PyQt6.QtGui import QFont # type: ignore
from PyQt6.QtWidgets import ( # type: ignore
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel,
    QPushButton, QFrame, QSizePolicy, QSpacerItem,
)

from desktop.ui.theme import (
    ACCENT, ACCENT_LIGHT, WHITE, SNOW, SILVER, CHARCOAL, SMOKE, BLACK,
    heading_font, body_font, SPACING_SM, SPACING_MD, SPACING_LG,
)
from desktop.api_client import api


class SidebarButton(QPushButton):
    """Navigation button in the sidebar."""

    def __init__(self, text: str, icon_char: str = ""):
        display = f"  {icon_char}   {text}" if icon_char else f"  {text}"
        super().__init__(display)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self.setFont(body_font(11))
        self._update_style(False)

    def _update_style(self, checked: bool):
        if checked:
            self.setStyleSheet(
                f"QPushButton {{ text-align: left; padding-left: 20px; "
                f"background-color: {ACCENT_LIGHT}; color: {ACCENT}; "
                f"border: none; border-left: 3px solid {ACCENT}; "
                f"font-weight: 600; border-radius: 0; }}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton {{ text-align: left; padding-left: 20px; "
                f"background-color: transparent; color: {CHARCOAL}; "
                f"border: none; font-weight: 500; border-radius: 0; }}"
                f"QPushButton:hover {{ background-color: {SNOW}; }}"
            )

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._update_style(checked)


class MainWindow(QWidget):

    def __init__(self, on_logout: callable):
        super().__init__()
        self.on_logout = on_logout
        self._nav_buttons: list[SidebarButton] = []
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(
            f"QFrame {{ background-color: {WHITE}; border-right: 1px solid {SILVER}; }}"
        )
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Brand header
        brand_frame = QFrame()
        brand_frame.setFixedHeight(72)
        brand_frame.setStyleSheet(f"border-bottom: 1px solid {SILVER}; background: {WHITE};")
        bl = QVBoxLayout(brand_frame)
        bl.setContentsMargins(20, 12, 20, 12)
        brand = QLabel("Horizon Cinemas")
        brand.setFont(heading_font(14))
        brand.setStyleSheet(f"color: {CHARCOAL}; border: none;")
        bl.addWidget(brand)
        cinema_lbl = QLabel(api.cinema_name)
        cinema_lbl.setFont(body_font(9))
        cinema_lbl.setStyleSheet(f"color: {SMOKE}; border: none;")
        bl.addWidget(cinema_lbl)
        sb_layout.addWidget(brand_frame)

        sb_layout.addSpacing(SPACING_SM)

        # Section label
        def section_label(text):
            lbl = QLabel(f"  {text}")
            lbl.setFont(body_font(9))
            lbl.setStyleSheet(
                f"color: {SMOKE}; font-weight: 600; letter-spacing: 1px; "
                f"padding: 12px 20px 4px 20px; border: none;"
            )
            return lbl

        # Nav items (role-gated)
        role = api.role

        sb_layout.addWidget(section_label("BOOKING"))
        self._add_nav(sb_layout, "Film Listings", "🎬")
        self._add_nav(sb_layout, "New Booking", "🎟")
        self._add_nav(sb_layout, "Cancellation", "✕")

        if role in ("admin", "manager"):
            sb_layout.addWidget(section_label("ADMINISTRATION"))
            self._add_nav(sb_layout, "Manage Films", "📽")
            self._add_nav(sb_layout, "Manage Listings", "📋")
            self._add_nav(sb_layout, "Reports", "📊")

        if role == "manager":
            sb_layout.addWidget(section_label("MANAGEMENT"))
            self._add_nav(sb_layout, "Manage Cinemas", "🏢")

        sb_layout.addStretch(1)

        # User info + logout
        user_frame = QFrame()
        user_frame.setStyleSheet(f"border-top: 1px solid {SILVER}; background: {SNOW};")
        uf_layout = QVBoxLayout(user_frame)
        uf_layout.setContentsMargins(16, 12, 16, 12)

        name_lbl = QLabel(api.display_name)
        name_lbl.setFont(body_font(10))
        name_lbl.setStyleSheet(f"color: {CHARCOAL}; font-weight: 600; border: none;")
        uf_layout.addWidget(name_lbl)

        role_lbl = QLabel(api.role.replace("_", " ").title())
        role_lbl.setFont(body_font(9))
        role_lbl.setStyleSheet(f"color: {SMOKE}; border: none;")
        uf_layout.addWidget(role_lbl)

        logout_btn = QPushButton("Sign Out")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFont(body_font(10))
        logout_btn.setStyleSheet(
            f"QPushButton {{ color: {SMOKE}; background: transparent; "
            f"border: 1px solid {SILVER}; border-radius: 4px; padding: 6px; "
            f"margin-top: 8px; font-weight: 500; }}"
            f"QPushButton:hover {{ background: {WHITE}; color: {CHARCOAL}; }}"
        )
        logout_btn.clicked.connect(self._do_logout)
        uf_layout.addWidget(logout_btn)

        sb_layout.addWidget(user_frame)
        root.addWidget(sidebar)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {SNOW};")
        root.addWidget(self.stack, 1)

        # Lazy-load pages on first nav click
        self._pages: dict[str, QWidget] = {}

        # Select first item
        if self._nav_buttons:
            self._nav_buttons[0].click()

    def _add_nav(self, layout, label: str, icon: str = ""):
        btn = SidebarButton(label, icon)
        btn.clicked.connect(lambda checked, l=label: self._navigate(l))
        layout.addWidget(btn)
        self._nav_buttons.append(btn)

    def _navigate(self, label: str):
        # Toggle buttons
        for btn in self._nav_buttons:
            btn.setChecked(btn.text().strip().endswith(label))

        # Lazy-load page
        if label not in self._pages:
            page = self._create_page(label)
            self._pages[label] = page
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self._pages[label])

    def _create_page(self, label: str) -> QWidget:
        """Create the appropriate view widget for a nav label."""
        from desktop.ui.windows.booking_staff.film_listings import FilmListingsView
        from desktop.ui.windows.booking_staff.new_booking import NewBookingView
        from desktop.ui.windows.booking_staff.cancellation import CancellationView

        if label == "Film Listings":
            return FilmListingsView()
        elif label == "New Booking":
            return NewBookingView()
        elif label == "Cancellation":
            return CancellationView()

        if api.role in ("admin", "manager"):
            from desktop.ui.windows.admin.manage_films import ManageFilmsView
            from desktop.ui.windows.admin.manage_listings import ManageListingsView
            from desktop.ui.windows.admin.reports import ReportsView

            if label == "Manage Films":
                return ManageFilmsView()
            elif label == "Manage Listings":
                return ManageListingsView()
            elif label == "Reports":
                return ReportsView()

        if api.role == "manager":
            from desktop.ui.windows.manager.manage_cinemas import ManageCinemasView

            if label == "Manage Cinemas":
                return ManageCinemasView()

        # Fallback
        placeholder = QLabel(f"{label}\n\nComing soon…")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(body_font(14))
        return placeholder

    def _do_logout(self):
        api.logout()
        self.on_logout()