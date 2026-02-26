"""
desktop/ui/windows/login_window.py
Login screen — centred card with username/password.
"""

from PyQt6.QtCore import Qt, QSize # type: ignore
from PyQt6.QtWidgets import ( # type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QSpacerItem, QSizePolicy,
)

from desktop.ui.theme import (
    ACCENT, SMOKE, CHARCOAL, SILVER, WHITE, SNOW,
    heading_font, body_font, SPACING_MD, SPACING_LG, SPACING_XL,
)
from desktop.ui.widgets import (
    primary_button, muted_label, Card, error_dialog,
)
from desktop.api_client import api


class LoginWindow(QWidget):
    """
    Emits no signals — calls on_login_success callback directly
    so the main app can swap to the dashboard.
    """

    def __init__(self, on_login_success: callable):
        super().__init__()
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        self.setMinimumSize(QSize(480, 580))

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)

        # Brand
        brand = QLabel("Horizon Cinemas")
        brand.setFont(heading_font(26))
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet(f"color: {CHARCOAL}; margin-bottom: 4px;")
        outer.addWidget(brand)

        tagline = muted_label("Booking Management System")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(tagline)

        outer.addSpacing(SPACING_LG)

        # Card
        card = Card()
        card.setFixedWidth(380)

        title = QLabel("Staff Login")
        title.setFont(heading_font(16))
        title.setStyleSheet(f"color: {CHARCOAL}; margin-bottom: 8px;")
        card.add(title)

        # Username
        user_lbl = QLabel("Username")
        user_lbl.setFont(body_font(10))
        user_lbl.setStyleSheet(f"color: {SMOKE}; font-weight: 500; margin-top: 8px;")
        card.add(user_lbl)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        card.add(self.username_input)

        # Password
        pass_lbl = QLabel("Password")
        pass_lbl.setFont(body_font(10))
        pass_lbl.setStyleSheet(f"color: {SMOKE}; font-weight: 500; margin-top: 8px;")
        card.add(pass_lbl)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        card.add(self.password_input)

        # Error label (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setFont(body_font(10))
        self.error_label.setStyleSheet(f"color: #DC2626; margin-top: 4px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        card.add(self.error_label)

        # Login button
        card._layout.addSpacing(SPACING_MD)
        self.login_btn = primary_button("Sign In")
        self.login_btn.clicked.connect(self._do_login)
        card.add(self.login_btn)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addSpacing(SPACING_MD)
        footer = muted_label("© 2025 Horizon Cinemas — Internal Use Only")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(footer)

        # Enter key triggers login
        self.password_input.returnPressed.connect(self._do_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_error("Please enter both username and password")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Signing in…")

        try:
            api.login(username, password)
            self.error_label.hide()
            self.on_login_success()
        except Exception as exc:
            detail = ""
            if hasattr(exc, "response"):
                try:
                    detail = exc.response.json().get("detail", str(exc))
                except Exception:
                    detail = str(exc)
            else:
                detail = str(exc)
            self._show_error(detail)
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Sign In")

    def _show_error(self, msg: str):
        self.error_label.setText(msg)
        self.error_label.show()