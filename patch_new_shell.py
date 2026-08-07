from pathlib import Path

path = Path("ui/app.py")
text = path.read_text(encoding="utf-8")

# ---------------------------------------------------------
# ADD QTimer IMPORT
# ---------------------------------------------------------

text = text.replace(
    "from PySide6.QtCore import Qt",
    "from PySide6.QtCore import Qt, QTimer"
)

# ---------------------------------------------------------
# IMPORTANT:
# Dashboard must exist BEFORE _build_ui because the new
# header uses dashboard_page.index_cards.
# ---------------------------------------------------------

old = '''        self.setMinimumSize(1280, 760)
        self.resize(1600, 960)
        self._build_ui()
        self._initialize_live_market()
        self.show_page("dashboard")'''

new = '''        self.setMinimumSize(1280, 760)
        self.resize(1600, 960)

        # Create dashboard first because its live IndexCard
        # widgets are mounted into the application header.
        self.dashboard_page = DashboardPage()

        self._build_ui()
        self._initialize_live_market()
        self.show_page("dashboard")'''

if old not in text:
    raise SystemExit("STOP: __init__ TARGET NOT FOUND")

text = text.replace(old, new)

# ---------------------------------------------------------
# REMOVE SECOND DASHBOARD CREATION
# ---------------------------------------------------------

old = '''        self.dashboard_page = DashboardPage()
        self._add_page(
            "dashboard",
            self.dashboard_page,
        )'''

new = '''        self._add_page(
            "dashboard",
            self.dashboard_page,
        )'''

if old not in text:
    raise SystemExit("STOP: DASHBOARD CREATION TARGET NOT FOUND")

text = text.replace(old, new)

# ---------------------------------------------------------
# REPLACE SIDEBAR -> FOOTER METHODS
# ---------------------------------------------------------

start = text.index("    def _create_sidebar(self) -> QFrame:")
end = text.index("    def _add_page(", start)

