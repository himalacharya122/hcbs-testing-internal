"""
desktop/ui/windows/booking_staff/new_booking.py
────────────────────────────────────────────────
Booking form: select film → showing → date → seat type → check availability
→ fill customer info → book → show receipt.
"""

from datetime import date
from PyQt6.QtCore import Qt, QDate # type: ignore
from PyQt6.QtWidgets import ( # type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit,
    QRadioButton, QSpinBox, QLineEdit, QButtonGroup, QGroupBox,
    QTextEdit, QScrollArea, QFrame, QSizePolicy,
)

from desktop.ui.theme import (
    PRIMARY, PRIMARY_DARK, PRIMARY_LIGHT, WHITE, OFFWHITE, SURFACE, DIVIDER, TEXT, MUTED, HEADING, SUCCESS, DANGER,
    heading_font, body_font, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_2XL,
)
from desktop.ui.widgets import (
    heading_label, subheading_label, muted_label, primary_button,
    secondary_button, danger_button, Card, separator, form_row,
    labelled_value, show_toast, error_dialog, status_badge,
)
from desktop.api_client import api


class NewBookingView(QWidget):

    def __init__(self):
        super().__init__()
        self._showings_data = []
        self._availability = None
        self._build_ui()
        self._load_cinemas()

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
        hero_layout.setSpacing(SPACING_SM)

        hero_title = QLabel("New Booking")
        hero_title.setFont(heading_font(28, bold=True))
        hero_title.setStyleSheet("color: white; border: none; letter-spacing: -1px;")
        hero_layout.addWidget(hero_title)

        hero_subtitle = QLabel("Step 1: Select Film  •  Step 2: Choose Seats  •  Step 3: Confirm")
        hero_subtitle.setFont(body_font(11))
        hero_subtitle.setStyleSheet("color: rgba(255,255,255,0.85); border: none; font-weight: 500;")
        hero_layout.addWidget(hero_subtitle)

        layout.addWidget(hero)

        # Main content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {OFFWHITE}; }}")

        content = QWidget()
        content.setStyleSheet(f"background-color: {OFFWHITE};")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        self.main_layout.setSpacing(SPACING_MD)

        # Two-column layout: form | receipt
        columns = QHBoxLayout()
        columns.setSpacing(SPACING_LG)

        # Step 1: Cinema & Film selection
        select_card = Card()
        step1_title = subheading_label("Step 1: Select Film", 13)
        select_card.add(step1_title)

        # Left column — booking form
        left = QVBoxLayout()
        left.setSpacing(SPACING_MD)

        self.cinema_combo = QComboBox()
        self.cinema_combo.currentIndexChanged.connect(self._on_cinema_changed)
        select_card.add_layout(form_row("Cinema", self.cinema_combo))

        self.film_combo = QComboBox()
        self.film_combo.currentIndexChanged.connect(self._on_film_changed)
        select_card.add_layout(form_row("Film", self.film_combo))

        self.showing_combo = QComboBox()
        select_card.add_layout(form_row("Showing", self.showing_combo))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setMaximumDate(QDate.currentDate().addDays(7))
        select_card.add_layout(form_row("Date", self.date_edit))

        left.addWidget(select_card)

        # Ticket type
        ticket_card = Card()
        type_group_layout = QHBoxLayout()
        self.seat_type_group = QButtonGroup(self)

        self.rb_lower = QRadioButton("Lower Hall")
        self.rb_upper = QRadioButton("Upper Gallery")
        self.rb_vip = QRadioButton("VIP")
        self.rb_lower.setChecked(True)

        self.seat_type_group.addButton(self.rb_lower, 0)
        self.seat_type_group.addButton(self.rb_upper, 1)
        self.seat_type_group.addButton(self.rb_vip, 2)

        type_group_layout.addWidget(QLabel("Seat Type:"))
        type_group_layout.addWidget(self.rb_lower)
        type_group_layout.addWidget(self.rb_upper)
        type_group_layout.addWidget(self.rb_vip)
        type_group_layout.addStretch()
        ticket_card.add_layout(type_group_layout)

        self.num_tickets = QSpinBox()
        self.num_tickets.setMinimum(1)
        self.num_tickets.setMaximum(20)
        self.num_tickets.setValue(1)
        ticket_card.add_layout(form_row("Tickets", self.num_tickets))

        self.check_btn = primary_button("Check Availability & Price")
        self.check_btn.clicked.connect(self._check_availability)
        ticket_card.add(self.check_btn)

        # Availability result
        self.avail_label = QLabel("")
        self.avail_label.setFont(body_font(11))
        self.avail_label.setWordWrap(True)
        self.avail_label.hide()
        ticket_card.add(self.avail_label)

        left.addWidget(ticket_card)

        # Step 3: Customer info
        customer_card = Card()
        cust_title = subheading_label("Step 3: Customer Details", 13)
        customer_card.add(cust_title)
        customer_card.add(separator())

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        customer_card.add_layout(form_row("Name *", self.name_input))

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone number")
        customer_card.add_layout(form_row("Phone", self.phone_input))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        customer_card.add_layout(form_row("Email", self.email_input))

        customer_card.add(separator())

        # Simulated payment
        self.payment_cb_label = QLabel("Simulate payment (card details not stored)")
        self.payment_cb_label.setFont(body_font(9))
        self.payment_cb_label.setStyleSheet(f"color: {SMOKE};")
        customer_card.add(self.payment_cb_label)

        btn_row = QHBoxLayout()
        self.book_btn = primary_button("Confirm Booking")
        self.book_btn.setEnabled(False)
        self.book_btn.clicked.connect(self._create_booking)
        btn_row.addWidget(self.book_btn)

        self.reset_btn = secondary_button("Reset")
        self.reset_btn.clicked.connect(self._reset_form)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch()

        customer_card.add_layout(btn_row)

        left.addWidget(customer_card)
        left.addStretch()

        # Right column — receipt
        right = QVBoxLayout()
        right.setSpacing(SPACING_MD)

        receipt_title = subheading_label("Booking Receipt", 13)
        right.addWidget(receipt_title)

        self.receipt_card = Card()
        self.receipt_placeholder = muted_label("Receipt will appear here after booking.")
        self.receipt_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.receipt_placeholder.setMinimumHeight(200)
        self.receipt_card.add(self.receipt_placeholder)
        right.addWidget(self.receipt_card)
        right.addStretch()

        columns.addLayout(left, 3)
        columns.addLayout(right, 2)

        self.main_layout.addLayout(columns)
        self.main_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    # Data loading
    def _load_cinemas(self):
        try:
            cinemas = api.get_cinemas()
            self.cinema_combo.blockSignals(True)
            self.cinema_combo.clear()

            # If booking_staff, only show home cinema
            # If admin/manager, show all
            if api.role == "booking_staff":
                cinemas = [c for c in cinemas if c["cinema_id"] == api.cinema_id]

            for c in cinemas:
                label = f"{c['cinema_name']}"
                if c.get('city_name'):
                    label += f"  —  {c['city_name']}"
                self.cinema_combo.addItem(label, c["cinema_id"])

            self.cinema_combo.blockSignals(False)
            self._on_cinema_changed()
        except Exception as e:
            error_dialog(self, f"Failed to load cinemas: {e}")

    def _on_cinema_changed(self):
        cinema_id = self.cinema_combo.currentData()
        if not cinema_id:
            return
        target = self.date_edit.date().toPyDate().isoformat()
        try:
            listings = api.get_film_listings(cinema_id, target)
            self.film_combo.blockSignals(True)
            self.film_combo.clear()
            self._showings_data = []

            for l in listings:
                self.film_combo.addItem(
                    f"{l['title']}  (Screen {l['screen_number']})",
                    l,
                )

            self.film_combo.blockSignals(False)
            self._on_film_changed()
        except Exception as e:
            error_dialog(self, f"Failed to load films: {e}")

    def _on_film_changed(self):
        self.showing_combo.clear()
        idx = self.film_combo.currentIndex()
        if idx < 0:
            return

        film_data = self.film_combo.itemData(idx)
        if not film_data:
            return

        self._showings_data = film_data.get("showings", [])
        for s in self._showings_data:
            t = s["show_time"]
            if isinstance(t, str) and len(t) > 5:
                t = t[:5]
            label = f"{t}  ({s['show_type'].capitalize()})  —  from £{s['lower_hall_price']:.2f}"
            self.showing_combo.addItem(label, s)

        self._availability = None
        self.book_btn.setEnabled(False)
        self.avail_label.hide()

    # Availability check
    def _get_seat_type(self) -> str:
        btn_id = self.seat_type_group.checkedId()
        return ["lower_hall", "upper_gallery", "vip"][btn_id]

    def _check_availability(self):
        showing_idx = self.showing_combo.currentIndex()
        if showing_idx < 0 or not self._showings_data:
            error_dialog(self, "Please select a film and showing first.")
            return

        showing = self.showing_combo.itemData(showing_idx)
        if not showing:
            return

        data = {
            "showing_id": showing["showing_id"],
            "show_date": self.date_edit.date().toPyDate().isoformat(),
            "seat_type": self._get_seat_type(),
            "num_tickets": self.num_tickets.value(),
        }

        try:
            result = api.check_availability(data)
            self._availability = result
            available = result["available"]
            seats = result["seats_available"]
            total_seats = result["seats_total"]
            unit = result["unit_price"]
            total = result["total_price"]
            seat_type = result["seat_type"].replace("_", " ").title()

            if available:
                self.avail_label.setText(
                    f"✓  {seats}/{total_seats} {seat_type} seats available\n"
                    f"Unit price: £{unit:.2f}  ×  {self.num_tickets.value()} tickets  =  "
                    f"<b>£{total:.2f}</b>"
                )
                self.avail_label.setStyleSheet(f"color: {SUCCESS}; padding: 8px;")
                self.book_btn.setEnabled(True)
            else:
                self.avail_label.setText(
                    f"✗  Only {seats} {seat_type} seat(s) available "
                    f"(requested {self.num_tickets.value()})"
                )
                self.avail_label.setStyleSheet(f"color: #DC2626; padding: 8px;")
                self.book_btn.setEnabled(False)

            self.avail_label.show()
        except Exception as e:
            detail = str(e)
            if hasattr(e, "response"):
                try:
                    detail = e.response.json().get("detail", detail)
                except Exception:
                    pass
            error_dialog(self, detail)

    # Create booking
    def _create_booking(self):
        name = self.name_input.text().strip()
        if not name:
            error_dialog(self, "Customer name is required.")
            return

        showing_idx = self.showing_combo.currentIndex()
        showing = self.showing_combo.itemData(showing_idx)
        if not showing:
            return

        data = {
            "showing_id": showing["showing_id"],
            "show_date": self.date_edit.date().toPyDate().isoformat(),
            "customer_name": name,
            "customer_phone": self.phone_input.text().strip() or None,
            "customer_email": self.email_input.text().strip() or None,
            "seat_type": self._get_seat_type(),
            "num_tickets": self.num_tickets.value(),
            "payment_simulated": True,
        }

        self.book_btn.setEnabled(False)
        self.book_btn.setText("Processing…")

        try:
            booking = api.create_booking(data)
            self._show_receipt(booking)
            show_toast(self, f"Booking {booking['booking_reference']} confirmed!", success=True)
        except Exception as e:
            detail = str(e)
            if hasattr(e, "response"):
                try:
                    detail = e.response.json().get("detail", detail)
                except Exception:
                    pass
            error_dialog(self, detail)
        finally:
            self.book_btn.setEnabled(True)
            self.book_btn.setText("Confirm Booking")

    # Receipt
    def _show_receipt(self, booking: dict):
        # Clear receipt card
        while self.receipt_card._layout.count():
            item = self.receipt_card._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.receipt_card.add(subheading_label("Booking Confirmed", 13))
        self.receipt_card.add(status_badge(booking["booking_status"]))
        self.receipt_card.add(separator())

        fields = [
            ("Reference", booking["booking_reference"]),
            ("Film", booking.get("film_title", "")),
            ("Date", str(booking["show_date"])),
            ("Time", str(booking.get("show_time", ""))[:5]),
            ("Screen", str(booking.get("screen_number", ""))),
            ("Cinema", booking.get("cinema_name", "")),
            ("Customer", booking["customer_name"]),
            ("Tickets", str(booking["num_tickets"])),
        ]

        for label, value in fields:
            self.receipt_card.add_layout(labelled_value(label, value))

        # Seat numbers
        seats = booking.get("booked_seats", [])
        if seats:
            seat_nums = ", ".join(s["seat_number"] for s in seats)
            seat_type = seats[0]["seat_type"].replace("_", " ").title()
            self.receipt_card.add_layout(labelled_value("Seats", seat_nums))
            self.receipt_card.add_layout(labelled_value("Seat Type", seat_type))

        self.receipt_card.add(separator())

        total_lbl = QLabel(f"Total: £{booking['total_cost']:.2f}")
        total_lbl.setFont(heading_font(16, bold=True))
        total_lbl.setStyleSheet(f"color: {PRIMARY}; border: none;")
        self.receipt_card.add(total_lbl)

        booking_date = booking.get("booking_date", "")
        if booking_date:
            bd_str = str(booking_date)[:19] if len(str(booking_date)) > 19 else str(booking_date)
            self.receipt_card.add(muted_label(f"Booked: {bd_str}"))

    # Reset
    def _reset_form(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.num_tickets.setValue(1)
        self.rb_lower.setChecked(True)
        self.avail_label.hide()
        self.book_btn.setEnabled(False)
        self._availability = None

        # Reset receipt
        while self.receipt_card._layout.count():
            item = self.receipt_card._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.receipt_placeholder = muted_label("Receipt will appear here after booking.")
        self.receipt_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.receipt_placeholder.setMinimumHeight(200)
        self.receipt_card.add(self.receipt_placeholder)
