"""
StockVersity Scanner Pro
Main Application Shell

Approved UI:
- Large readable sidebar
- NIFTY 50
- BANK NIFTY
- INDIA VIX
- BTC / USD
- GOLD / USD
- SILVER / USD
- No search box
- FINNIFTY hidden from header
- Live Upstox market pipeline preserved
"""

from __future__ import annotations

from datetime import datetime
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

from core.market_data.upstox_auto_login import (
    get_upstox_access_token_sync,
)

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
from core.market_data.nifty500_universe import Nifty500Universe
from core.market_data.live_stock_universe import LiveStockUniverse
from core.upstox_client import UpstoxClient


# =========================================================
# COLORS
# =========================================================

BG = "#06101d"
SIDEBAR_BG = "#071321"
HEADER_BG = "#07111e"
FOOTER_BG = "#07111e"

PANEL = "#0a1828"
PANEL_ALT = "#0d1c2e"

BORDER = "#1a2b40"
BORDER_ACTIVE = "#2458ff"

TEXT = "#f0f4fb"
MUTED = "#8ca0ba"

BLUE = "#2f7cff"
CYAN = "#00c8ff"

GREEN = "#21dd7a"
RED = "#ff4658"
ORANGE = "#ff9818"
GOLD = "#f5b400"
SILVER = "#aeb7c4"


# =========================================================
# MAIN WINDOW
# =========================================================

