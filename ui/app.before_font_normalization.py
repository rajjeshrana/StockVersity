"""StockVersity Pro application shell with a modern dashboard layout."""

from __future__ import annotations

import os
from typing import Dict, Optional

import upstox_client

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages.dashboard_page import DashboardPage
from ui.pages.intraday_page import IntradayScannerPage
from core.market_data.upstox_provider import UpstoxProvider
from core.market_data.authentication import (
    AuthenticationManager,
    UpstoxAuthentication,
)
from core.config import (
    UPSTOX_API_KEY,
    UPSTOX_API_SECRET,
    UPSTOX_REDIRECT_URI,
)
from ui.market_controller import MarketController
from ui.live_market_bridge import LiveMarketBridge
from core.dependency_container import get_container


class MainWindow(QMainWindow):
    """Main window for StockVersity Scanner Pro."""

    PAGES = {
        "dashboard": "Dashboard",
        "scanner": "Scanner",
        "market": "Market",
        "watchlist": "Watchlist",
        "alerts": "Alerts",
        "portfolio": "Portfolio",
        "news": "News",
        "reports": "Reports",
        "settings": "Settings",
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._pages: Dict[str, QWidget] = {}
        self._nav_buttons: Dict[str, QPushButton] = {}
        self.setWindowTitle("StockVersity Scanner Pro")
        self.setMinimumSize(1280, 760)
        self.resize(1600, 960)

        # Create dashboard first because its live IndexCard
        # widgets are mounted into the application header.
        self.dashboard_page = DashboardPage()

        self._build_ui()
        self._initialize_live_market()
        self.show_page("dashboard")

    def _initialize_live_market(self) -> None:
        """
        Initialize the production Upstox live market pipeline.

        Upstox
            -> UpstoxProvider
            -> WebSocketManager V3
            -> MarketDataParser
            -> LiveMarketBridge
            -> MarketController
            -> Dashboard
        """

        self.upstox_provider = None
        self.market_controller = None
        self.live_market_bridge = None

        try:
            # ---------------------------------------------
            # Upstox configuration
            # ---------------------------------------------
            api_key = UPSTOX_API_KEY
            api_secret = UPSTOX_API_SECRET
            redirect_uri = UPSTOX_REDIRECT_URI

            # ---------------------------------------------
            # Authentication manager
            # ---------------------------------------------
            self.auth_manager = AuthenticationManager()
            saved_token = self.auth_manager.get_token(
                "upstox"
            )
            access_token = (
                saved_token.access_token
                if saved_token is not None
                else ""
            )

            # ---------------------------------------------
            # OAuth provider
            # ---------------------------------------------
            self.upstox_auth = UpstoxAuthentication(
                client_id=api_key,
                client_secret=api_secret,
                redirect_uri=redirect_uri,
            )

            # ---------------------------------------------
            # Validate configuration
            # ---------------------------------------------
            if not api_key:
                print(
                    "[LIVE MARKET] "
                    "UPSTOX_API_KEY missing."
                )
                return

            if not api_secret:
                print(
                    "[LIVE MARKET] "
                    "UPSTOX_API_SECRET missing."
                )
                return

            if not redirect_uri:
                print(
                    "[LIVE MARKET] "
                    "UPSTOX_REDIRECT_URI missing."
                )
                return

            if not access_token:
                print(
                    "[LIVE MARKET] "
                    "No saved Upstox access token."
                )
                print(
                    "[LIVE MARKET] "
                    "OAuth login required."
                )
                return

            # ---------------------------------------------
            # Official Upstox SDK configuration
            # ---------------------------------------------

            configuration = (
                upstox_client.Configuration()
            )

            configuration.access_token = (
                access_token
            )

            api_client = (
                upstox_client.ApiClient(
                    configuration
                )
            )

            # Keep reference alive for the application
            self.upstox_api_client = api_client

            # ---------------------------------------------
            # Provider
            # ---------------------------------------------

            self.upstox_provider = (
                UpstoxProvider(
                    api_client
                )
            )

            # ---------------------------------------------
            # Market Controller
            # ---------------------------------------------

            container = get_container()
            self.market_controller = (
                MarketController(
                    backend=container.nse_engine,
                    dashboard=self.dashboard_page,
                    parent=self,
                )
            )

            # ---------------------------------------------
            # Qt-safe bridge
            # ---------------------------------------------

            self.live_market_bridge = (
                LiveMarketBridge(
                    market_controller=(
                        self.market_controller
                    ),
                    parent=self,
                )
            )

            # Provider -> Qt bridge
            self.upstox_provider.add_tick_callback(
                self.live_market_bridge.on_tick
            )
            # ---------------------------------------------
            # Dashboard live index subscriptions
            # ---------------------------------------------
            index_instruments = [
                "NSE_INDEX|Nifty 50",
                "NSE_INDEX|Nifty Bank",
                "NSE_INDEX|Nifty Fin Service",
                "NSE_INDEX|India VIX",
            ]
            # Register subscriptions before connection.
            self.upstox_provider.subscribe_many(
                index_instruments,
                mode="full",
            )
            # Start Upstox WebSocket.
            connected = self.upstox_provider.start()
            if connected:
                print(
                    "[LIVE MARKET] Upstox connected."
                )
            else:
                print(
                    "[LIVE MARKET] Upstox connection failed."
                )
            # Start dashboard market timers.
            self.market_controller.start()

            print(
                "[LIVE MARKET] Pipeline initialized."
            )

        except Exception as exc:

            print(
                "[LIVE MARKET] Initialization failed:",
                exc,
            )

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background: #070d18; }
            QLabel { color: #e8edf7; font-family: 'Segoe UI'; }
            QScrollBar:vertical { background: #0b1322; width: 10px; }
            QScrollBar::handle:vertical { background: #24314b; border-radius: 5px; }
        """)
        root = QWidget(self)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._create_sidebar())

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._create_header())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: #080f1c; }")
        right_layout.addWidget(self.stack, 1)
        right_layout.addWidget(self._create_footer())
        root_layout.addWidget(right, 1)
        self.setCentralWidget(root)

        self._add_page(
            "dashboard",
            self.dashboard_page,
        )
        self._add_page("scanner", IntradayScannerPage())

    def _create_sidebar(self) -> QFrame:
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
                font-size: 13px;
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
            font-size: 15px;
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
            font-size: 13px;
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
                    font-size: 13px;
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


    def _add_page(self, key: str, page: QWidget) -> None:
        self._pages[key] = page
        self.stack.addWidget(page)

    def _placeholder(self, key: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel(self.PAGES[key])
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        detail = QLabel("This workspace is ready for its next module.")
        detail.setAlignment(Qt.AlignCenter)
        detail.setStyleSheet("color: #95a3b8; font-size: 16px;")
        layout.addWidget(title)
        layout.addWidget(detail)
        return page

    def show_page(self, key: str) -> None:
        if key not in self._pages:
            self._add_page(key, self._placeholder(key))
        self.stack.setCurrentWidget(self._pages[key])
        for name, button in self._nav_buttons.items():
            button.setProperty("active", name == key)
            button.style().unpolish(button)
            button.style().polish(button)

    def cleanup(self) -> None:
        """Hook called by main.py during shutdown."""

    def closeEvent(self, event: QCloseEvent) -> None:
        self.cleanup()
        event.accept()