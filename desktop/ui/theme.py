"""
desktop/ui/theme.py
───────────────────
Design system: colours, fonts, spacing, and the global QSS stylesheet.
Modern BookMyShow-inspired aesthetic with vibrant accent and elegant neutrals.

Fonts:
  - Manrope  → headings, titles, navigation
  - Inter       → body text, labels, inputs

Palette:
  - White       #FFFFFF   — primary backgrounds
  - Offwhite    #FAFBFC   — secondary backgrounds
  - Surface     #F3F4F6   — cards, panels
  - Divider     #E5E7EB   — borders, separators
  - Muted       #9CA3AF   — placeholder text, secondary labels
  - Slate       #4B5563   — secondary text
  - Text        #1F2937   — primary text
  - Heading     #111827   — headings
  - Primary     #EE2A7B   — brand accent (vibrant magenta/pink)
  - PrimaryDark #C2155A   — primary hover
  - PrimaryLight #FFB3D9  — accent tint for highlights
  - Success     #10B981   — confirmed, positive actions
  - Warning     #F59E0B   — warnings, caution
  - Danger      #EF4444   — errors, cancellations
"""

from pathlib import Path
from PyQt6.QtGui import QFontDatabase, QFont # type: ignore
from PyQt6.QtWidgets import QApplication # type: ignore

# Colour Palette - BookMyShow Inspired
WHITE       = "#FFFFFF"
OFFWHITE    = "#FAFBFC"
SURFACE     = "#F3F4F6"
DIVIDER     = "#E5E7EB"
MUTED       = "#9CA3AF"
SLATE       = "#4B5563"
TEXT        = "#1F2937"
HEADING     = "#111827"

PRIMARY     = "#EE2A7B"  # Vibrant magenta/pink
PRIMARY_DARK = "#C2155A"  # Primary hover/pressed
PRIMARY_LIGHT = "#FFB3D9"  # Light accent for tints

SUCCESS     = "#10B981"
WARNING     = "#F59E0B"
DANGER      = "#EF4444"

# Legacy aliases for compatibility
ACCENT = PRIMARY
ACCENT_HOVER = PRIMARY_DARK
ACCENT_LIGHT = PRIMARY_LIGHT
CHARCOAL = TEXT
BLACK = HEADING
SILVER = DIVIDER
SMOKE = MUTED
SNOW = SURFACE

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


# Spacing / Sizing constants - Modern compact spacing
RADIUS      = "8px"
RADIUS_LG   = "12px"
SPACING_XS  = 4
SPACING_SM  = 8
SPACING_MD  = 16
SPACING_LG  = 24
SPACING_XL  = 32
SPACING_2XL = 48

INPUT_HEIGHT = "40px"
BTN_HEIGHT   = "44px"

