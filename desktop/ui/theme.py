"""
desktop/ui/theme.py
───────────────────
Design system: colours, fonts, spacing, and the global QSS stylesheet.

Fonts:
  - Manrope  → headings, titles, navigation
  - Inter       → body text, labels, inputs

Palette:
  - White       #FFFFFF   — backgrounds
  - Snow        #F7F8FA   — secondary backgrounds, cards
  - Silver      #E5E7EB   — borders, dividers
  - Smoke       #9CA3AF   — placeholder text, muted labels
  - Slate       #4B5563   — secondary text
  - Charcoal    #1F2937   — primary text
  - Black       #111827   — headings
  - Accent      #2563EB   — buttons, links, highlights (blue-600)
  - AccentHover #1D4ED8   — button hover (blue-700)
  - AccentLight #EFF6FF   — accent tint for selected rows etc.
  - Danger      #DC2626   — cancel, errors
  - DangerHover #B91C1C
  - Success     #059669   — confirmed badges
"""

from pathlib import Path
from PyQt6.QtGui import QFontDatabase, QFont # type: ignore
from PyQt6.QtWidgets import QApplication # type: ignore

# Colour Palette
WHITE       = "#FFFFFF"
SNOW        = "#F7F8FA"
SILVER      = "#E5E7EB"
SMOKE       = "#9CA3AF"
SLATE       = "#4B5563"
CHARCOAL    = "#1F2937"
BLACK       = "#111827"

ACCENT      = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
ACCENT_LIGHT = "#EFF6FF"

DANGER      = "#DC2626"
DANGER_HOVER = "#B91C1C"
SUCCESS     = "#059669"

# Font loading
FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

_fonts_loaded = False


def load_fonts():
    """
    Load Manrope and Inter from the local fonts directory.
    Call once at app startup. Supports .ttf, .otf and .woff2 files.
    Falls back to system fonts if the files aren't present.
    """
    global _fonts_loaded
    if _fonts_loaded:
        return
    _fonts_loaded = True

    if not FONTS_DIR.exists():
        return

    for font_file in FONTS_DIR.rglob("*"):
        if font_file.suffix.lower() in (".ttf", ".otf"):
            QFontDatabase.addApplicationFont(str(font_file))


def heading_font(size: int = 16, bold: bool = True) -> QFont:
    """Return a Manrope font for headings."""
    f = QFont("Manrope", size)
    if bold:
        f.setBold(True)
    return f


def body_font(size: int = 11) -> QFont:
    """Return an Inter font for body text."""
    return QFont("Inter", size)


# Spacing / Sizing constants
RADIUS      = "6px"
RADIUS_LG   = "10px"
SPACING_XS  = 4
SPACING_SM  = 8
SPACING_MD  = 16
SPACING_LG  = 24
SPACING_XL  = 32

INPUT_HEIGHT = "38px"
BTN_HEIGHT   = "40px"