replacement = r'''    def _create_sidebar(self) -> QFrame:
        """Create approved StockVersity navigation sidebar."""

        sidebar = QFrame()
        sidebar.setObjectName("mainSidebar")
        sidebar.setFixedWidth(178)

        sidebar.setStyleSheet("""
            QFrame#mainSidebar {
                background: #08111f;
                border-right: 1px solid #18263a;
            }

            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                color: #8f9caf;
                text-align: left;
                padding: 9px 12px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 500;
            }

            QPushButton:hover {
                background: #101d30;
                color: #e9eef7;
            }

            QPushButton[active="true"] {
                background: #142642;
                color: #ffffff;
                font-weight: 700;
                border-left: 2px solid #3578ff;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(11, 14, 11, 12)
        layout.setSpacing(3)

        # Brand
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(5, 0, 0, 0)

        logo = QLabel("◆")
        logo.setStyleSheet("""
            color: #397cff;
            font-size: 18px;
            font-weight: 800;
        """)

        brand = QLabel("StockVersity")
        brand.setStyleSheet("""
            color: #f1f5fb;
            font-family: "Segoe UI";
            font-size: 16px;
            font-weight: 800;
        """)

        pro = QLabel("PRO")
        pro.setAlignment(Qt.AlignCenter)
        pro.setFixedSize(28, 16)
        pro.setStyleSheet("""
            background: #173564;
            color: #6ea0ff;
            border-radius: 4px;
            font-size: 7px;
            font-weight: 800;
        """)

        brand_row.addWidget(logo)
        brand_row.addSpacing(4)
        brand_row.addWidget(brand)
        brand_row.addSpacing(4)
        brand_row.addWidget(pro)
        brand_row.addStretch()

        layout.addLayout(brand_row)
        layout.addSpacing(18)

        nav_items = [
            ("dashboard", "▦", "Dashboard"),
            ("scanner", "⌁", "Scanner"),
            ("market", "⌁", "Market"),
            ("watchlist", "★", "Watchlist"),
            ("alerts", "●", "Alerts"),
            ("portfolio", "▣", "Portfolio"),
            ("news", "▤", "News"),
            ("reports", "▥", "Reports"),
            ("settings", "⚙", "Settings"),
        ]

        for key, icon, label in nav_items:
            button = QPushButton(
                f"{icon}     {label}"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False, name=key:
                self.show_page(name)
            )

            self._nav_buttons[key] = button
            layout.addWidget(button)

        layout.addStretch(1)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(
            "background:#18263a;"
        )
        layout.addWidget(separator)
        layout.addSpacing(10)

        market_title = QLabel("MARKET TIME")
        market_title.setStyleSheet("""
            color: #66758b;
            font-size: 8px;
            font-weight: 800;
        """)

        self.sidebar_clock = QLabel("--:--:--")
        self.sidebar_clock.setStyleSheet("""
            color: #e6edf8;
            font-size: 14px;
            font-weight: 700;
        """)

        self.sidebar_market_status = QLabel(
            "●  NSE   CHECKING\n●  BSE   CHECKING"
        )

        self.sidebar_market_status.setStyleSheet("""
            color: #6f8097;
            font-size: 9px;
            line-height: 1.5;
        """)

        layout.addWidget(market_title)
        layout.addSpacing(4)
        layout.addWidget(self.sidebar_clock)
        layout.addSpacing(5)
        layout.addWidget(self.sidebar_market_status)

        return sidebar


    def _create_header(self) -> QFrame:
        """Create approved compact live-market header."""

        header = QFrame()
        header.setObjectName("mainHeader")
        header.setFixedHeight(70)

        header.setStyleSheet("""
            QFrame#mainHeader {
                background: #091321;
                border-bottom: 1px solid #19283d;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 7, 14, 7)
        layout.setSpacing(4)

        # -------------------------------------------------
        # Search box
        # -------------------------------------------------

        search = QLabel(
            "⌕   Search stocks, indices...     Ctrl + K"
        )

        search.setFixedWidth(235)
        search.setStyleSheet("""
            background: #0e1b2d;
            border: 1px solid #1d3048;
            border-radius: 7px;
            color: #75859b;
            padding: 8px 10px;
            font-size: 10px;
        """)

        layout.addWidget(search)
        layout.addSpacing(6)

        # -------------------------------------------------
        # LIVE index cards from DashboardPage
        # -------------------------------------------------

        for key in (
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
            "INDIAVIX",
        ):
            card = self.dashboard_page.index_cards[key]
            card.setMinimumWidth(100)
            card.setMaximumWidth(130)
            layout.addWidget(card)

        layout.addStretch(1)

        # -------------------------------------------------
        # Market status
        # -------------------------------------------------

        self.header_market_status = QLabel(
            "● MARKET\n  --:--:--"
        )

        self.header_market_status.setMinimumWidth(92)
        self.header_market_status.setAlignment(
            Qt.AlignCenter
        )

        self.header_market_status.setStyleSheet("""
            background: #0d1b29;
            border: 1px solid #1d3148;
            border-radius: 7px;
            color: #42dc87;
            padding: 5px 7px;
            font-size: 8px;
            font-weight: 700;
        """)

        layout.addWidget(self.header_market_status)

        # -------------------------------------------------
        # Compact controls
        # -------------------------------------------------

        for symbol in ("☼", "☾", "●", "⚙"):
            button = QPushButton(symbol)
            button.setFixedSize(28, 28)
            button.setCursor(Qt.PointingHandCursor)

            button.setStyleSheet("""
                QPushButton {
                    background: #0e1b2d;
                    border: 1px solid #1d3048;
                    border-radius: 6px;
                    color: #9aabc0;
                    font-size: 11px;
                }

                QPushButton:hover {
                    background: #15263d;
                    color: #ffffff;
                }
            """)

            layout.addWidget(button)

        profile = QLabel("RR")
        profile.setFixedSize(30, 30)
        profile.setAlignment(Qt.AlignCenter)

        profile.setStyleSheet("""
            background: #17325c;
            border: 1px solid #315d9d;
            border-radius: 15px;
            color: #ffffff;
            font-size: 9px;
            font-weight: 800;
        """)

        layout.addWidget(profile)

        # Clock
        self.ui_clock_timer = QTimer(self)
        self.ui_clock_timer.timeout.connect(
            self._update_shell_clock
        )
        self.ui_clock_timer.start(1000)

        self._update_shell_clock()

        return header


    def _create_footer(self) -> QFrame:
        """Create approved compact application footer."""

        footer = QFrame()
        footer.setObjectName("mainFooter")
        footer.setFixedHeight(27)

        footer.setStyleSheet("""
            QFrame#mainFooter {
                background: #08111f;
                border-top: 1px solid #18263a;
            }
        """)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        source = QLabel(
            "NSE • BSE     Powered by StockVersity Engine"
        )

        source.setStyleSheet("""
            color: #64758b;
            font-size: 8px;
        """)

        layout.addWidget(source)
        layout.addStretch(1)

        self.footer_status = QLabel(
            "● REAL-TIME     ● CONNECTED"
        )

        self.footer_status.setStyleSheet("""
            color: #32d47f;
            font-size: 8px;
            font-weight: 700;
        """)

        layout.addWidget(self.footer_status)

        return footer


    def _update_shell_clock(self) -> None:
        """Update sidebar/header market clock."""

        from datetime import datetime

        now = datetime.now()
        time_text = now.strftime("%H:%M:%S")

        if hasattr(self, "sidebar_clock"):
            self.sidebar_clock.setText(
                time_text
            )

        # NSE regular session.
        minutes = now.hour * 60 + now.minute

        market_open = (
            now.weekday() < 5
            and
            (9 * 60 + 15)
            <= minutes
            <
            (15 * 60 + 30)
        )

        if market_open:
            status_text = "OPEN"
            status_color = "#32d47f"
        else:
            status_text = "CLOSED"
            status_color = "#ff5b68"

        if hasattr(
            self,
            "sidebar_market_status",
        ):
            self.sidebar_market_status.setText(
                f"●  NSE   {status_text}\n"
                f"●  BSE   {status_text}"
            )

            self.sidebar_market_status.setStyleSheet(
                f"""
                color: {status_color};
                font-size: 9px;
                line-height: 1.5;
                """
            )

        if hasattr(
            self,
            "header_market_status",
        ):
            self.header_market_status.setText(
                f"● MARKET {status_text}\n"
                f"{time_text}"
            )

            self.header_market_status.setStyleSheet(
                f"""
                background: #0d1b29;
                border: 1px solid #1d3148;
                border-radius: 7px;
                color: {status_color};
                padding: 5px 7px;
                font-size: 8px;
                font-weight: 700;
                """
            )


'''

text = (
    text[:start]
    + replacement
    + text[end:]
)

path.write_text(
    text,
    encoding="utf-8",
)

print("NEW APPROVED APP SHELL PATCHED: OK")