# Global QSS - Modern BookMyShow-inspired styling
GLOBAL_QSS = f"""
/* Base */
QMainWindow, QDialog, QWidget {{
    background-color: {OFFWHITE};
    color: {TEXT};
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 11pt;
}}

/* Labels */
QLabel {{
    color: {TEXT};
    background: transparent;
}}

QLabel[heading="true"] {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-size: 20pt;
    font-weight: 700;
    color: {HEADING};
    letter-spacing: -0.5px;
}}

QLabel[subheading="true"] {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-size: 14pt;
    font-weight: 600;
    color: {TEXT};
}}

QLabel[muted="true"] {{
    color: {MUTED};
    font-size: 10pt;
}}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {{
    background-color: {WHITE};
    border: 1px solid {DIVIDER};
    border-radius: {RADIUS};
    padding: 8px 12px;
    min-height: {INPUT_HEIGHT};
    color: {TEXT};
    font-size: 11pt;
    selection-background-color: {PRIMARY_LIGHT};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus {{
    border: 2px solid {PRIMARY};
    outline: none;
    background-color: {WHITE};
}}

QLineEdit:disabled, QSpinBox:disabled {{
    background-color: {SURFACE};
    color: {MUTED};
}}

QLineEdit[echoMode="2"] {{
    lineedit-password-character: 9679;
}}

/* Combo box */
QComboBox {{
    background-color: {WHITE};
    border: 1px solid {DIVIDER};
    border-radius: {RADIUS};
    padding: 8px 12px;
    min-height: {INPUT_HEIGHT};
    color: {TEXT};
    font-size: 11pt;
    font-weight: 500;
}}

QComboBox:focus {{
    border: 2px solid {PRIMARY};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid {DIVIDER};
    border-top-right-radius: {RADIUS};
    border-bottom-right-radius: {RADIUS};
}}

QComboBox QAbstractItemView {{
    background-color: {WHITE};
    border: 1px solid {DIVIDER};
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {HEADING};
    outline: 0;
}}

/* Buttons */
QPushButton {{
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 11pt;
    font-weight: 600;
    border-radius: {RADIUS};
    padding: 10px 24px;
    min-height: {BTN_HEIGHT};
    border: none;
    letter-spacing: 0.2px;
}}

QPushButton[primary="true"] {{
    background-color: {PRIMARY};
    color: {WHITE};
}}

QPushButton[primary="true"]:hover {{
    background-color: {PRIMARY_DARK};
}}

QPushButton[primary="true"]:pressed {{
    background-color: #A01550;
}}

QPushButton[secondary="true"] {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {DIVIDER};
}}

QPushButton[secondary="true"]:hover {{
    background-color: {DIVIDER};
    border: 1px solid {MUTED};
}}

QPushButton[secondary="true"]:pressed {{
    background-color: {DIVIDER};
}}

QPushButton[danger="true"] {{
    background-color: {DANGER};
    color: {WHITE};
}}

QPushButton[danger="true"]:hover {{
    background-color: #DC2626;
}}

QPushButton[success="true"] {{
    background-color: {SUCCESS};
    color: {WHITE};
}}

QPushButton[success="true"]:hover {{
    background-color: #059669;
}}

QPushButton:disabled {{
    background-color: {SURFACE};
    color: {MUTED};
    border: 1px solid {DIVIDER};
}}

/* Radio Buttons & Checkboxes */
QRadioButton, QCheckBox {{
    spacing: 8px;
    font-size: 11pt;
    color: {TEXT};
}}

QRadioButton::indicator, QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QRadioButton::indicator:checked {{
    background-color: {PRIMARY};
}}

QCheckBox::indicator:checked {{
    background-color: {PRIMARY};
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: {WHITE};
    alternate-background-color: {SURFACE};
    gridline-color: {DIVIDER};
    border: 1px solid {DIVIDER};
    border-radius: {RADIUS};
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {HEADING};
    font-size: 10pt;
}}

QHeaderView::section {{
    background-color: {SURFACE};
    color: {TEXT};
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-weight: 600;
    font-size: 10pt;
    padding: 12px;
    border: none;
    border-bottom: 1px solid {DIVIDER};
    border-right: 1px solid {DIVIDER};
}}

QTableWidget::item {{
    padding: 10px 12px;
}}

/* Scroll bars */
QScrollBar:vertical {{
    background: {OFFWHITE};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {DIVIDER};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {OFFWHITE};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {DIVIDER};
    border-radius: 4px;
    min-width: 30px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {DIVIDER};
    border-radius: {RADIUS};
    background: {WHITE};
    margin-top: -1px;
}}

QTabBar::tab {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-weight: 600;
    font-size: 10pt;
    padding: 10px 24px;
    background: {SURFACE};
    color: {MUTED};
    border: 1px solid {DIVIDER};
    border-bottom: none;
    border-top-left-radius: {RADIUS};
    border-top-right-radius: {RADIUS};
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: {WHITE};
    color: {PRIMARY};
    border-bottom: 2px solid {PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background: {OFFWHITE};
    color: {TEXT};
}}

/* Group boxes */
QGroupBox {{
    font-family: "Manrope", "Segoe UI", sans-serif;
    font-weight: 600;
    font-size: 11pt;
    color: {TEXT};
    border: 1px solid {DIVIDER};
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
    background-color: {SURFACE};
    color: {SLATE};
    font-size: 9pt;
    border-top: 1px solid {DIVIDER};
}}

/* Message boxes */
QMessageBox {{
    background-color: {WHITE};
}}

QMessageBox QLabel {{
    color: {TEXT};
    font-size: 11pt;
}}

/* Text edit / plain text */
QTextEdit, QPlainTextEdit {{
    background-color: {WHITE};
    border: 1px solid {DIVIDER};
    border-radius: {RADIUS};
    padding: 8px;
    color: {TEXT};
    font-size: 10pt;
}}
"""