# Global QSS
GLOBAL_QSS = f"""
/* Base */
QMainWindow, QDialog, QWidget {{
    background-color: {WHITE};
    color: {CHARCOAL};
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 11pt;
}}

/* Labels */
QLabel {{
    color: {CHARCOAL};
    background: transparent;
}}

QLabel[heading="true"] {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-size: 18pt;
    font-weight: 700;
    color: {BLACK};
}}

QLabel[subheading="true"] {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-size: 13pt;
    font-weight: 600;
    color: {CHARCOAL};
}}

QLabel[muted="true"] {{
    color: {SMOKE};
    font-size: 10pt;
}}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {{
    background-color: {WHITE};
    border: 1px solid {SILVER};
    border-radius: {RADIUS};
    padding: 6px 12px;
    min-height: {INPUT_HEIGHT};
    color: {CHARCOAL};
    font-size: 11pt;
    selection-background-color: {ACCENT_LIGHT};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus {{
    border: 1.5px solid {ACCENT};
    outline: none;
}}

QLineEdit:disabled, QSpinBox:disabled {{
    background-color: {SNOW};
    color: {SMOKE};
}}

QLineEdit[echoMode="2"] {{
    lineedit-password-character: 9679;
}}

/* Combo box */
QComboBox {{
    background-color: {WHITE};
    border: 1px solid {SILVER};
    border-radius: {RADIUS};
    padding: 6px 12px;
    min-height: {INPUT_HEIGHT};
    color: {CHARCOAL};
    font-size: 11pt;
}}

QComboBox:focus {{
    border: 1.5px solid {ACCENT};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid {SILVER};
    border-top-right-radius: {RADIUS};
    border-bottom-right-radius: {RADIUS};
}}

QComboBox QAbstractItemView {{
    background-color: {WHITE};
    border: 1px solid {SILVER};
    selection-background-color: {ACCENT_LIGHT};
    selection-color: {CHARCOAL};
    outline: 0;
}}

/* Buttons */
QPushButton {{
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 11pt;
    font-weight: 600;
    border-radius: {RADIUS};
    padding: 8px 20px;
    min-height: {BTN_HEIGHT};
    border: none;
}}

QPushButton[primary="true"] {{
    background-color: {ACCENT};
    color: {WHITE};
}}

QPushButton[primary="true"]:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton[primary="true"]:pressed {{
    background-color: #1E40AF;
}}

QPushButton[secondary="true"] {{
    background-color: {SNOW};
    color: {CHARCOAL};
    border: 1px solid {SILVER};
}}

QPushButton[secondary="true"]:hover {{
    background-color: {SILVER};
}}

QPushButton[danger="true"] {{
    background-color: {DANGER};
    color: {WHITE};
}}

QPushButton[danger="true"]:hover {{
    background-color: {DANGER_HOVER};
}}

QPushButton:disabled {{
    background-color: {SNOW};
    color: {SMOKE};
    border: 1px solid {SILVER};
}}

/* Radio Buttons & Checkboxes */
QRadioButton, QCheckBox {{
    spacing: 8px;
    font-size: 11pt;
    color: {CHARCOAL};
}}

QRadioButton::indicator, QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: {WHITE};
    alternate-background-color: {SNOW};
    gridline-color: {SILVER};
    border: 1px solid {SILVER};
    border-radius: {RADIUS};
    selection-background-color: {ACCENT_LIGHT};
    selection-color: {CHARCOAL};
    font-size: 10pt;
}}

QHeaderView::section {{
    background-color: {SNOW};
    color: {CHARCOAL};
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-weight: 600;
    font-size: 10pt;
    padding: 8px 12px;
    border: none;
    border-bottom: 2px solid {SILVER};
    border-right: 1px solid {SILVER};
}}

QTableWidget::item {{
    padding: 6px 12px;
}}

/* Scroll bars */
QScrollBar:vertical {{
    background: {SNOW};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {SILVER};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {SMOKE};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {SNOW};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {SILVER};
    border-radius: 4px;
    min-width: 30px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {SILVER};
    border-radius: {RADIUS};
    background: {WHITE};
    margin-top: -1px;
}}

QTabBar::tab {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-weight: 600;
    font-size: 10pt;
    padding: 10px 24px;
    background: {SNOW};
    color: {SLATE};
    border: 1px solid {SILVER};
    border-bottom: none;
    border-top-left-radius: {RADIUS};
    border-top-right-radius: {RADIUS};
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: {WHITE};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}

QTabBar::tab:hover:!selected {{
    background: {WHITE};
    color: {CHARCOAL};
}}

/* Group boxes */
QGroupBox {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-weight: 600;
    font-size: 11pt;
    color: {CHARCOAL};
    border: 1px solid {SILVER};
    border-radius: {RADIUS};
    margin-top: 12px;
    padding-top: 20px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    background-color: {WHITE};
}}

/* Status bar */
QStatusBar {{
    background-color: {SNOW};
    color: {SLATE};
    font-size: 9pt;
    border-top: 1px solid {SILVER};
}}

/* Message boxes */
QMessageBox {{
    background-color: {WHITE};
}}

QMessageBox QLabel {{
    color: {CHARCOAL};
    font-size: 11pt;
}}

/* Text edit / plain text */
QTextEdit, QPlainTextEdit {{
    background-color: {WHITE};
    border: 1px solid {SILVER};
    border-radius: {RADIUS};
    padding: 8px;
    color: {CHARCOAL};
    font-size: 10pt;
}}
"""