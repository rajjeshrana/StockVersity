# ==========================================================
# StockVersity Professional Trading Terminal
#
# File : market_header.py
# Part : 1 / 6
#
# DO NOT DELETE THIS MARKER
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)

# ==========================================================
# COLORS
# ==========================================================

HEADER_BG = "#111827"

CARD_BG = "#1E293B"

GREEN = "#22C55E"

RED = "#EF4444"

WHITE = "#F8FAFC"

GRAY = "#94A3B8"

BLUE = "#3B82F6"

# ==========================================================
# MARKET TILE
# ==========================================================


@dataclass
class MarketSnapshot:

    symbol: str

    price: float = 0.0

    change: float = 0.0

    percent: float = 0.0


class MarketTile(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        symbol: str,
    ):

        super().__init__()

        self.snapshot = MarketSnapshot(
            symbol=symbol,
        )

        self.setObjectName(
            "MarketTile",
        )

        self.setMinimumWidth(170)

        self.setMaximumHeight(90)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.setStyleSheet(
            f"""
            QFrame#MarketTile{{
                background:{CARD_BG};
                border:1px solid #2D3748;
                border-radius:10px;
            }}
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            12,
            8,
            12,
            8,
        )

        self.symbolLabel = QLabel(symbol)

        self.symbolLabel.setStyleSheet(
            f"""
            color:{WHITE};
            font-size:13px;
            font-weight:700;
            """
        )

        self.priceLabel = QLabel("0.00")

        self.priceLabel.setStyleSheet(
            f"""
            color:{WHITE};
            font-size:22px;
            font-weight:800;
            """
        )

        self.changeLabel = QLabel("0.00 (0.00%)")

        self.changeLabel.setStyleSheet(
            f"""
            color:{GRAY};
            font-size:11px;
            """
        )

        layout.addWidget(
            self.symbolLabel
        )

        layout.addWidget(
            self.priceLabel
        )

        layout.addWidget(
            self.changeLabel
        )

    # ------------------------------------------------------

    def update_data(
        self,
        price: float,
        change: float,
        percent: float,
    ):

        self.snapshot.price = price

        self.snapshot.change = change

        self.snapshot.percent = percent

        self.priceLabel.setText(
            f"{price:,.2f}"
        )

        arrow = "▲"

        colour = GREEN

        if change < 0:

            arrow = "▼"

            colour = RED

        self.changeLabel.setStyleSheet(
            f"""
            color:{colour};
            font-size:11px;
            font-weight:600;
            """
        )

        self.changeLabel.setText(
            f"{arrow} {change:+.2f} ({percent:+.2f}%)"
        )

# ==========================================================
# END PART 1
# ==========================================================

# ==========================================================
# MARKET HEADER
# Part 2 / 6
# ==========================================================


class MarketHeader(QWidget):

    symbolClicked = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.tiles: Dict[str, MarketTile] = {}

        self._build_ui()

        self._create_timer()

    # ------------------------------------------------------

    def _build_ui(self):

        self.setObjectName("MarketHeader")

        self.setMinimumHeight(110)

        self.setStyleSheet(
            f"""
            QWidget#MarketHeader{{
                background:{HEADER_BG};
                border-bottom:1px solid #2D3748;
            }}
            """
        )

        self.mainLayout = QHBoxLayout(self)

        self.mainLayout.setContentsMargins(
            12,
            8,
            12,
            8,
        )

        self.mainLayout.setSpacing(10)

        symbols = [

            "NIFTY 50",

            "BANK NIFTY",

            "GIFT NIFTY",

            "INDIA VIX",

            "GOLD",

            "BTC",

        ]

        for symbol in symbols:

            tile = MarketTile(symbol)

            self.tiles[symbol] = tile

            self.mainLayout.addWidget(tile)

    # ------------------------------------------------------

    def _create_timer(self):

        self.timer = QTimer(self)

        self.timer.setInterval(1000)

        self.timer.timeout.connect(
            self._heartbeat
        )

        self.timer.start()

    # ------------------------------------------------------

    def _heartbeat(self):

        """
        Reserved for future
        live refresh.
        """

        pass

    # ------------------------------------------------------

    def update_symbol(

        self,

        symbol: str,

        price: float,

        change: float,

        percent: float,

    ):

        tile = self.tiles.get(symbol)

        if tile is None:

            return

        tile.update_data(

            price,

            change,

            percent,

        )

# ==========================================================
# END PART 2
# ==========================================================

# ==========================================================
# LIVE DATA API
# Part 3 / 6
# ==========================================================

    def update_snapshot(
        self,
        snapshot: dict,
    ):
        """
        Runtime Snapshot

        {
            "NIFTY 50":{
                "price":...,
                "change":...,
                "percent":...
            }
        }
        """

        if not snapshot:
            return

        for symbol, values in snapshot.items():

            if symbol not in self.tiles:
                continue

            self.update_symbol(

                symbol,

                float(
                    values.get(
                        "price",
                        0,
                    )
                ),

                float(
                    values.get(
                        "change",
                        0,
                    )
                ),

                float(
                    values.get(
                        "percent",
                        0,
                    )
                ),

            )

    # ------------------------------------------------------

    def set_market_open(
        self,
        opened: bool,
    ):

        self.market_open = opened

    # ------------------------------------------------------

    def set_connection(
        self,
        connected: bool,
    ):

        self.connected = connected

    # ------------------------------------------------------

    def reset(self):

        for tile in self.tiles.values():

            tile.update_data(
                0,
                0,
                0,
            )

# ==========================================================
# SAMPLE DATA
# Remove after Upstox integration
# ==========================================================

    def demo_data(self):

        self.update_symbol(

            "NIFTY 50",

            24836.20,

            124.65,

            0.51,

        )

        self.update_symbol(

            "BANK NIFTY",

            58112.80,

            381.40,

            0.66,

        )

        self.update_symbol(

            "GIFT NIFTY",

            24901.40,

            76.50,

            0.31,

        )

        self.update_symbol(

            "INDIA VIX",

            11.82,

            -0.42,

            -3.43,

        )

        self.update_symbol(

            "GOLD",

            101245,

            860,

            0.86,

        )

        self.update_symbol(

            "BTC",

            118420,

            1580,

            1.35,

        )

# ==========================================================
# END PART 3
# ==========================================================

# ==========================================================
# PART 4 / 6
# Professional Tile Behaviour
# ==========================================================

from PySide6.QtGui import (
    QColor,
    QPalette,
)


class MarketTile(MarketTile):

    # ------------------------------------------------------

    def mousePressEvent(
        self,
        event,
    ):

        self.clicked.emit(
            self.snapshot.symbol
        )

        super().mousePressEvent(
            event
        )

    # ------------------------------------------------------

    def mouseDoubleClickEvent(
        self,
        event,
    ):

        self.clicked.emit(
            self.snapshot.symbol
        )

        super().mouseDoubleClickEvent(
            event
        )

    # ------------------------------------------------------

    def flash_green(self):

        self.setStyleSheet(
            f"""
            QFrame#MarketTile{{
                background:#14532D;
                border:2px solid {GREEN};
                border-radius:10px;
            }}
            """
        )

        QTimer.singleShot(
            250,
            self.restore_style,
        )

    # ------------------------------------------------------

    def flash_red(self):

        self.setStyleSheet(
            f"""
            QFrame#MarketTile{{
                background:#450A0A;
                border:2px solid {RED};
                border-radius:10px;
            }}
            """
        )

        QTimer.singleShot(
            250,
            self.restore_style,
        )

    # ------------------------------------------------------

    def restore_style(self):

        self.setStyleSheet(
            f"""
            QFrame#MarketTile{{
                background:{CARD_BG};
                border:1px solid #2D3748;
                border-radius:10px;
            }}
            """
        )

    # ------------------------------------------------------

    def update_data(
        self,
        price,
        change,
        percent,
    ):

        previous = self.snapshot.price

        super().update_data(

            price,

            change,

            percent,

        )

        if previous == 0:
            return

        if price > previous:

            self.flash_green()

        elif price < previous:

            self.flash_red()


# ==========================================================
# HEADER EVENTS
# ==========================================================


class MarketHeader(MarketHeader):

    def connect_chart(
        self,
        callback,
    ):

        for tile in self.tiles.values():

            tile.clicked.connect(
                callback
            )

    # ------------------------------------------------------

    def highlight_gift_nifty(self):

        tile = self.tiles.get(
            "GIFT NIFTY"
        )

        if tile is None:
            return

        tile.setStyleSheet(
            """
            QFrame#MarketTile{

                background:#172554;

                border:2px solid #3B82F6;

                border-radius:10px;

            }
            """
        )


# ==========================================================
# END PART 4
# ==========================================================

