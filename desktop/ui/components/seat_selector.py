"""
desktop/ui/components/seat_selector.py
────────────────────────────────────────
Interactive seat selection component for booking flow.
Displays a visual seat map with color-coded status (available, booked, selected).
"""

from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtWidgets import ( # type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QMessageBox,
)
from PyQt6.QtGui import QColor, QFont # type: ignore

from desktop.ui.theme import (
    PRIMARY, SUCCESS, DANGER, MUTED, TEXT, HEADING, DIVIDER, SURFACE, WHITE,
    heading_font, body_font, SPACING_MD, SPACING_LG, RADIUS,
)


class SeatButton(QPushButton):
    """Individual seat button with visual state management."""
    
    def __init__(self, seat_number: str, is_available: bool = True):
        super().__init__(seat_number)
        self.seat_number = seat_number
        self.is_available = is_available
        self.is_selected = False
        
        self.setFixedSize(48, 48)
        self.setCursor(Qt.CursorShape.PointingHandCursor if is_available else Qt.CursorShape.ArrowCursor)
        self.setFont(body_font(9))
        self.setEnabled(is_available)
        
        self._update_style()
        self.clicked.connect(self._on_click)
    
    def _update_style(self):
        """Update button appearance based on state."""
        if not self.is_available:
            # Booked seat
            self.setStyleSheet(
                f"QPushButton {{"
                f"background-color: #E5E7EB; color: {MUTED}; border: 1px solid {DIVIDER};"
                f"border-radius: {RADIUS}; font-weight: 600;"
                f"}}"
            )
        elif self.is_selected:
            # Selected seat
            self.setStyleSheet(
                f"QPushButton {{"
                f"background-color: {PRIMARY}; color: white; border: 2px solid {PRIMARY};"
                f"border-radius: {RADIUS}; font-weight: 700;"
                f"}}"
            )
        else:
            # Available seat
            self.setStyleSheet(
                f"QPushButton {{"
                f"background-color: {SURFACE}; color: {TEXT}; border: 1px solid {DIVIDER};"
                f"border-radius: {RADIUS}; font-weight: 600;"
                f"}}"
                f"QPushButton:hover {{"
                f"background-color: {PRIMARY}; color: white; border: 1px solid {PRIMARY};"
                f"}}"
            )
    
    def set_selected(self, selected: bool):
        """Set seat selection state."""
        if not self.is_available:
            return
        self.is_selected = selected
        self._update_style()
    
    def _on_click(self):
        """Handle seat click."""
        if self.is_available:
            self.set_selected(not self.is_selected)


class SeatSelector(QWidget):
    """Interactive seat selection component."""
    
    seats_changed = pyqtSignal(list)  # Emits list of selected seat numbers
    
    def __init__(self, total_seats: int = 120, booked_seats: list = None, vip_seats: list = None):
        super().__init__()
        self.total_seats = total_seats
        self.booked_seats = set(booked_seats or [])
        self.vip_seats = set(vip_seats or [])
        self.selected_seats: set = set()
        self.seat_buttons: dict = {}
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the seat selector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)
        
        # Header
        header_row = QHBoxLayout()
        title = QLabel("Select Your Seats")
        title.setFont(heading_font(16, bold=True))
        title.setStyleSheet(f"color: {HEADING}; border: none;")
        header_row.addWidget(title)
        header_row.addStretch()
        layout.addLayout(header_row)
        
        # Legend
        legend = QHBoxLayout()
        legend.setSpacing(SPACING_LG)
        
        legend_items = [
            ("Available", SURFACE, DIVIDER),
            ("Selected", PRIMARY, PRIMARY),
            ("Booked", "#E5E7EB", DIVIDER),
        ]
        
        for label, bg_color, border_color in legend_items:
            item = QFrame()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(8, 0, 8, 0)
            item_layout.setSpacing(8)
            
            indicator = QFrame()
            indicator.setFixedSize(20, 20)
            indicator.setStyleSheet(
                f"background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 4px;"
            )
            
            label_widget = QLabel(label)
            label_widget.setFont(body_font(9))
            label_widget.setStyleSheet(f"color: {TEXT}; border: none;")
            
            item_layout.addWidget(indicator)
            item_layout.addWidget(label_widget)
            
            legend.addWidget(item)
        
        legend.addStretch()
        layout.addLayout(legend)
        
        # Seat grid
        grid_container = QFrame()
        grid_container.setStyleSheet(f"background-color: {WHITE}; border: 1px solid {DIVIDER}; border-radius: {RADIUS};")
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        
        # Generate seat layout (typical cinema layout)
        rows = 10
        cols = 12
        seat_num = 1
        
        for row in range(rows):
            for col in range(cols):
                seat_id = f"{chr(65 + row)}{col + 1}"  # A1, A2, B1, B2, etc.
                is_available = seat_id not in self.booked_seats
                
                seat_btn = SeatButton(seat_id, is_available)
                self.seat_buttons[seat_id] = seat_btn
                seat_btn.clicked.connect(self._on_seat_changed)
                
                grid_layout.addWidget(seat_btn, row, col)
        
        layout.addWidget(grid_container)
        
        # Summary
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel("0 seats selected")
        self.summary_label.setFont(body_font(11))
        self.summary_label.setStyleSheet(f"color: {TEXT}; font-weight: 600; border: none;")
        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.setMaximumWidth(140)
        self.clear_btn.setProperty("secondary", True)
        self.clear_btn.clicked.connect(self._clear_selection)
        summary_layout.addWidget(self.clear_btn)
        
        layout.addLayout(summary_layout)
    
    def _on_seat_changed(self):
        """Handle seat selection change."""
        self.selected_seats.clear()
        for seat_id, btn in self.seat_buttons.items():
            if btn.is_selected:
                self.selected_seats.add(seat_id)
        
        # Update summary
        count = len(self.selected_seats)
        self.summary_label.setText(
            f"{count} seat{'s' if count != 1 else ''} selected"
        )
        
        self.seats_changed.emit(sorted(list(self.selected_seats)))
    
    def _clear_selection(self):
        """Clear all selected seats."""
        for btn in self.seat_buttons.values():
            if btn.is_selected:
                btn.set_selected(False)
        
        self._on_seat_changed()
    
    def get_selected_seats(self) -> list:
        """Get list of currently selected seat numbers."""
        return sorted(list(self.selected_seats))
    
    def set_seat_booked(self, seat_id: str):
        """Mark a seat as booked."""
        if seat_id in self.seat_buttons:
            btn = self.seat_buttons[seat_id]
            btn.is_available = False
            btn.setEnabled(False)
            btn._update_style()
    
    def reset_selection(self):
        """Reset all selections."""
        self.selected_seats.clear()
        for btn in self.seat_buttons.values():
            btn.is_selected = False
            btn._update_style()
        self.summary_label.setText("0 seats selected")