class MainWindow(QMainWindow):
    """
    Main StockVersity Scanner Pro application window.
    """

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

    NAV_ICONS = {
        "dashboard": "▦",
        "scanner": "⌁",
        "market": "〽",
        "watchlist": "☆",
        "alerts": "♧",
        "portfolio": "▣",
        "news": "▤",
        "reports": "▥",
        "settings": "⚙",
    }

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        # -------------------------------------------------
        # Internal UI containers
        # -------------------------------------------------

        self._pages: Dict[str, QWidget] = {}
        self._nav_buttons: Dict[str, QPushButton] = {}

        # -------------------------------------------------
        # Live market objects
        # -------------------------------------------------

        self.upstox_provider = None
        self.upstox_api_client = None

        self.market_controller = None
        self.live_market_bridge = None

        self.auth_manager = None
        self.upstox_auth = None

        # -------------------------------------------------
        # Window
        # -------------------------------------------------

        self.setWindowTitle(
            "StockVersity Scanner Pro"
        )

        self.setMinimumSize(
            1280,
            760,
        )

        self.resize(
            1600,
            920,
        )

        # -------------------------------------------------
        # Build UI FIRST
        # -------------------------------------------------

        self._build_ui()

        # -------------------------------------------------
        # Start live market pipeline
        # -------------------------------------------------

        self._initialize_live_market()

        # -------------------------------------------------
        # Default page
        # -------------------------------------------------

        self.show_page(
            "dashboard"
        )


    # =====================================================
    # LIVE MARKET INITIALIZATION
    # =====================================================

    def _initialize_live_market(self) -> None:
        """
        Initialize production Upstox live-market pipeline.

        Upstox
            ->
        UpstoxProvider
            ->
        WebSocketManager V3
            ->
        MarketDataParser
            ->
        LiveMarketBridge
            ->
        MarketController
            ->
        Dashboard
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
            # Validate Upstox configuration
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

            # ---------------------------------------------
            # Authentication manager / OAuth provider
            # ---------------------------------------------

            self.auth_manager = (
                AuthenticationManager()
            )

            self.upstox_auth = (
                UpstoxAuthentication(
                    client_id=api_key,
                    client_secret=api_secret,
                    redirect_uri=redirect_uri,
                )
            )

            # ---------------------------------------------
            # Automatic background Upstox authentication
            # ---------------------------------------------

            print(
                "[LIVE MARKET] "
                "Checking Upstox authentication..."
            )

            try:

                access_token = (
                    get_upstox_access_token_sync()
                )

            except Exception as exc:

                print(
                    "[LIVE MARKET] "
                    "Upstox automatic authentication "
                    f"failed: {exc}"
                )

                return

            if not access_token:

                print(
                    "[LIVE MARKET] "
                    "Upstox access token unavailable."
                )

                return

            print(
                "[LIVE MARKET] "
                "Upstox authentication ready."
            )

            # ---------------------------------------------
            # Official Upstox SDK
            # ---------------------------------------------

            # ---------------------------------------------
            # Scanner historical REST client
            # Uses SAME authenticated Upstox token.
            # ---------------------------------------------

            self.upstox_history_client = UpstoxClient(
                api_key=api_key,
                access_token=access_token,
                sandbox=False,
            )

            print(
                "[SCANNER DATA] "
                "Historical Upstox client ready."
            )

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

            # Keep reference alive
            self.upstox_api_client = (
                api_client
            )

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
            # Qt-safe live bridge
            # ---------------------------------------------

            self.live_market_bridge = (
                LiveMarketBridge(
                    market_controller=(
                        self.market_controller
                    ),
                    parent=self,
                )
            )

            # ---------------------------------------------
            # Previous-session index closes
            # ---------------------------------------------
            # Load once from the existing authenticated
            # historical REST client. These values are used
            # by LiveMarketBridge only when an incoming
            # WebSocket index tick does not contain a valid
            # previous_close.
            #
            # No second WebSocket or authentication session
            # is created here.

            try:

                from datetime import date, timedelta

                history_to = date.today()
                history_from = (
                    history_to
                    - timedelta(days=10)
                )

                index_history_keys = (
                    "NSE_INDEX|Nifty 50",
                    "NSE_INDEX|Nifty Bank",
                    "NSE_INDEX|Nifty Fin Service",
                    "NSE_INDEX|India VIX",
                )

                previous_closes = {}

                for instrument_key in index_history_keys:

                    try:

                        dataframe = (
                            self.upstox_history_client
                            .historical_data(
                                instrument_key,
                                "day",
                                history_from.isoformat(),
                                history_to.isoformat(),
                            )
                        )

                        if (
                            dataframe is not None
                            and not dataframe.empty
                            and "close" in dataframe.columns
                        ):

                            valid_close = (
                                dataframe["close"]
                                .dropna()
                            )

                            if not valid_close.empty:

                                close = float(
                                    valid_close.iloc[-1]
                                )

                                if close > 0:

                                    previous_closes[
                                        instrument_key
                                    ] = close

                                    print(
                                        "[INDEX HISTORY] "
                                        f"{instrument_key}: "
                                        f"previous close "
                                        f"{close:.2f}"
                                    )

                    except Exception as exc:

                        print(
                            "[INDEX HISTORY] "
                            f"Unable to load "
                            f"{instrument_key}: "
                            f"{exc}"
                        )

                self.live_market_bridge.set_previous_closes(
                    previous_closes
                )

                print(
                    "[INDEX HISTORY] "
                    f"Loaded {len(previous_closes)}/"
                    f"{len(index_history_keys)} "
                    "previous closes."
                )

            except Exception as exc:

                print(
                    "[INDEX HISTORY] "
                    "Previous-close bootstrap failed: "
                    f"{exc}"
                )

            # ---------------------------------------------
            # Provider -> Qt bridge
            # ---------------------------------------------

            self.upstox_provider.add_tick_callback(
                self.live_market_bridge.on_tick
            )

            # ---------------------------------------------
            # NIFTY 500 live stock universe
            # ---------------------------------------------

            self.nifty500_universe = (
                Nifty500Universe()
            )

            self.live_stock_universe = (
                LiveStockUniverse(
                    self.nifty500_universe
                ).load()
            )

            # ---------------------------------------------
            # Give MarketController access to the same
            # live NIFTY 500 universe.
            # ---------------------------------------------

            self.market_controller.live_stock_universe = (
                self.live_stock_universe
            )

            self.upstox_provider.add_tick_callback(
                self.live_stock_universe.on_tick
            )

            nifty500_instruments = (
                self.live_stock_universe.instrument_keys()
            )

            print(
                "[LIVE MARKET] "
                f"NIFTY 500 universe ready: "
                f"{len(nifty500_instruments)} instruments."
            )

            self.upstox_provider.subscribe_many(
                nifty500_instruments,
                mode="ltpc",
            )

            # ---------------------------------------------
            # Dashboard live index subscriptions
            # ---------------------------------------------

            index_instruments = [
                "NSE_INDEX|Nifty 50",
                "NSE_INDEX|Nifty Bank",

                # Keep FINNIFTY subscription internally.
                # It is hidden visually from the header,
                # but MarketController may still use it.
                "NSE_INDEX|Nifty Fin Service",

                "NSE_INDEX|India VIX",
            ]

            self.upstox_provider.subscribe_many(
                index_instruments,
                mode="full",
            )

            # ---------------------------------------------
            # Start Upstox WebSocket
            # ---------------------------------------------

            connected = (
                self.upstox_provider.start()
            )

            if connected:

                print(
                    "[LIVE MARKET] "
                    "Upstox connected."
                )

            else:

                print(
                    "[LIVE MARKET] "
                    "Upstox connection failed."
                )

            # ---------------------------------------------
            # Start controller timers
            # ---------------------------------------------

            self.market_controller.start()

            print(
                "[LIVE MARKET] "
                "Pipeline initialized."
            )

        except Exception as exc:

            print(
                "[LIVE MARKET] "
                "Initialization failed:",
                exc,
            )


    # =====================================================
    # BUILD APPLICATION
    # =====================================================

    def _build_ui(self) -> None:

        # -------------------------------------------------
        # Global shell style
        # -------------------------------------------------

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: {BG};
            }}

            QLabel {{
                color: {TEXT};
                font-family: "Segoe UI";
            }}

            QPushButton {{
                font-family: "Segoe UI";
            }}

            QScrollBar:vertical {{
                background: #07111e;
                width: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: #25364f;
                border-radius: 5px;
                min-height: 35px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #354b6b;
            }}

            QScrollBar:horizontal {{
                height: 0px;
                background: transparent;
            }}
            """
        )

        # -------------------------------------------------
        # Root widget
        # -------------------------------------------------

        root = QWidget(self)

        root_layout = QHBoxLayout(root)

        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root_layout.setSpacing(0)

        # -------------------------------------------------
        # Sidebar
        # -------------------------------------------------

        root_layout.addWidget(
            self._create_sidebar()
        )

        # -------------------------------------------------
        # Right application area
        # -------------------------------------------------

        right = QWidget()

        right.setStyleSheet(
            f"background:{BG};"
        )

        right_layout = QVBoxLayout(right)

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        right_layout.setSpacing(0)

        # -------------------------------------------------
        # IMPORTANT:
        # Dashboard must exist before header because header
        # uses dashboard_page.index_cards.
        # -------------------------------------------------

        self.dashboard_page = (
            DashboardPage()
        )

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        right_layout.addWidget(
            self._create_header()
        )

        # -------------------------------------------------
        # Page stack
        # -------------------------------------------------

        self.stack = QStackedWidget()

        self.stack.setStyleSheet(
            f"""
            QStackedWidget {{
                background: {BG};
                border: none;
            }}
            """
        )

        right_layout.addWidget(
            self.stack,
            1,
        )

        # -------------------------------------------------
        # Footer
        # -------------------------------------------------

        right_layout.addWidget(
            self._create_footer()
        )

        root_layout.addWidget(
            right,
            1,
        )

        self.setCentralWidget(
            root
        )

        # -------------------------------------------------
        # Pages
        # -------------------------------------------------

        self._add_page(
            "dashboard",
            self.dashboard_page,
        )

        self.intraday_page = IntradayScannerPage()

        self._add_page(
            "scanner",
            self.intraday_page,
        )

        # -------------------------------------------------
        # LIVE INTRADAY SCANNER CONNECTION
        # -------------------------------------------------

        try:

            container = get_container()

            self.application_controller = (
                container.get(
                    "application_controller"
                )
            )

            self.intraday_page.scan_requested.connect(
                self._run_intraday_scan
            )

            self.application_controller.scannerCompleted.connect(
                self._receive_intraday_results
            )

            print(
                "[INTRADAY] Live scanner connected."
            )

        except Exception as exc:

            print(
                "[INTRADAY] Connection failed:",
                exc,
            )


    # =====================================================
    # LIVE INTRADAY SCANNER BRIDGE
    # =====================================================

    def _run_intraday_scan(
        self,
        filters: Dict,
    ) -> None:
        """
        Run the shared production scanner system.

        Uses the same ScannerBootstrap singleton populated by
        DataManager from the live Upstox feed and historical
        candle pipeline.
        """

        try:

            from core.scanner.scanner_bootstrap import (
                get_scanner_system,
            )

            print(
                "[INTRADAY] Scan requested:",
                filters,
            )

            scanner_system = get_scanner_system()

            if not getattr(
                scanner_system,
                "initialized",
                False,
            ):
                scanner_system.initialize()

            status_before = scanner_system.status()

            bridge_status = status_before.get(
                "bridge",
                {},
            )

            print(
                "[PRODUCTION SCANNER] Bridge symbols:",
                bridge_status.get(
                    "symbols",
                    0,
                ),
            )

            print(
                "[PRODUCTION SCANNER] Registered scanners:",
                len(
                    status_before.get(
                        "registered_scanners",
                        [],
                    )
                ),
            )

            signals = scanner_system.scan_now()

            if signals is None:
                signals = []

            print(
                "[PRODUCTION SCANNER] Raw signals:",
                len(signals),
            )

            opportunities = []

            for signal in signals:

                signal_type = getattr(
                    signal,
                    "signal_type",
                    "",
                )

                if hasattr(signal_type, "value"):
                    signal_type = signal_type.value

                strength = getattr(
                    signal,
                    "strength",
                    "",
                )

                if hasattr(strength, "value"):
                    strength = strength.value

                indicators = getattr(
                    signal,
                    "indicators",
                    {},
                ) or {}

                metadata = getattr(
                    signal,
                    "metadata",
                    {},
                ) or {}

                entry = float(
                    getattr(
                        signal,
                        "entry",
                        0.0,
                    )
                    or 0.0
                )

                price = float(
                    getattr(
                        signal,
                        "price",
                        0.0,
                    )
                    or 0.0
                )

                if entry <= 0:
                    entry = price

                score = float(
                    getattr(
                        signal,
                        "score",
                        0.0,
                    )
                    or 0.0
                )

                confidence = float(
                    getattr(
                        signal,
                        "confidence",
                        0.0,
                    )
                    or 0.0
                )

                if score <= 1.0 and score > 0:
                    score *= 100.0

                if confidence <= 1.0 and confidence > 0:
                    confidence *= 100.0

                rvol = (
                    indicators.get("rvol")
                    or indicators.get(
                        "relative_volume"
                    )
                    or metadata.get("rvol")
                    or metadata.get(
                        "relative_volume"
                    )
                    or 0.0
                )

                opportunity = {
                    "symbol": getattr(
                        signal,
                        "symbol",
                        "",
                    ),
                    "instrument_key": getattr(
                        signal,
                        "instrument_key",
                        "",
                    ),
                    "signal": str(
                        signal_type
                    ),
                    "signal_type": str(
                        signal_type
                    ),
                    "strength": str(
                        strength
                    ),
                    "pattern": getattr(
                        signal,
                        "pattern",
                        "",
                    ),
                    "scanner": getattr(
                        signal,
                        "scanner_name",
                        "",
                    ),
                    "scanner_name": getattr(
                        signal,
                        "scanner_name",
                        "",
                    ),
                    "timeframe": getattr(
                        signal,
                        "timeframe",
                        "",
                    ),
                    "score": score,
                    "confidence": confidence,
                    "price": price,
                    "ltp": price,
                    "entry": entry,
                    "stop_loss": float(
                        getattr(
                            signal,
                            "stop_loss",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target": float(
                        getattr(
                            signal,
                            "target1",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target1": float(
                        getattr(
                            signal,
                            "target1",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target2": float(
                        getattr(
                            signal,
                            "target2",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target3": float(
                        getattr(
                            signal,
                            "target3",
                            0.0,
                        )
                        or 0.0
                    ),
                    "risk_reward": float(
                        getattr(
                            signal,
                            "risk_reward",
                            0.0,
                        )
                        or 0.0
                    ),
                    "rr": float(
                        getattr(
                            signal,
                            "risk_reward",
                            0.0,
                        )
                        or 0.0
                    ),
                    "volume": getattr(
                        signal,
                        "volume",
                        0,
                    ),
                    "average_volume": getattr(
                        signal,
                        "average_volume",
                        0,
                    ),
                    "rvol": float(
                        rvol or 0.0
                    ),
                    "indicators": indicators,
                    "metadata": metadata,
                }

                opportunities.append(
                    opportunity
                )

            minimum_score = float(
                filters.get(
                    "minimum_score",
                    0,
                )
                or 0
            )

            if minimum_score > 0:

                opportunities = [
                    item
                    for item in opportunities
                    if float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ) >= minimum_score
                ]

            direction = str(
                filters.get(
                    "direction",
                    "Both",
                )
            ).strip().lower()

            if direction not in (
                "",
                "both",
                "all",
            ):

                if direction in (
                    "buy",
                    "bullish",
                    "long",
                ):
                    allowed = {
                        "BUY",
                        "BULLISH",
                        "LONG",
                    }

                elif direction in (
                    "sell",
                    "bearish",
                    "short",
                ):
                    allowed = {
                        "SELL",
                        "BEARISH",
                        "SHORT",
                    }

                else:
                    allowed = set()

                if allowed:

                    opportunities = [
                        item
                        for item in opportunities
                        if str(
                            item.get(
                                "signal",
                                "",
                            )
                        ).upper() in allowed
                    ]

            opportunities.sort(
                key=lambda item: (
                    float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ),
                    float(
                        item.get(
                            "confidence",
                            0.0,
                        )
                        or 0.0
                    ),
                ),
                reverse=True,
            )

            print(
                "[PRODUCTION SCANNER] UI opportunities:",
                len(opportunities),
            )

            self._receive_intraday_results(
                opportunities
            )

        except Exception as exc:

            import traceback

            print(
                "[INTRADAY] Production scan failed:",
                exc,
            )

            traceback.print_exc()

            if hasattr(
                self,
                "intraday_page",
            ):

                self.intraday_page.scan_failed(
                    str(exc)
                )


    def _receive_intraday_results(
        self,
        opportunities,
    ) -> None:
        """
        Receive ranked opportunities from the existing
        ApplicationController scannerCompleted signal.
        """

        try:

            if opportunities is None:
                opportunities = []

            if not isinstance(
                opportunities,
                list,
            ):
                opportunities = list(
                    opportunities
                )

            print(
                "[INTRADAY] Results received:",
                len(opportunities),
            )

            self.intraday_page.set_scanner_results(
                opportunities
            )

            # Keep Dashboard scanner widgets synchronized
            # with the same real scannerCompleted payload.
            if hasattr(
                self,
                "dashboard_page",
            ):

                self.dashboard_page.update_scanner_results(
                    opportunities
                )

        except Exception as exc:

            print(
                "[INTRADAY] Result update failed:",
                exc,
            )


    # =====================================================
    # SIDEBAR
    # =====================================================

    def _create_sidebar(self) -> QFrame:
        """
        Create approved larger StockVersity sidebar.
        """

        sidebar = QFrame()

        sidebar.setObjectName(
            "mainSidebar"
        )

        sidebar.setFixedWidth(
            200
        )

        sidebar.setStyleSheet(
            f"""
            QFrame#mainSidebar {{
                background: {SIDEBAR_BG};
                border-right: 1px solid {BORDER};
            }}

            QPushButton {{
                color: #c3cfdf;
                background: transparent;
                border: none;
                border-left: 3px solid transparent;
                border-radius: 7px;
                text-align: left;
                padding: 11px 12px;
                font-size: 15px;
                font-weight: 500;
            }}

            QPushButton:hover {{
                background: #10223a;
                color: #ffffff;
            }}

            QPushButton[active="true"] {{
                background: #15345f;
                color: #ffffff;
                border-left: 3px solid #347cff;
                font-weight: 700;
            }}
            """
        )

        layout = QVBoxLayout(
            sidebar
        )

        layout.setContentsMargins(
            12,
            15,
            12,
            12,
        )

        layout.setSpacing(
            5
        )

        # -------------------------------------------------
        # Brand
        # -------------------------------------------------

        brand_row = QHBoxLayout()

        brand_row.setContentsMargins(
            2,
            0,
            2,
            8,
        )

        brand_icon = QLabel("◆")

        brand_icon.setStyleSheet(
            """
            color: #397cff;
            font-size: 20px;
            font-weight: 900;
            """
        )

        brand_row.addWidget(
            brand_icon
        )

        brand_text = QLabel(
            "StockVersity"
        )

        brand_text.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Bold,
            )
        )

        brand_text.setStyleSheet(
            """
            color: #ffffff;
            font-size: 17px;
            font-weight: 800;
            """
        )

        brand_row.addWidget(
            brand_text
        )

        pro = QLabel("PRO")

        pro.setAlignment(
            Qt.AlignCenter
        )

        pro.setFixedSize(
            30,
            18,
        )

        pro.setStyleSheet(
            """
            background: #294ea0;
            border-radius: 4px;
            color: #9fc8ff;
            font-size: 9px;
            font-weight: 800;
            """
        )

        brand_row.addWidget(
            pro
        )

        brand_row.addStretch()

        layout.addLayout(
            brand_row
        )

        # -------------------------------------------------
        # Scanner Pro subtitle
        # -------------------------------------------------

        scanner_pro = QLabel(
            "Scanner Pro"
        )

        scanner_pro.setStyleSheet(
            """
            color: #00c8ff;
            font-size: 12px;
            font-weight: 700;
            padding-left: 36px;
            padding-bottom: 6px;
            """
        )

        layout.addWidget(
            scanner_pro
        )

        # -------------------------------------------------
        # Navigation
        # -------------------------------------------------

        for key, label in self.PAGES.items():

            icon = self.NAV_ICONS.get(
                key,
                "•",
            )

            button = QPushButton(
                f"  {icon}     {label}"
            )

            button.setMinimumHeight(
                43
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False, name=key:
                self.show_page(name)
            )

            self._nav_buttons[
                key
            ] = button

            layout.addWidget(
                button
            )

        layout.addStretch(
            1
        )

        # -------------------------------------------------
        # Bottom divider
        # -------------------------------------------------

        divider = QFrame()

        divider.setFixedHeight(
            1
        )

        divider.setStyleSheet(
            f"background:{BORDER};"
        )

        layout.addWidget(
            divider
        )

        layout.addSpacing(
            7
        )

        # -------------------------------------------------
        # Market time label
        # -------------------------------------------------

        market_title = QLabel(
            "MARKET TIME"
        )

        market_title.setStyleSheet(
            """
            color: #4ca8ff;
            font-size: 10px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            market_title
        )

        # -------------------------------------------------
        # Sidebar clock
        # -------------------------------------------------

        self.sidebar_clock = QLabel(
            "--:--:--"
        )

        self.sidebar_clock.setStyleSheet(
            """
            color: #ffffff;
            font-size: 17px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.sidebar_clock
        )

        # -------------------------------------------------
        # Market status
        # -------------------------------------------------

        self.sidebar_market_status = QLabel(
            "NSE   ● OPEN\nBSE   ● OPEN"
        )

        self.sidebar_market_status.setStyleSheet(
            """
            color: #25dc7b;
            font-size: 11px;
            font-weight: 700;
            line-height: 150%;
            """
        )

        layout.addSpacing(
            4
        )

        layout.addWidget(
            self.sidebar_market_status
        )

        return sidebar


    # =====================================================
    # HEADER
    # =====================================================

    def _create_header(self) -> QFrame:
        """
        Approved StockVersity live-market header.

        Visible:
            NIFTY 50
            BANK NIFTY
            INDIA VIX
            BTC/USD
            GOLD/USD
            SILVER/USD

        Hidden:
            FIN NIFTY
            Search
            Market-open box
        """

        header = QFrame()

        header.setObjectName(
            "mainHeader"
        )

        header.setFixedHeight(
            84
        )

        header.setStyleSheet(
            f"""
            QFrame#mainHeader {{
                background: {HEADER_BG};
                border-bottom: 1px solid {BORDER};
            }}
            """
        )

        layout = QHBoxLayout(
            header
        )

        layout.setContentsMargins(
            12,
            7,
            12,
            7,
        )

        layout.setSpacing(
            6
        )

        # -------------------------------------------------
        # LIVE NSE INDEX CARDS
        # -------------------------------------------------

        # FINNIFTY intentionally remains in DashboardPage
        # for MarketController compatibility but is NOT
        # shown in this header.

        for key in (
            "NIFTY",
            "BANKNIFTY",
            "INDIAVIX",
        ):

            card = (
                self.dashboard_page
                .index_cards[key]
            )

            card.setMinimumWidth(
                155
            )

            card.setMaximumWidth(
                190
            )

            card.setMinimumHeight(
                66
            )

            layout.addWidget(
                card
            )

        # -------------------------------------------------
        # BTC/USD
        # -------------------------------------------------

        self.btc_header_card = (
            self._create_asset_header_card(
                title="BTC / USD",
                price="$69,450.20",
                change="+1.82%",
                accent=ORANGE,
                icon_text="₿",
            )
        )

        layout.addWidget(
            self.btc_header_card
        )

        # -------------------------------------------------
        # GOLD/USD
        # -------------------------------------------------

        self.gold_header_card = (
            self._create_asset_header_card(
                title="GOLD / USD",
                price="$2,351.60",
                change="+0.45%",
                accent=GOLD,
                icon_text="●",
            )
        )

        layout.addWidget(
            self.gold_header_card
        )

        # -------------------------------------------------
        # SILVER/USD
        # -------------------------------------------------

        self.silver_header_card = (
            self._create_asset_header_card(
                title="SILVER / USD",
                price="$30.12",
                change="+0.72%",
                accent=SILVER,
                icon_text="◆",
            )
        )

        layout.addWidget(
            self.silver_header_card
        )

        layout.addStretch(
            1
        )

        # -------------------------------------------------
        # Controls
        # -------------------------------------------------

        controls = (
            ("☀", "#ffc21c"),
            ("☾", "#a9b7ca"),
            ("⚙", "#dce5f2"),
        )

        for symbol, color in controls:

            button = QPushButton(
                symbol
            )

            button.setFixedSize(
                36,
                36,
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: #091624;
                    border: 1px solid #1c3047;
                    border-radius: 18px;
                    color: {color};
                    font-size: 17px;
                    font-weight: 700;
                }}

                QPushButton:hover {{
                    background: #12243a;
                    border-color: #315277;
                    color: #ffffff;
                }}
                """
            )

            layout.addWidget(
                button
            )

        # -------------------------------------------------
        # Profile
        # -------------------------------------------------

        profile = QLabel(
            "RR"
        )

        profile.setFixedSize(
            38,
            38,
        )

        profile.setAlignment(
            Qt.AlignCenter
        )

        profile.setStyleSheet(
            """
            background: #163a72;
            border: 1px solid #3264a8;
            border-radius: 19px;
            color: #ffffff;
            font-size: 12px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            profile
        )

        # -------------------------------------------------
        # UI clock
        # -------------------------------------------------

        self.ui_clock_timer = (
            QTimer(self)
        )

        self.ui_clock_timer.timeout.connect(
            self._update_shell_clock
        )

        self.ui_clock_timer.start(
            1000
        )

        self._update_shell_clock()

        return header


    # =====================================================
    # HEADER ASSET CARD
    # =====================================================

    def _create_asset_header_card(
        self,
        title: str,
        price: str,
        change: str,
        accent: str,
        icon_text: str,
    ) -> QFrame:
        """
        Create BTC / Gold / Silver quote card.
        """

        card = QFrame()

        card.setObjectName(
            "assetHeaderCard"
        )

        card.setMinimumWidth(
            155
        )

        card.setMaximumWidth(
            190
        )

        card.setFixedHeight(
            66
        )

        card.setStyleSheet(
            f"""
            QFrame#assetHeaderCard {{
                background: #091624;
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            """
        )

        row = QHBoxLayout(
            card
        )

        row.setContentsMargins(
            9,
            6,
            9,
            6,
        )

        row.setSpacing(
            8
        )

        # -------------------------------------------------
        # Asset icon
        # -------------------------------------------------

        icon = QLabel(
            icon_text
        )

        icon.setFixedSize(
            30,
            30,
        )

        icon.setAlignment(
            Qt.AlignCenter
        )

        icon.setStyleSheet(
            f"""
            background: {accent};
            color: #ffffff;
            border-radius: 15px;
            font-size: 15px;
            font-weight: 900;
            """
        )

        row.addWidget(
            icon
        )

        # -------------------------------------------------
        # Text area
        # -------------------------------------------------

        text_box = QWidget()

        text_layout = QVBoxLayout(
            text_box
        )

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            0
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            """
            color: #cbd6e5;
            font-size: 11px;
            font-weight: 700;
            """
        )

        price_label = QLabel(
            price
        )

        price_label.setStyleSheet(
            """
            color: #ffffff;
            font-size: 15px;
            font-weight: 800;
            """
        )

        change_label = QLabel(
            change
        )

        change_label.setStyleSheet(
            """
            color: #20df79;
            font-size: 11px;
            font-weight: 800;
            """
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            price_label
        )

        text_layout.addWidget(
            change_label
        )

        row.addWidget(
            text_box,
            1,
        )

        return card


    # =====================================================
    # FOOTER
    # =====================================================

    def _create_footer(self) -> QFrame:
        """
        Create larger readable application footer.
        """

        footer = QFrame()

        footer.setObjectName(
            "mainFooter"
        )

        footer.setFixedHeight(
            38
        )

        footer.setStyleSheet(
            f"""
            QFrame#mainFooter {{
                background: {FOOTER_BG};
                border-top: 1px solid {BORDER};
            }}
            """
        )

        layout = QHBoxLayout(
            footer
        )

        layout.setContentsMargins(
            18,
            0,
            18,
            0,
        )

        layout.setSpacing(
            15
        )

        # -------------------------------------------------
        # NSE
        # -------------------------------------------------

        self.footer_nse = QLabel(
            "NSE   ●   OPEN"
        )

        nse = self.footer_nse

        nse.setStyleSheet(
            """
            color: #e8eef8;
            font-size: 12px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            nse
        )

        # -------------------------------------------------
        # Separator
        # -------------------------------------------------

        sep1 = QLabel("|")

        sep1.setStyleSheet(
            """
            color:#40516a;
            font-size:14px;
            """
        )

        layout.addWidget(
            sep1
        )

        # -------------------------------------------------
        # BSE
        # -------------------------------------------------

        self.footer_bse = QLabel(
            "BSE   ●   OPEN"
        )

        bse = self.footer_bse

        bse.setStyleSheet(
            """
            color: #e8eef8;
            font-size: 12px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            bse
        )

        # -------------------------------------------------
        # Separator
        # -------------------------------------------------

        sep2 = QLabel("|")

        sep2.setStyleSheet(
            """
            color:#40516a;
            font-size:14px;
            """
        )

        layout.addWidget(
            sep2
        )

        # -------------------------------------------------
        # Powered by
        # -------------------------------------------------

        source = QLabel(
            "Powered by StockVersity Engine"
        )

        source.setStyleSheet(
            """
            color: #8d9db2;
            font-size: 12px;
            font-weight: 500;
            """
        )

        layout.addWidget(
            source
        )

        layout.addStretch(
            1
        )

        # -------------------------------------------------
        # Live status
        # -------------------------------------------------

        self.footer_status = QLabel(
            "●  REAL-TIME      ●  CONNECTED"
        )

        self.footer_status.setStyleSheet(
            """
            color: #28df7c;
            font-size: 12px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.footer_status
        )

        return footer


    # =====================================================
    # CLOCK / MARKET SESSION
    # =====================================================

    def _update_shell_clock(
        self,
    ) -> None:
        """
        Update sidebar clock and NSE/BSE session status.
        """

        now = datetime.now()

        current_time = (
            now.strftime(
                "%H:%M:%S"
            )
        )

        # ---------------------------------------------
        # Sidebar clock
        # ---------------------------------------------

        if hasattr(
            self,
            "sidebar_clock",
        ):

            self.sidebar_clock.setText(
                current_time
            )

        # ---------------------------------------------
        # Indian market session
        # ---------------------------------------------

        weekday = (
            now.weekday()
        )

        minutes_now = (
            now.hour * 60
            + now.minute
        )

        market_open_minutes = (
            9 * 60 + 15
        )

        market_close_minutes = (
            15 * 60 + 30
        )

        is_weekday = (
            weekday < 5
        )

        is_market_hours = (
            market_open_minutes
            <= minutes_now
            <= market_close_minutes
        )

        market_open = (
            is_weekday
            and is_market_hours
        )

        # ---------------------------------------------
        # Sidebar market status
        # ---------------------------------------------

        if hasattr(
            self,
            "sidebar_market_status",
        ):

            if market_open:

                self.sidebar_market_status.setText(
                    "NSE   ● OPEN\n"
                    "BSE   ● OPEN"
                )

                self.sidebar_market_status.setStyleSheet(
                    """
                    color: #25dc7b;
                    font-size: 11px;
                    font-weight: 700;
                    """
                )

            else:

                self.sidebar_market_status.setText(
                    "NSE   ● CLOSED\n"
                    "BSE   ● CLOSED"
                )

                self.sidebar_market_status.setStyleSheet(
                    """
                    color: #ff5364;
                    font-size: 11px;
                    font-weight: 700;
                    """
                )


        # ---------------------------------------------
        # Footer market status
        # ---------------------------------------------

        footer_state = (
            "OPEN"
            if market_open
            else "CLOSED"
        )

        footer_color = (
            "#25dc7b"
            if market_open
            else "#ff5364"
        )

        if hasattr(
            self,
            "footer_nse",
        ):

            self.footer_nse.setText(
                f"NSE   ●   {footer_state}"
            )

            self.footer_nse.setStyleSheet(
                f"""
                color: {footer_color};
                font-size: 12px;
                font-weight: 700;
                """
            )

        if hasattr(
            self,
            "footer_bse",
        ):

            self.footer_bse.setText(
                f"BSE   ●   {footer_state}"
            )

            self.footer_bse.setStyleSheet(
                f"""
                color: {footer_color};
                font-size: 12px;
                font-weight: 700;
                """
            )


    # =====================================================
    # PAGE MANAGEMENT
    # =====================================================

    def _add_page(
        self,
        key: str,
        page: QWidget,
    ) -> None:

        self._pages[
            key
        ] = page

        self.stack.addWidget(
            page
        )


    # =====================================================
    # PLACEHOLDER PAGE
    # =====================================================

    def _placeholder(
        self,
        key: str,
    ) -> QWidget:

        page = QWidget()

        page.setStyleSheet(
            f"background:{BG};"
        )

        layout = QVBoxLayout(
            page
        )

        layout.setAlignment(
            Qt.AlignCenter
        )

        title = QLabel(
            self.PAGES[key]
        )

        title.setFont(
            QFont(
                "Segoe UI",
                28,
                QFont.Bold,
            )
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            color:#ffffff;
            font-size:28px;
            font-weight:800;
            """
        )

        detail = QLabel(
            "This workspace is ready for its next module."
        )

        detail.setAlignment(
            Qt.AlignCenter
        )

        detail.setStyleSheet(
            """
            color:#95a3b8;
            font-size:15px;
            """
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            detail
        )

        return page


    # =====================================================
    # SHOW PAGE
    # =====================================================

    def show_page(
        self,
        key: str,
    ) -> None:

        if key not in self._pages:

            self._add_page(
                key,
                self._placeholder(
                    key
                ),
            )

        self.stack.setCurrentWidget(
            self._pages[key]
        )

        for (
            name,
            button,
        ) in self._nav_buttons.items():

            button.setProperty(
                "active",
                name == key,
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

            button.update()


    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(
        self,
    ) -> None:
        """
        Stop live services during application shutdown.
        """

        # ---------------------------------------------
        # Stop controller
        # ---------------------------------------------

        if self.market_controller is not None:

            try:

                stop_method = getattr(
                    self.market_controller,
                    "stop",
                    None,
                )

                if callable(
                    stop_method
                ):

                    stop_method()

            except Exception as exc:

                print(
                    "[SHUTDOWN] "
                    "MarketController stop failed:",
                    exc,
                )

        # ---------------------------------------------
        # Stop Upstox provider
        # ---------------------------------------------

        if self.upstox_provider is not None:

            try:

                stop_method = getattr(
                    self.upstox_provider,
                    "stop",
                    None,
                )

                if callable(
                    stop_method
                ):

                    stop_method()

            except Exception as exc:

                print(
                    "[SHUTDOWN] "
                    "UpstoxProvider stop failed:",
                    exc,
                )

        # ---------------------------------------------
        # Stop UI clock
        # ---------------------------------------------

        if hasattr(
            self,
            "ui_clock_timer",
        ):

            try:

                self.ui_clock_timer.stop()

            except Exception:

                pass


    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(
        self,
        event: QCloseEvent,
    ) -> None:

        self.cleanup()

        event.accept()