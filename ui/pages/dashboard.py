"""
=========================================================
StockVersity Scanner Pro
Dashboard Page
Version : 4.0
Powered By : AI
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    Qt,
    Signal,
    QTimer,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
    QPushButton,
    QScrollArea,
)

from ui.widgets.info_card import InfoCard
from ui.widgets.opportunities_table import OpportunitiesTable


class DashboardPage(QWidget):

    """
    Main Professional Dashboard
    """

    refreshRequested = Signal()
    openScannerRequested = Signal()

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.market_data = {}

        self.statistics = {}

        self.scan_results = []

        self.build_ui()

        self.start_refresh_timer()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(

            15,

            15,

            15,

            15

        )

        root.setSpacing(15)

        # ------------------------------------------
        # Scroll Area
        # ------------------------------------------

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        self.scroll.setFrameShape(

            QFrame.NoFrame

        )

        root.addWidget(

            self.scroll

        )

        self.container = QWidget()

        self.scroll.setWidget(

            self.container

        )

        self.layout = QVBoxLayout(

            self.container

        )

        self.layout.setSpacing(15)

        self.create_header()

        self.create_summary_cards()

        self.create_market_section()

        self.create_tables()

    # =====================================================
    # HEADER
    # =====================================================

    def create_header(self):

        frame = QFrame()

        layout = QHBoxLayout(frame)

        title = QLabel(

            "ðŸ“Š Trading Dashboard"

        )

        title.setObjectName(

            "dashboardTitle"

        )

        layout.addWidget(title)

        layout.addStretch()

        self.last_update = QLabel(

            "Never"

        )

        layout.addWidget(

            QLabel("Updated :")

        )

        layout.addWidget(

            self.last_update

        )

        self.refresh_button = QPushButton(

            "Refresh"

        )

        self.refresh_button.clicked.connect(

            self.refreshRequested.emit

        )

        layout.addWidget(

            self.refresh_button

        )

        self.layout.addWidget(

            frame

        )

    # =====================================================
    # SUMMARY CARDS
    # =====================================================

    def create_summary_cards(self):

        grid = QGridLayout()

        grid.setHorizontalSpacing(12)

        grid.setVerticalSpacing(12)

        self.total_card = InfoCard(

            "Stocks",

            "--"

        )

        self.buy_card = InfoCard(

            "Buy Signals",

            "--"

        )

        self.sell_card = InfoCard(

            "Sell Signals",

            "--"

        )

        self.confidence_card = InfoCard(

            "AI Confidence",

            "--"

        )

        grid.addWidget(

            self.total_card,

            0,

            0

        )

        grid.addWidget(

            self.buy_card,

            0,

            1

        )

        grid.addWidget(

            self.sell_card,

            0,

            2

        )

        grid.addWidget(

            self.confidence_card,

            0,

            3

        )

        self.layout.addLayout(

            grid

        )

    # =====================================================
    # MARKET OVERVIEW
    # =====================================================

    def create_market_section(self):

        frame = QFrame()

        layout = QGridLayout(frame)

        self.nifty = InfoCard(

            "NIFTY",

            "--"

        )

        self.banknifty = InfoCard(

            "BANK NIFTY",

            "--"

        )

        self.sensex = InfoCard(

            "SENSEX",

            "--"

        )

        self.vix = InfoCard(

            "INDIA VIX",

            "--"

        )

        layout.addWidget(

            self.nifty,

            0,

            0

        )

        layout.addWidget(

            self.banknifty,

            0,

            1

        )

        layout.addWidget(

            self.sensex,

            0,

            2

        )

        layout.addWidget(

            self.vix,

            0,

            3

        )

        self.layout.addWidget(

            frame

        )

    # =====================================================
    # TABLES
    # =====================================================

    def create_tables(self):

        self.opportunities = OpportunitiesTable()

        self.layout.addWidget(

            self.opportunities,

            1

        )
            # =====================================================
    # AUTO REFRESH TIMER
    # =====================================================

    def start_refresh_timer(self):

        self.refresh_timer = QTimer(self)

        self.refresh_timer.timeout.connect(

            self.auto_refresh

        )

        self.refresh_timer.start(

            30000

        )  # 30 Seconds

    # =====================================================
    # AUTO REFRESH
    # =====================================================

    def auto_refresh(self):

        self.refreshRequested.emit()

    # =====================================================
    # UPDATE DASHBOARD
    # =====================================================

    def update_dashboard(

        self,

        market_data: dict,

        statistics: dict,

        scan_results: list

    ):

        self.market_data = market_data or {}

        self.statistics = statistics or {}

        self.scan_results = scan_results or []

        self.update_summary_cards()

        self.update_market_cards()

        self.update_opportunities()

        self.update_timestamp()

    # =====================================================
    # SUMMARY CARDS
    # =====================================================

    def update_summary_cards(self):

        self.total_card.set_value(

            str(

                self.statistics.get(

                    "total_stocks",

                    0

                )

            )

        )

        self.buy_card.set_value(

            str(

                self.statistics.get(

                    "buy_signals",

                    0

                )

            )

        )

        self.sell_card.set_value(

            str(

                self.statistics.get(

                    "sell_signals",

                    0

                )

            )

        )

        confidence = self.statistics.get(

            "confidence",

            0

        )

        self.confidence_card.set_value(

            f"{confidence}%"

        )

    # =====================================================
    # MARKET CARDS
    # =====================================================

    def update_market_cards(self):

        self.nifty.set_value(

            self.market_data.get(

                "nifty",

                "--"

            )

        )

        self.banknifty.set_value(

            self.market_data.get(

                "banknifty",

                "--"

            )

        )

        self.sensex.set_value(

            self.market_data.get(

                "sensex",

                "--"

            )

        )

        self.vix.set_value(

            self.market_data.get(

                "vix",

                "--"

            )

        )

    # =====================================================
    # OPPORTUNITIES
    # =====================================================

    def update_opportunities(self):

        self.opportunities.set_data(

            self.scan_results

        )

    # =====================================================
    # LAST UPDATE
    # =====================================================

    def update_timestamp(self):

        self.last_update.setText(

            datetime.now().strftime(

                "%d-%b-%Y %H:%M:%S"

            )

        )

    # =====================================================
    # CLEAR DASHBOARD
    # =====================================================

    def clear_dashboard(self):

        self.market_data.clear()

        self.statistics.clear()

        self.scan_results.clear()

        self.total_card.set_value("--")

        self.buy_card.set_value("--")

        self.sell_card.set_value("--")

        self.confidence_card.set_value("--")

        self.nifty.set_value("--")

        self.banknifty.set_value("--")

        self.sensex.set_value("--")

        self.vix.set_value("--")

        self.opportunities.clear()

        self.last_update.setText("Never")

    # =====================================================
    # REFRESH NOW
    # =====================================================

    def refresh_now(self):

        self.refreshRequested.emit()

    # =====================================================
    # OPEN SCANNER
    # =====================================================

    def open_scanner(self):

        self.openScannerRequested.emit()
            # =====================================================
    # ADVANCED PANELS
    # =====================================================

    def create_advanced_panels(self):

        """
        Intraday / Swing / Positional Layout
        """

        container = QHBoxLayout()

        # -------------------------------------------------
        # Intraday
        # -------------------------------------------------

        self.intraday_frame = QFrame()

        intraday_layout = QVBoxLayout(

            self.intraday_frame

        )

        intraday_title = QLabel(

            "âš¡ Intraday Opportunities"

        )

        intraday_title.setObjectName(

            "sectionTitle"

        )

        self.intraday_table = OpportunitiesTable()

        intraday_layout.addWidget(

            intraday_title

        )

        intraday_layout.addWidget(

            self.intraday_table

        )

        # -------------------------------------------------
        # Swing
        # -------------------------------------------------

        self.swing_frame = QFrame()

        swing_layout = QVBoxLayout(

            self.swing_frame

        )

        swing_title = QLabel(

            "ðŸ“ˆ Swing Opportunities"

        )

        swing_title.setObjectName(

            "sectionTitle"

        )

        self.swing_table = OpportunitiesTable()

        swing_layout.addWidget(

            swing_title

        )

        swing_layout.addWidget(

            self.swing_table

        )

        # -------------------------------------------------
        # Positional
        # -------------------------------------------------

        self.positional_frame = QFrame()

        positional_layout = QVBoxLayout(

            self.positional_frame

        )

        positional_title = QLabel(

            "ðŸ† Positional Opportunities"

        )

        positional_title.setObjectName(

            "sectionTitle"

        )

        self.positional_table = OpportunitiesTable()

        positional_layout.addWidget(

            positional_title

        )

        positional_layout.addWidget(

            self.positional_table

        )

        container.addWidget(

            self.intraday_frame

        )

        container.addWidget(

            self.swing_frame

        )

        container.addWidget(

            self.positional_frame

        )

        self.layout.addLayout(

            container

        )

    # =====================================================
    # AI RECOMMENDATION PANEL
    # =====================================================

    def create_ai_panel(self):

        frame = QFrame()

        layout = QGridLayout(frame)

        self.ai_buy = InfoCard(

            "Strong Buy",

            "0"

        )

        self.ai_watch = InfoCard(

            "Watchlist",

            "0"

        )

        self.ai_sell = InfoCard(

            "Strong Sell",

            "0"

        )

        self.ai_score = InfoCard(

            "AI Score",

            "--"

        )

        layout.addWidget(

            self.ai_buy,

            0,

            0

        )

        layout.addWidget(

            self.ai_watch,

            0,

            1

        )

        layout.addWidget(

            self.ai_sell,

            0,

            2

        )

        layout.addWidget(

            self.ai_score,

            0,

            3

        )

        self.layout.addWidget(

            frame

        )

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def create_sector_panel(self):

        frame = QFrame()

        layout = QVBoxLayout(frame)

        title = QLabel(

            "ðŸ­ Sector Rotation"

        )

        title.setObjectName(

            "sectionTitle"

        )

        self.sector_table = OpportunitiesTable()

        layout.addWidget(title)

        layout.addWidget(

            self.sector_table

        )

        self.layout.addWidget(frame)

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def create_market_breadth_panel(self):

        frame = QFrame()

        layout = QGridLayout(frame)

        self.advance_card = InfoCard(

            "Advances",

            "--"

        )

        self.decline_card = InfoCard(

            "Declines",

            "--"

        )

        self.adr_card = InfoCard(

            "A/D Ratio",

            "--"

        )

        self.new_high_card = InfoCard(

            "New Highs",

            "--"

        )

        layout.addWidget(

            self.advance_card,

            0,

            0

        )

        layout.addWidget(

            self.decline_card,

            0,

            1

        )

        layout.addWidget(

            self.adr_card,

            0,

            2

        )

        layout.addWidget(

            self.new_high_card,

            0,

            3

        )

        self.layout.addWidget(frame)

    # =====================================================
    # BUILD COMPLETE DASHBOARD
    # =====================================================

    def build_professional_dashboard(self):

        self.create_advanced_panels()

        self.create_ai_panel()

        self.create_sector_panel()

        self.create_market_breadth_panel()
            # =====================================================
    # UPDATE PROFESSIONAL PANELS
    # =====================================================

    def update_professional_dashboard(
        self,
        dashboard_data: dict
    ):

        if not dashboard_data:
            return

        self.update_intraday_panel(
            dashboard_data.get(
                "intraday",
                []
            )
        )

        self.update_swing_panel(
            dashboard_data.get(
                "swing",
                []
            )
        )

        self.update_positional_panel(
            dashboard_data.get(
                "positional",
                []
            )
        )

        self.update_ai_panel_data(
            dashboard_data.get(
                "ai",
                {}
            )
        )

        self.update_sector_rotation(
            dashboard_data.get(
                "sectors",
                []
            )
        )

        self.update_market_breadth(
            dashboard_data.get(
                "breadth",
                {}
            )
        )

    # =====================================================
    # INTRADAY PANEL
    # =====================================================

    def update_intraday_panel(
        self,
        stocks: list
    ):

        self.intraday_table.set_data(
            stocks
        )

    # =====================================================
    # SWING PANEL
    # =====================================================

    def update_swing_panel(
        self,
        stocks: list
    ):

        self.swing_table.set_data(
            stocks
        )

    # =====================================================
    # POSITIONAL PANEL
    # =====================================================

    def update_positional_panel(
        self,
        stocks: list
    ):

        self.positional_table.set_data(
            stocks
        )

    # =====================================================
    # AI PANEL
    # =====================================================

    def update_ai_panel_data(
        self,
        ai: dict
    ):

        self.ai_buy.set_value(
            str(
                ai.get(
                    "buy",
                    0
                )
            )
        )

        self.ai_watch.set_value(
            str(
                ai.get(
                    "watch",
                    0
                )
            )
        )

        self.ai_sell.set_value(
            str(
                ai.get(
                    "sell",
                    0
                )
            )
        )

        self.ai_score.set_value(
            f"{ai.get('score',0)}%"
        )

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def update_sector_rotation(
        self,
        sectors: list
    ):

        self.sector_table.set_data(
            sectors
        )

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def update_market_breadth(
        self,
        breadth: dict
    ):

        self.advance_card.set_value(
            str(
                breadth.get(
                    "advances",
                    "--"
                )
            )
        )

        self.decline_card.set_value(
            str(
                breadth.get(
                    "declines",
                    "--"
                )
            )
        )

        self.adr_card.set_value(
            str(
                breadth.get(
                    "ad_ratio",
                    "--"
                )
            )
        )

        self.new_high_card.set_value(
            str(
                breadth.get(
                    "new_highs",
                    "--"
                )
            )
        )

    # =====================================================
    # FILTER SCAN RESULTS
    # =====================================================

    def categorize_scan_results(self):

        intraday = []

        swing = []

        positional = []

        for stock in self.scan_results:

            trade_type = str(
                stock.get(
                    "trade_type",
                    ""
                )
            ).lower()

            if trade_type == "intraday":

                intraday.append(stock)

            elif trade_type == "swing":

                swing.append(stock)

            elif trade_type == "positional":

                positional.append(stock)

        self.update_intraday_panel(
            intraday
        )

        self.update_swing_panel(
            swing
        )

        self.update_positional_panel(
            positional
        )

    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def top_opportunities(
        self,
        limit: int = 5
    ):

        ranked = sorted(

            self.scan_results,

            key=lambda x: x.get(
                "score",
                0
            ),

            reverse=True

        )

        return ranked[:limit]

    # =====================================================
    # REFRESH ALL PANELS
    # =====================================================

    def refresh_panels(self):

        self.update_summary_cards()

        self.update_market_cards()

        self.update_opportunities()

        self.categorize_scan_results()

        self.update_timestamp()
            # =====================================================
    # ADVANCED ANALYTICS PANELS
    # =====================================================

    def create_analytics_panels(self):

        analytics_layout = QGridLayout()

        analytics_layout.setHorizontalSpacing(12)

        analytics_layout.setVerticalSpacing(12)

        # -------------------------------------------------
        # AI Market Prediction
        # -------------------------------------------------

        self.market_prediction_card = InfoCard(
            "AI Market Prediction",
            "--"
        )

        # -------------------------------------------------
        # Market Sentiment
        # -------------------------------------------------

        self.market_sentiment_card = InfoCard(
            "Market Sentiment",
            "--"
        )

        # -------------------------------------------------
        # Market Regime
        # -------------------------------------------------

        self.market_regime_card = InfoCard(
            "Market Regime",
            "--"
        )

        # -------------------------------------------------
        # Risk Score
        # -------------------------------------------------

        self.risk_score_card = InfoCard(
            "Risk Score",
            "--"
        )

        # -------------------------------------------------
        # Liquidity Score
        # -------------------------------------------------

        self.liquidity_card = InfoCard(
            "Liquidity",
            "--"
        )

        # -------------------------------------------------
        # Volume Strength
        # -------------------------------------------------

        self.volume_strength_card = InfoCard(
            "Volume Strength",
            "--"
        )

        # -------------------------------------------------
        # Institutional Activity
        # -------------------------------------------------

        self.institutional_card = InfoCard(
            "Institutional Activity",
            "--"
        )

        # -------------------------------------------------
        # Market Confidence
        # -------------------------------------------------

        self.market_confidence_card = InfoCard(
            "AI Confidence",
            "--"
        )

        analytics_layout.addWidget(
            self.market_prediction_card,
            0,
            0
        )

        analytics_layout.addWidget(
            self.market_sentiment_card,
            0,
            1
        )

        analytics_layout.addWidget(
            self.market_regime_card,
            0,
            2
        )

        analytics_layout.addWidget(
            self.risk_score_card,
            0,
            3
        )

        analytics_layout.addWidget(
            self.liquidity_card,
            1,
            0
        )

        analytics_layout.addWidget(
            self.volume_strength_card,
            1,
            1
        )

        analytics_layout.addWidget(
            self.institutional_card,
            1,
            2
        )

        analytics_layout.addWidget(
            self.market_confidence_card,
            1,
            3
        )

        self.layout.addLayout(
            analytics_layout
        )

    # =====================================================
    # UPDATE ANALYTICS
    # =====================================================

    def update_analytics(
        self,
        analytics: dict
    ):

        if not analytics:
            return

        self.market_prediction_card.set_value(
            analytics.get(
                "prediction",
                "--"
            )
        )

        self.market_sentiment_card.set_value(
            analytics.get(
                "sentiment",
                "--"
            )
        )

        self.market_regime_card.set_value(
            analytics.get(
                "regime",
                "--"
            )
        )

        self.risk_score_card.set_value(
            str(
                analytics.get(
                    "risk_score",
                    "--"
                )
            )
        )

        self.liquidity_card.set_value(
            str(
                analytics.get(
                    "liquidity_score",
                    "--"
                )
            )
        )

        self.volume_strength_card.set_value(
            analytics.get(
                "volume_strength",
                "--"
            )
        )

        self.institutional_card.set_value(
            analytics.get(
                "institutional_activity",
                "--"
            )
        )

        confidence = analytics.get(
            "confidence",
            "--"
        )

        if confidence != "--":
            confidence = f"{confidence}%"

        self.market_confidence_card.set_value(
            confidence
        )

    # =====================================================
    # UPDATE COMPLETE ANALYTICS
    # =====================================================

    def refresh_analytics(
        self,
        analytics: dict
    ):

        self.update_analytics(
            analytics
        )

    # =====================================================
    # CLEAR ANALYTICS
    # =====================================================

    def clear_analytics(self):

        self.market_prediction_card.set_value("--")

        self.market_sentiment_card.set_value("--")

        self.market_regime_card.set_value("--")

        self.risk_score_card.set_value("--")

        self.liquidity_card.set_value("--")

        self.volume_strength_card.set_value("--")

        self.institutional_card.set_value("--")

        self.market_confidence_card.set_value("--")
            # =====================================================
    # LIVE TRADING PANELS
    # =====================================================

    def create_live_trading_panels(self):

        """
        Professional Trading Widgets
        """

        layout = QGridLayout()

        layout.setHorizontalSpacing(12)

        layout.setVerticalSpacing(12)

        # -------------------------------------------------
        # Live Watchlist
        # -------------------------------------------------

        self.watchlist_table = OpportunitiesTable()

        watchlist_frame = QFrame()

        watchlist_layout = QVBoxLayout(watchlist_frame)

        watchlist_layout.addWidget(
            QLabel("â­ Live Watchlist")
        )

        watchlist_layout.addWidget(
            self.watchlist_table
        )

        # -------------------------------------------------
        # Recent AI Alerts
        # -------------------------------------------------

        self.alert_table = OpportunitiesTable()

        alert_frame = QFrame()

        alert_layout = QVBoxLayout(alert_frame)

        alert_layout.addWidget(
            QLabel("ðŸš¨ AI Alerts")
        )

        alert_layout.addWidget(
            self.alert_table
        )

        # -------------------------------------------------
        # F&O Activity
        # -------------------------------------------------

        self.fo_table = OpportunitiesTable()

        fo_frame = QFrame()

        fo_layout = QVBoxLayout(fo_frame)

        fo_layout.addWidget(
            QLabel("ðŸ“Š F&O Activity")
        )

        fo_layout.addWidget(
            self.fo_table
        )

        # -------------------------------------------------
        # Breakout Candidates
        # -------------------------------------------------

        self.breakout_table = OpportunitiesTable()

        breakout_frame = QFrame()

        breakout_layout = QVBoxLayout(
            breakout_frame
        )

        breakout_layout.addWidget(
            QLabel("ðŸ”¥ Breakout Candidates")
        )

        breakout_layout.addWidget(
            self.breakout_table
        )

        layout.addWidget(
            watchlist_frame,
            0,
            0
        )

        layout.addWidget(
            alert_frame,
            0,
            1
        )

        layout.addWidget(
            fo_frame,
            1,
            0
        )

        layout.addWidget(
            breakout_frame,
            1,
            1
        )

        self.layout.addLayout(layout)

    # =====================================================
    # UPDATE WATCHLIST
    # =====================================================

    def update_watchlist(
        self,
        stocks: list
    ):

        self.watchlist_table.set_data(
            stocks
        )

    # =====================================================
    # UPDATE ALERTS
    # =====================================================

    def update_alerts(
        self,
        alerts: list
    ):

        self.alert_table.set_data(
            alerts
        )

    # =====================================================
    # UPDATE F&O
    # =====================================================

    def update_fo_activity(
        self,
        activity: list
    ):

        self.fo_table.set_data(
            activity
        )

    # =====================================================
    # UPDATE BREAKOUTS
    # =====================================================

    def update_breakouts(
        self,
        stocks: list
    ):

        self.breakout_table.set_data(
            stocks
        )

    # =====================================================
    # TOP GAINERS
    # =====================================================

    def top_gainers(
        self,
        limit: int = 10
    ):

        gainers = sorted(

            self.scan_results,

            key=lambda x: x.get(
                "change_percent",
                0
            ),

            reverse=True

        )

        return gainers[:limit]

    # =====================================================
    # TOP LOSERS
    # =====================================================

    def top_losers(
        self,
        limit: int = 10
    ):

        losers = sorted(

            self.scan_results,

            key=lambda x: x.get(
                "change_percent",
                0
            )
        )

        return losers[:limit]

    # =====================================================
    # HIGH VOLUME MOVERS
    # =====================================================

    def high_volume_movers(
        self,
        limit: int = 10
    ):

        movers = sorted(

            self.scan_results,

            key=lambda x: x.get(
                "relative_volume",
                0
            ),

            reverse=True

        )

        return movers[:limit]

    # =====================================================
    # HIGH AI CONFIDENCE
    # =====================================================

    def highest_confidence(
        self,
        limit: int = 10
    ):

        ranked = sorted(

            self.scan_results,

            key=lambda x: x.get(
                "confidence",
                0
            ),

            reverse=True

        )

        return ranked[:limit]

    # =====================================================
    # REFRESH LIVE PANELS
    # =====================================================

    def refresh_live_panels(self):

        self.update_watchlist(
            self.highest_confidence(20)
        )

        self.update_breakouts(
            self.top_opportunities(20)
        )

    # =====================================================
    # REFRESH COMPLETE LIVE DASHBOARD
    # =====================================================

    def refresh_live_dashboard(
        self,
        live_data: dict
    ):

        if not live_data:
            return

        self.update_watchlist(
            live_data.get(
                "watchlist",
                []
            )
        )

        self.update_alerts(
            live_data.get(
                "alerts",
                []
            )
        )

        self.update_fo_activity(
            live_data.get(
                "fo_activity",
                []
            )
        )

        self.update_breakouts(
            live_data.get(
                "breakouts",
                []
            )
        )
            # =====================================================
    # DASHBOARD STATE
    # =====================================================

    def save_state(self):

        return {

            "market_data": self.market_data,

            "statistics": self.statistics,

            "scan_results": self.scan_results,

            "last_update": self.last_update.text()

        }

    # =====================================================
    # RESTORE STATE
    # =====================================================

    def restore_state(

        self,

        state: dict

    ):

        if not state:

            return

        self.market_data = state.get(

            "market_data",

            {}

        )

        self.statistics = state.get(

            "statistics",

            {}

        )

        self.scan_results = state.get(

            "scan_results",

            []

        )

        self.refresh_panels()

    # =====================================================
    # USER PREFERENCES
    # =====================================================

    def apply_user_preferences(

        self,

        preferences: dict

    ):

        if not preferences:

            return

        refresh_interval = preferences.get(

            "refresh_interval",

            30

        )

        self.refresh_timer.start(

            refresh_interval * 1000

        )

    # =====================================================
    # THEME UPDATED
    # =====================================================

    def theme_changed(

        self,

        theme_name: str

    ):

        self.setProperty(

            "theme",

            theme_name

        )

        self.style().unpolish(self)

        self.style().polish(self)

        self.update()

    # =====================================================
    # PERFORMANCE METRICS
    # =====================================================

    def performance_metrics(self):

        total = len(self.scan_results)

        buy = len(

            [

                s

                for s in self.scan_results

                if str(

                    s.get(

                        "signal",

                        ""

                    )

                ).upper() == "BUY"

            ]

        )

        sell = len(

            [

                s

                for s in self.scan_results

                if str(

                    s.get(

                        "signal",

                        ""

                    )

                ).upper() == "SELL"

            ]

        )

        return {

            "total_stocks": total,

            "buy_signals": buy,

            "sell_signals": sell,

            "updated":

                self.last_update.text()

        }

    # =====================================================
    # KEYBOARD SHORTCUTS
    # =====================================================

    def keyPressEvent(

        self,

        event

    ):

        if event.key() == Qt.Key_F5:

            self.refresh_now()

            return

        if event.key() == Qt.Key_F9:

            self.open_scanner()

            return

        super().keyPressEvent(event)

    # =====================================================
    # EVENT HANDLER
    # =====================================================

    def handle_scan_completed(

        self,

        results: list

    ):

        self.scan_results = results

        self.refresh_panels()

    # =====================================================
    # APPLICATION CONTROLLER
    # =====================================================

    def attach_application_controller(

        self,

        controller

    ):

        self.application_controller = controller

    # =====================================================
    # SERVICE MANAGER
    # =====================================================

    def attach_service_manager(

        self,

        manager

    ):

        self.service_manager = manager

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_status(self):

        return {

            "component":

                "Dashboard",

            "healthy": True,

            "records":

                len(

                    self.scan_results

                ),

            "market_loaded":

                bool(

                    self.market_data

                ),

            "statistics_loaded":

                bool(

                    self.statistics

                )

        }

    # =====================================================
    # RUNTIME DIAGNOSTICS
    # =====================================================

    def diagnostics(self):

        return {

            "component":

                "DashboardPage",

            "performance":

                self.performance_metrics(),

            "health":

                self.health_status(),

            "timestamp":

                datetime.now().isoformat()

        }

    # =====================================================
    # REFRESH EVERYTHING
    # =====================================================

    def refresh_all(self):

        self.refresh_panels()

        self.refresh_live_panels()

        self.update()

        self.repaint()
            # =====================================================
    # RESET DASHBOARD
    # =====================================================

    def reset(self):

        self.market_data = {}

        self.statistics = {}

        self.scan_results = []

        self.clear_dashboard()

        self.clear_analytics()

        if hasattr(self, "intraday_table"):
            self.intraday_table.clear()

        if hasattr(self, "swing_table"):
            self.swing_table.clear()

        if hasattr(self, "positional_table"):
            self.positional_table.clear()

        if hasattr(self, "watchlist_table"):
            self.watchlist_table.clear()

        if hasattr(self, "alert_table"):
            self.alert_table.clear()

        if hasattr(self, "fo_table"):
            self.fo_table.clear()

        if hasattr(self, "breakout_table"):
            self.breakout_table.clear()

        if hasattr(self, "sector_table"):
            self.sector_table.clear()

    # =====================================================
    # COMPONENT INFORMATION
    # =====================================================

    @property
    def component_name(self):

        return "DashboardPage"

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"

    @property
    def version(self):

        return "4.0"

    # =====================================================
    # BUILD INFORMATION
    # =====================================================

    def build_information(self):

        return {

            "application":
                self.application_name,

            "component":
                self.component_name,

            "version":
                self.version,

            "powered_by":
                "AI"

        }

    # =====================================================
    # EXPORT DASHBOARD
    # =====================================================

    def export_dashboard(self):

        return {

            "build":
                self.build_information(),

            "market":
                self.market_data,

            "statistics":
                self.statistics,

            "performance":
                self.performance_metrics(),

            "health":
                self.health_status(),

            "diagnostics":
                self.diagnostics()

        }

    # =====================================================
    # IMPORT DASHBOARD
    # =====================================================

    def import_dashboard(

        self,

        data: dict

    ):

        if not data:

            return

        self.market_data = data.get(

            "market",

            {}

        )

        self.statistics = data.get(

            "statistics",

            {}

        )

        self.refresh_panels()

    # =====================================================
    # ENABLE AUTO REFRESH
    # =====================================================

    def enable_auto_refresh(self):

        if not self.refresh_timer.isActive():

            self.refresh_timer.start(30000)

    # =====================================================
    # DISABLE AUTO REFRESH
    # =====================================================

    def disable_auto_refresh(self):

        if self.refresh_timer.isActive():

            self.refresh_timer.stop()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.disable_auto_refresh()

        self.reset()

    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(self, event):

        self.shutdown()

        super().closeEvent(event)

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<DashboardPage "

            f"stocks={len(self.scan_results)} "

            f"updated='{self.last_update.text()}'>"

        )


# =====================================================
# FACTORY
# =====================================================

def create_dashboard():

    return DashboardPage()


# =====================================================
# END OF FILE
# =====================================================
