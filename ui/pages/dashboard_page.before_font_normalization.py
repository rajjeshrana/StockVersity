"""
StockVersity Scanner Pro
New Dashboard UI
Approved UI Build
"""

from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# =========================================================
# COLORS
# =========================================================

BG = "#07101d"
PANEL = "#0c1727"
PANEL_ALT = "#0f1c2e"
BORDER = "#1d2b40"

TEXT = "#e9eef7"
MUTED = "#8190a6"

BLUE = "#3578ff"
GREEN = "#28d17c"
RED = "#ff5364"
ORANGE = "#ffad42"
PURPLE = "#8b6cff"


# =========================================================
# BASE CARD
# =========================================================

class DashboardCard(QFrame):

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.setObjectName("dashboardCard")

        self.setStyleSheet(
            f"""
            QFrame#dashboardCard {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            """
        )

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            18, 16, 18, 16
        )

        self.layout.setSpacing(12)

        if title:

            title_label = QLabel(title)

            title_label.setStyleSheet(
                f"""
                color: {TEXT};
                font-size: 17px;
                font-weight: 700;
                border: none;
                background: transparent;
                """
            )

            self.layout.addWidget(title_label)


# =========================================================
# LIVE INDEX CARD
# =========================================================

class IndexCard(QFrame):

    def __init__(
        self,
        name: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.name = name
        self.history: List[float] = []

        self.setObjectName("indexCard")

        self.setStyleSheet(
            """
            QFrame#indexCard {
                background: transparent;
                border: none;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(12, 5, 12, 5)
        layout.setSpacing(2)

        self.name_label = QLabel(name)

        self.name_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 11px;
            font-weight: 700;
            """
        )

        self.value_label = QLabel("--")

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 18px;
            font-weight: 700;
            """
        )

        self.change_label = QLabel("--")

        self.change_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 11px;
            font-weight: 600;
            """
        )

        layout.addWidget(self.name_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.change_label)

    def update_data(
        self,
        value: float,
        change: float,
        history: Optional[List[float]] = None,
    ):

        self.value_label.setText(
            f"{value:,.2f}"
        )

        sign = "+" if change > 0 else ""

        self.change_label.setText(
            f"{sign}{change:.2f}%"
        )

        if change > 0:
            color = GREEN
        elif change < 0:
            color = RED
        else:
            color = MUTED

        self.change_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 11px;
            font-weight: 700;
            """
        )

        self.history = list(
            history or []
        )


# =========================================================
# SMALL STAT
# =========================================================

class StatLabel(QWidget):

    def __init__(
        self,
        title: str,
        value: str,
        value_color: str = TEXT,
    ):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QLabel(title)

        title_label.setStyleSheet(
            f"color:{MUTED}; font-size:11px;"
        )

        value_label = QLabel(value)

        value_label.setStyleSheet(
            f"""
            color:{value_color};
            font-size:17px;
            font-weight:700;
            """
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)


# =========================================================
# DASHBOARD PAGE
# =========================================================

class DashboardPage(QWidget):

    stock_requested = Signal(str)
    scanner_requested = Signal(str)
    refresh_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.setObjectName("newDashboard")

        self.setStyleSheet(
            f"""
            QWidget#newDashboard {{
                background: {BG};
            }}
            QLabel {{
                font-family: "Segoe UI";
            }}
            """
        )

        # Compatibility contract used by MarketController.
        self.index_cards: Dict[str, IndexCard] = {
            "NIFTY": IndexCard("NIFTY 50"),
            "BANKNIFTY": IndexCard("BANK NIFTY"),
            "FINNIFTY": IndexCard("FIN NIFTY"),
            "INDIAVIX": IndexCard("INDIA VIX"),
        }

        self._build_ui()


    # =====================================================
    # BUILD
    # =====================================================

    def _build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background: {BG};
            }}

            QScrollBar:vertical {{
                background: {BG};
                width: 8px;
            }}

            QScrollBar::handle:vertical {{
                background: #25344b;
                border-radius: 4px;
                min-height: 30px;
            }}
            """
        )

        content = QWidget()

        content.setMinimumWidth(1380)

        content.setStyleSheet(
            f"background:{BG};"
        )

        self.grid = QGridLayout(content)

        self.grid.setContentsMargins(
            18, 16, 18, 18
        )

        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)

        # ROW 1
        self.grid.addWidget(
            self._top_opportunities(),
            0, 0, 1, 2
        )

        self.grid.addWidget(
            self._sector_strength(),
            0, 2
        )

        self.grid.addWidget(
            self._market_breadth(),
            0, 3
        )

        self.grid.addWidget(
            self._market_heatmap(),
            0, 4
        )

        # ROW 2
        self.grid.addWidget(
            self._scanner_summary(),
            1, 0
        )

        self.grid.addWidget(
            self._top_movers(),
            1, 1
        )

        self.grid.addWidget(
            self._live_alerts(),
            1, 2, 1, 2
        )

        self.grid.addWidget(
            self._watchlist(),
            1, 4
        )

        # ROW 3
        self.grid.addWidget(
            self._market_pulse(),
            2, 0, 1, 2
        )

        self.grid.addWidget(
            self._recent_news(),
            2, 2
        )

        self.grid.addWidget(
            self._institutional_flow(),
            2, 3
        )

        self.grid.addWidget(
            self._derivatives_pulse(),
            2, 4
        )

        for column in range(5):
            self.grid.setColumnStretch(
                column,
                1
            )

        scroll.setWidget(content)

        root.addWidget(scroll)


    # =====================================================
    # HELPERS
    # =====================================================

    def _text(
        self,
        text: str,
        color: str = MUTED,
        size: int = 13,
        bold: bool = False,
    ):

        label = QLabel(text)

        weight = 700 if bold else 400

        label.setStyleSheet(
            f"""
            color:{color};
            font-size:{size}px;
            font-weight:{weight};
            """
        )

        return label


    def _row(
        self,
        left: str,
        right: str,
        right_color: str = TEXT,
    ):

        widget = QWidget()

        layout = QHBoxLayout(widget)

        layout.setContentsMargins(0, 3, 0, 3)

        layout.addWidget(
            self._text(left, TEXT, 13, True)
        )

        layout.addStretch()

        layout.addWidget(
            self._text(
                right,
                right_color,
                13,
                True,
            )
        )

        return widget


    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def _top_opportunities(self):

        card = DashboardCard(
            "Top Opportunities"
        )

        header = self._row(
            "SYMBOL      SIGNAL",
            "SCORE     PRICE"
        )

        card.layout.addWidget(header)

        for symbol, signal, score, price in [
            ("RELIANCE", "BUY", "92", "2,984.40"),
            ("HDFCBANK", "BUY", "88", "1,742.10"),
            ("TCS", "BUY", "86", "4,186.25"),
            ("INFY", "SELL", "82", "1,928.70"),
            ("ICICIBANK", "BUY", "79", "1,326.50"),
        ]:

            color = (
                GREEN
                if signal == "BUY"
                else RED
            )

            card.layout.addWidget(
                self._row(
                    f"{symbol}   {signal}",
                    f"{score}     ₹{price}",
                    color,
                )
            )

        return card


    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    def _sector_strength(self):

        card = DashboardCard(
            "Sector Strength"
        )

        for name, value in [
            ("IT", "+1.8%"),
            ("BANK", "+1.2%"),
            ("AUTO", "+0.9%"),
            ("PHARMA", "+0.4%"),
            ("METAL", "-0.6%"),
        ]:

            color = (
                GREEN
                if value.startswith("+")
                else RED
            )

            card.layout.addWidget(
                self._row(
                    name,
                    value,
                    color,
                )
            )

        card.layout.addStretch()

        return card


    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def _market_breadth(self):

        card = DashboardCard(
            "Market Breadth"
        )

        value = QLabel("64%")

        value.setAlignment(Qt.AlignCenter)

        value.setStyleSheet(
            f"""
            color:{GREEN};
            font-size:30px;
            font-weight:800;
            """
        )

        card.layout.addWidget(value)

        card.layout.addWidget(
            self._row(
                "Advances",
                "1,247",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "Declines",
                "684",
                RED,
            )
        )

        card.layout.addWidget(
            self._row(
                "Unchanged",
                "91",
            )
        )

        return card


    # =====================================================
    # HEATMAP
    # =====================================================

    def _market_heatmap(self):

        card = DashboardCard(
            "Market Heatmap"
        )

        grid = QGridLayout()

        items = [
            ("RELIANCE", GREEN),
            ("TCS", GREEN),
            ("HDFC", GREEN),
            ("INFY", RED),
            ("ICICI", GREEN),
            ("SBIN", GREEN),
            ("ITC", RED),
            ("LT", GREEN),
            ("AXIS", GREEN),
        ]

        for i, (symbol, color) in enumerate(items):

            tile = QLabel(symbol)

            tile.setAlignment(
                Qt.AlignCenter
            )

            tile.setMinimumHeight(32)

            tile.setStyleSheet(
                f"""
                background:{color};
                color:#ffffff;
                border-radius:4px;
                font-size:8px;
                font-weight:700;
                """
            )

            grid.addWidget(
                tile,
                i // 3,
                i % 3,
            )

        card.layout.addLayout(grid)

        return card


    # =====================================================
    # SCANNER SUMMARY
    # =====================================================

    def _scanner_summary(self):

        card = DashboardCard(
            "Scanner Summary"
        )

        number = QLabel("127")

        number.setAlignment(
            Qt.AlignCenter
        )

        number.setStyleSheet(
            f"""
            color:{TEXT};
            font-size:30px;
            font-weight:800;
            """
        )

        card.layout.addWidget(number)

        card.layout.addWidget(
            self._row(
                "BUY",
                "74",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "SELL",
                "53",
                RED,
            )
        )

        card.layout.addWidget(
            self._row(
                "Avg Score",
                "81",
                BLUE,
            )
        )

        return card


    # =====================================================
    # TOP MOVERS
    # =====================================================

    def _top_movers(self):

        card = DashboardCard(
            "Top Movers"
        )

        for symbol, value in [
            ("TRENT", "+5.42%"),
            ("BEL", "+4.18%"),
            ("HAL", "+3.91%"),
            ("BAJFINANCE", "-2.64%"),
            ("TATASTEEL", "-2.12%"),
        ]:

            color = (
                GREEN
                if value.startswith("+")
                else RED
            )

            card.layout.addWidget(
                self._row(
                    symbol,
                    value,
                    color,
                )
            )

        return card


    # =====================================================
    # LIVE ALERTS
    # =====================================================

    def _live_alerts(self):

        card = DashboardCard(
            "Live Scanner Alerts"
        )

        alerts = [
            ("RELIANCE", "Breakout above VWAP", GREEN),
            ("HDFCBANK", "Volume expansion", GREEN),
            ("INFY", "Momentum weakening", RED),
            ("TCS", "High confidence setup", BLUE),
        ]

        for symbol, message, color in alerts:

            card.layout.addWidget(
                self._row(
                    symbol,
                    message,
                    color,
                )
            )

        card.layout.addStretch()

        return card


    # =====================================================
    # WATCHLIST
    # =====================================================

    def _watchlist(self):

        card = DashboardCard(
            "Smart Watchlist"
        )

        for symbol, price in [
            ("RELIANCE", "2,984.40"),
            ("HDFCBANK", "1,742.10"),
            ("TCS", "4,186.25"),
            ("SBIN", "842.30"),
            ("LT", "3,628.75"),
        ]:

            card.layout.addWidget(
                self._row(
                    symbol,
                    f"₹{price}",
                )
            )

        return card


    # =====================================================
    # MARKET PULSE
    # =====================================================

    def _market_pulse(self):

        card = DashboardCard(
            "Market Pulse"
        )

        status = QLabel(
            "BULLISH"
        )

        status.setStyleSheet(
            f"""
            color:{GREEN};
            font-size:24px;
            font-weight:800;
            """
        )

        card.layout.addWidget(status)

        stats = QHBoxLayout()

        stats.addWidget(
            StatLabel(
                "Momentum",
                "Strong",
                GREEN,
            )
        )

        stats.addWidget(
            StatLabel(
                "Trend",
                "Positive",
                GREEN,
            )
        )

        stats.addWidget(
            StatLabel(
                "Volatility",
                "Low",
                BLUE,
            )
        )

        card.layout.addLayout(stats)

        card.layout.addStretch()

        return card


    # =====================================================
    # NEWS
    # =====================================================

    def _recent_news(self):

        card = DashboardCard(
            "Recent News"
        )

        for text in [
            "Markets trade higher on broad buying",
            "Banking stocks lead index gains",
            "IT shares see renewed momentum",
            "FII activity remains in focus",
        ]:

            label = self._text(
                text,
                TEXT,
                9,
            )

            label.setWordWrap(True)

            card.layout.addWidget(label)

        card.layout.addStretch()

        return card


    # =====================================================
    # INSTITUTIONAL FLOW
    # =====================================================

    def _institutional_flow(self):

        card = DashboardCard(
            "Institutional Flow"
        )

        card.layout.addWidget(
            self._row(
                "FII",
                "+₹2,184 Cr",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "DII",
                "+₹1,126 Cr",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "Net Flow",
                "+₹3,310 Cr",
                GREEN,
            )
        )

        card.layout.addStretch()

        return card


    # =====================================================
    # DERIVATIVES
    # =====================================================

    def _derivatives_pulse(self):

        card = DashboardCard(
            "Derivatives Pulse"
        )

        card.layout.addWidget(
            self._row(
                "PCR",
                "1.14",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "Max Pain",
                "25,500",
            )
        )

        card.layout.addWidget(
            self._row(
                "Call OI",
                "25,700",
                RED,
            )
        )

        card.layout.addWidget(
            self._row(
                "Put OI",
                "25,300",
                GREEN,
            )
        )

        card.layout.addStretch()

        return card


    # =====================================================
    # CONTROLLER COMPATIBILITY
    # =====================================================

    def show_notification(
        self,
        message: str,
    ):
        print(
            "[DASHBOARD]",
            message,
        )


__all__ = [
    "DashboardPage",
    "IndexCard",
]
