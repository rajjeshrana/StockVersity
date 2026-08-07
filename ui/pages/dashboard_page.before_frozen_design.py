


"""
StockVersity Scanner Pro
Final Approved Dashboard UI
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPainterPath
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
CYAN = "#36c5f0"


# =========================================================
# BASE DASHBOARD CARD
# =========================================================

class DashboardCard(QFrame):

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.setObjectName("dashboardCard")

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.setStyleSheet(
            f"""
            QFrame#dashboardCard {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 11px;
            }}
            """
        )

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            18, 16, 18, 16
        )

        self.layout.setSpacing(11)

        if title:
            title_label = QLabel(title)

            title_label.setStyleSheet(
                f"""
                color: {TEXT};
                font-size: 18px;
                font-weight: 700;
                background: transparent;
                border: none;
                """
            )

            self.layout.addWidget(title_label)


# =========================================================
# INDEX CARD
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

        layout.setContentsMargins(
            12, 4, 12, 4
        )

        layout.setSpacing(2)

        self.name_label = QLabel(name)

        self.name_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 13px;
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
            font-size: 13px;
            font-weight: 700;
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

        try:
            value = float(value or 0.0)
        except (TypeError, ValueError):
            value = 0.0

        try:
            change = float(change or 0.0)
        except (TypeError, ValueError):
            change = 0.0

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
            font-size: 13px;
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

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.setSpacing(3)

        title_label = QLabel(title)

        title_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 12px;
            font-weight: 600;
            """
        )

        value_label = QLabel(value)

        value_label.setStyleSheet(
            f"""
            color: {value_color};
            font-size: 17px;
            font-weight: 700;
            """
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)


# =========================================================
# MARKET PULSE GRAPHIC
# =========================================================

class MarketPulseGraphic(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(155)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        w = self.width()
        h = self.height()

        # -------------------------------------------------
        # BULL HEAD
        # -------------------------------------------------

        cx = w * 0.22
        cy = h * 0.47

        painter.setPen(
            QPen(QColor(GREEN), 4)
        )

        painter.setBrush(
            Qt.NoBrush
        )

        # face
        face = QPainterPath()

        face.moveTo(
            cx - 25,
            cy - 30,
        )

        face.lineTo(
            cx - 15,
            cy + 24,
        )

        face.lineTo(
            cx,
            cy + 39,
        )

        face.lineTo(
            cx + 15,
            cy + 24,
        )

        face.lineTo(
            cx + 25,
            cy - 30,
        )

        painter.drawPath(face)

        # horns
        left_horn = QPainterPath()

        left_horn.moveTo(
            cx - 20,
            cy - 25,
        )

        left_horn.cubicTo(
            cx - 55,
            cy - 48,
            cx - 60,
            cy - 10,
            cx - 40,
            cy - 5,
        )

        painter.drawPath(left_horn)

        right_horn = QPainterPath()

        right_horn.moveTo(
            cx + 20,
            cy - 25,
        )

        right_horn.cubicTo(
            cx + 55,
            cy - 48,
            cx + 60,
            cy - 10,
            cx + 40,
            cy - 5,
        )

        painter.drawPath(right_horn)

        # eyes
        painter.setBrush(
            QColor(GREEN)
        )

        painter.drawEllipse(
            QPointF(
                cx - 10,
                cy,
            ),
            3,
            3,
        )

        painter.drawEllipse(
            QPointF(
                cx + 10,
                cy,
            ),
            3,
            3,
        )

        # -------------------------------------------------
        # TREND GRAPH
        # -------------------------------------------------

        x0 = w * 0.43
        x1 = w * 0.95

        y0 = h * 0.72
        y1 = h * 0.20

        painter.setPen(
            QPen(
                QColor("#173151"),
                1,
            )
        )

        for i in range(4):

            y = (
                y1
                + ((y0 - y1) / 3) * i
            )

            painter.drawLine(
                QPointF(x0, y),
                QPointF(x1, y),
            )

        points = [
            (0.00, 0.78),
            (0.12, 0.67),
            (0.23, 0.71),
            (0.34, 0.52),
            (0.46, 0.57),
            (0.58, 0.39),
            (0.69, 0.43),
            (0.80, 0.24),
            (0.90, 0.30),
            (1.00, 0.10),
        ]

        path = QPainterPath()

        for i, (px, py) in enumerate(points):

            x = x0 + px * (x1 - x0)

            y = y1 + py * (y0 - y1)

            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        painter.setPen(
            QPen(
                QColor(GREEN),
                3,
            )
        )

        painter.drawPath(path)

        painter.end()


# =========================================================
# BREADTH GAUGE
# =========================================================

class BreadthGauge(QWidget):

    def __init__(
        self,
        value: int = 64,
    ):
        super().__init__()

        self.value = value

        self.setMinimumHeight(115)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        size = min(
            self.width(),
            self.height() * 1.7,
        )

        rect = QRectF(
            (self.width() - size) / 2,
            12,
            size,
            size,
        )

        pen = QPen(
            QColor("#18273b"),
            12,
        )

        pen.setCapStyle(
            Qt.RoundCap
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            0,
            180 * 16,
        )

        value_pen = QPen(
            QColor(GREEN),
            12,
        )

        value_pen.setCapStyle(
            Qt.RoundCap
        )

        painter.setPen(
            value_pen
        )

        span = int(
            180
            * (self.value / 100)
            * 16
        )

        painter.drawArc(
            rect,
            180 * 16,
            -span,
        )

        painter.setPen(
            QColor(TEXT)
        )

        font = QFont(
            "Segoe UI",
            19,
            QFont.Bold,
        )

        painter.setFont(font)

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            f"{self.value}%",
        )

        painter.end()


# =========================================================
# SCANNER DONUT
# =========================================================

class ScannerDonut(QWidget):

    def __init__(
        self,
        buy: int = 74,
        sell: int = 53,
    ):
        super().__init__()

        self.buy = buy
        self.sell = sell

        self.setMinimumHeight(125)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        size = min(
            self.width(),
            self.height(),
        ) - 22

        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        total = max(
            1,
            self.buy + self.sell,
        )

        buy_angle = int(
            360
            * self.buy
            / total
            * 16
        )

        pen = QPen(
            QColor(GREEN),
            13,
        )

        pen.setCapStyle(
            Qt.RoundCap
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            90 * 16,
            -buy_angle,
        )

        pen.setColor(
            QColor(RED)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            90 * 16 - buy_angle,
            -(360 * 16 - buy_angle),
        )

        painter.setPen(
            QColor(TEXT)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                19,
                QFont.Bold,
            )
        )

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            str(total),
        )

        painter.end()


# =========================================================
# DERIVATIVES GAUGE
# =========================================================

class DerivativesGauge(QWidget):

    def __init__(
        self,
        pcr: float = 1.18,
    ):
        super().__init__()

        self.pcr = pcr

        self.setMinimumHeight(115)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        w = self.width()
        h = self.height()

        x1 = 20
        x2 = w - 20

        y = h * 0.58

        painter.setPen(
            QPen(
                QColor("#1b2a40"),
                12,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(x1, y),
            QPointF(x2, y),
        )

        ratio = max(
            0.0,
            min(
                1.0,
                self.pcr / 2.0,
            ),
        )

        xpos = (
            x1
            + ratio * (x2 - x1)
        )

        painter.setPen(
            QPen(
                QColor(PURPLE),
                12,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(x1, y),
            QPointF(xpos, y),
        )

        painter.setBrush(
            QColor(TEXT)
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawEllipse(
            QPointF(xpos, y),
            7,
            7,
        )

        painter.setPen(
            QColor(TEXT)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Bold,
            )
        )

        painter.drawText(
            self.rect(),
            Qt.AlignTop | Qt.AlignHCenter,
            f"PCR {self.pcr:.2f}",
        )

        painter.end()


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

        self.setObjectName(
            "newDashboard"
        )

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

        # -------------------------------------------------
        # MarketController compatibility
        # -------------------------------------------------
        self.index_cards: Dict[
            str,
            IndexCard,
        ] = {
            "NIFTY": IndexCard(
                "NIFTY 50"
          ),
            "BANKNIFTY": IndexCard(
                "BANK NIFTY"
          ),
            "FINNIFTY": IndexCard(
                "FIN NIFTY"
          ),
            "INDIAVIX": IndexCard(
                "INDIA VIX"
          ),
        }

        self._build_ui()


    # =====================================================
    # BUILD
    # =====================================================

    def _build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(
            0, 0, 0, 0
        )

        root.setSpacing(0)

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setStyleSheet(
            f"""
            QScrollArea {{
                background: {BG};
                border: none;
            }}

            QScrollBar:vertical {{
                background: {BG};
                width: 9px;
            }}

            QScrollBar::handle:vertical {{
                background: #263750;
                border-radius: 4px;
                min-height: 40px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            """
        )

        content = QWidget()

        content.setObjectName(
            "dashboardContent"
        )

        content.setMinimumWidth(0)

        content.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        content.setStyleSheet(
            f"""
            QWidget#dashboardContent {{
                background: {BG};
            }}
            """
        )

        self.grid = QGridLayout(
            content
        )

        self.grid.setContentsMargins(
            18, 16, 18, 20
        )

        self.grid.setHorizontalSpacing(
            12
        )

        self.grid.setVerticalSpacing(
            12
        )

        # =================================================
        # ROW 1
        # =================================================

        self.grid.addWidget(
            self._market_pulse(),
            0, 0, 1, 2,
        )

        self.grid.addWidget(
            self._sector_strength(),
            0, 2,
        )

        self.grid.addWidget(
            self._market_breadth(),
            0, 3,
        )

        self.grid.addWidget(
            self._market_heatmap(),
            0, 4,
        )

        # =================================================
        # ROW 2
        # =================================================

        self.grid.addWidget(
            self._top_opportunities(),
            1, 0, 1, 2,
        )

        self.grid.addWidget(
            self._scanner_summary(),
            1, 2,
        )

        self.grid.addWidget(
            self._top_movers(),
            1, 3,
        )

        self.grid.addWidget(
            self._live_alerts(),
            1, 4,
        )

        # =================================================
        # ROW 3
        # =================================================

        self.grid.addWidget(
            self._institutional_flow(),
            2, 0, 1, 2,
        )

        self.grid.addWidget(
            self._derivatives_pulse(),
            2, 2,
        )

        self.grid.addWidget(
            self._nifty_oi_chart(),
            2, 3, 1, 2,
        )

        # =================================================
        # RESPONSIVE GRID
        # =================================================

        for column in range(5):

            self.grid.setColumnStretch(
                column,
                1,
            )

            self.grid.setColumnMinimumWidth(
                column,
                0,
            )

        self.grid.setRowStretch(
            0,
            5,
        )

        self.grid.setRowStretch(
            1,
            5,
        )

        self.grid.setRowStretch(
            2,
            4,
        )

        self.scroll.setWidget(
            content
        )

        root.addWidget(
            self.scroll
        )


    # =====================================================
    # TEXT
    # =====================================================

    def _text(
        self,
        text: str,
        color: str = MUTED,
        size: int = 13,
        bold: bool = False,
    ):

        label = QLabel(text)

        weight = (
            700
            if bold
            else 500
        )

        label.setStyleSheet(
            f"""
            color: {color};
            font-size: {size}px;
            font-weight: {weight};
            background: transparent;
            border: none;
            """
        )

        return label


    # =====================================================
    # BASIC ROW
    # =====================================================

    def _row(
        self,
        left: str,
        right: str,
        right_color: str = TEXT,
    ):

        widget = QWidget()

        layout = QHBoxLayout(
            widget
        )

        layout.setContentsMargins(
            0, 5, 0, 5
        )

        layout.setSpacing(8)

        left_label = self._text(
            left,
            TEXT,
            13,
            True,
        )

        right_label = self._text(
            right,
            right_color,
            13,
            True,
        )

        layout.addWidget(
            left_label
        )

        layout.addStretch()

        layout.addWidget(
            right_label
        )

        return widget


    # =====================================================
    # MARKET PULSE
    # =====================================================

    def _market_pulse(self):

        card = DashboardCard(
            "Market Pulse"
        )

        top = QHBoxLayout()

        status = QLabel(
            "BULLISH"
        )

        status.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 25px;
            font-weight: 800;
            """
        )

        score = QLabel(
            "78 / 100"
        )

        score.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 16px;
            font-weight: 700;
            """
        )

        top.addWidget(status)

        top.addStretch()

        top.addWidget(score)

        card.layout.addLayout(top)

        graphic = MarketPulseGraphic()

        card.layout.addWidget(
            graphic,
            1,
        )

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

        stats.addWidget(
            StatLabel(
                "Breadth",
                "Healthy",
                GREEN,
            )
        )

        card.layout.addLayout(
            stats
        )

        return card


    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    def _sector_strength(self):

        card = DashboardCard(
            "Sector Strength"
        )

        data = [
            ("IT", "+1.8%"),
            ("BANK", "+1.2%"),
            ("AUTO", "+0.9%"),
            ("PHARMA", "+0.4%"),
            ("METAL", "-0.6%"),
        ]

        for name, value in data:

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

        gauge = BreadthGauge(
            64
        )

        card.layout.addWidget(
            gauge
        )

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
                MUTED,
            )
        )

        return card


    # =====================================================
    # MARKET HEATMAP
    # =====================================================

    def _market_heatmap(self):

        card = DashboardCard(
            "Market Heatmap"
        )

        grid = QGridLayout()

        grid.setSpacing(6)

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

        for i, (
            symbol,
            color,
        ) in enumerate(items):

            tile = QLabel(
                symbol
            )

            tile.setAlignment(
                Qt.AlignCenter
            )

            tile.setMinimumHeight(
                39
            )

            tile.setStyleSheet(
                f"""
                background: {color};
                color: #ffffff;
                border-radius: 5px;
                font-size: 11px;
                font-weight: 700;
                """
            )

            grid.addWidget(
                tile,
                i // 3,
                i % 3,
            )

        card.layout.addLayout(
            grid
        )

        return card


    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def _top_opportunities(self):

        card = DashboardCard(
            "Top Opportunities"
        )

        header = QWidget()

        header_layout = QGridLayout(
            header
        )

        header_layout.setContentsMargins(
            0, 3, 0, 6
        )

        columns = [
            "SYMBOL",
            "SIGNAL",
            "SCORE",
            "PRICE",
        ]

        for i, name in enumerate(columns):

            label = self._text(
                name,
                MUTED,
                11,
                True,
            )

            header_layout.addWidget(
                label,
                0,
                i,
            )

        header_layout.setColumnStretch(
            0,
            2,
        )

        header_layout.setColumnStretch(
            1,
            1,
        )

        header_layout.setColumnStretch(
            2,
            1,
        )

        header_layout.setColumnStretch(
            3,
            2,
        )

        card.layout.addWidget(
            header
        )

        opportunities = [
            (
                "RELIANCE",
                "BUY",
                "92",
                "₹2,984.40",
            ),
            (
                "HDFCBANK",
                "BUY",
                "88",
                "₹1,742.10",
            ),
            (
                "TCS",
                "BUY",
                "86",
                "₹4,186.25",
            ),
            (
                "INFY",
                "SELL",
                "82",
                "₹1,928.70",
            ),
            (
                "ICICIBANK",
                "BUY",
                "79",
                "₹1,326.50",
            ),
        ]

        for (
            symbol,
            signal,
            score,
            price,
        ) in opportunities:

            row = QFrame()

            row.setStyleSheet(
                f"""
                QFrame {{
                    background: {PANEL_ALT};
                    border: none;
                    border-radius: 6px;
                }}
                """
            )

            layout = QGridLayout(
                row
            )

            layout.setContentsMargins(
                10, 8, 10, 8
            )

            signal_color = (
                GREEN
                if signal == "BUY"
                else RED
            )

            symbol_label = self._text(
                symbol,
                TEXT,
                13,
                True,
            )

            signal_label = self._text(
                signal,
                signal_color,
                12,
                True,
            )

            score_label = self._text(
                score,
                BLUE,
                13,
                True,
            )

            price_label = self._text(
                price,
                TEXT,
                13,
                True,
            )

            layout.addWidget(
                symbol_label,
                0, 0,
            )

            layout.addWidget(
                signal_label,
                0, 1,
            )

            layout.addWidget(
                score_label,
                0, 2,
            )

            layout.addWidget(
                price_label,
                0, 3,
            )

            layout.setColumnStretch(
                0, 2
            )

            layout.setColumnStretch(
                1, 1
            )

            layout.setColumnStretch(
                2, 1
            )

            layout.setColumnStretch(
                3, 2
            )

            card.layout.addWidget(
                row
            )

        return card


    # =====================================================
    # SCANNER SUMMARY
    # =====================================================

    def _scanner_summary(self):

        card = DashboardCard(
            "Scanner Summary"
        )

        donut = ScannerDonut(
            74,
            53,
        )

        card.layout.addWidget(
            donut
        )

        stats = QHBoxLayout()

        stats.addWidget(
            StatLabel(
                "BUY",
                "74",
                GREEN,
            )
        )

        stats.addWidget(
            StatLabel(
                "SELL",
                "53",
                RED,
            )
        )

        stats.addWidget(
            StatLabel(
                "AVG SCORE",
                "81",
                BLUE,
            )
        )

        card.layout.addLayout(
            stats
        )

        button = QPushButton(
            "Open Scanner"
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setStyleSheet(
            f"""
            QPushButton {{
                background: {BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 700;
            }}

            QPushButton:hover {{
                background: #4c88ff;
            }}
            """
        )

        button.clicked.connect(
            lambda:
            self.scanner_requested.emit(
                "intraday"
            )
        )

        card.layout.addWidget(
            button
        )

        return card


    # =====================================================
    # TOP MOVERS
    # =====================================================

    def _top_movers(self):

        card = DashboardCard(
            "Top Movers"
        )

        movers = [
            ("TRENT", "+5.42%"),
            ("BEL", "+4.18%"),
            ("HAL", "+3.91%"),
            ("BAJFINANCE", "-2.64%"),
            ("TATASTEEL", "-2.12%"),
        ]

        for symbol, value in movers:

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

        card.layout.addStretch()

        return card


    # =====================================================
    # LIVE SCANNER ALERTS
    # =====================================================

    def _live_alerts(self):

        card = DashboardCard(
            "Live Scanner Alerts"
        )

        header = QHBoxLayout()

        header.addWidget(
            self._text(
                "SYMBOL",
                MUTED,
                11,
                True,
            )
        )

        header.addStretch()

        header.addWidget(
            self._text(
                "TRIGGER",
                MUTED,
                11,
                True,
            )
        )

        card.layout.addLayout(
            header
        )

        alerts = [
            (
                "RELIANCE",
                "VWAP Breakout",
                GREEN,
            ),
            (
                "HDFCBANK",
                "Volume Expansion",
                GREEN,
            ),
            (
                "INFY",
                "Weak Momentum",
                RED,
            ),
            (
                "TCS",
                "High Confidence",
                BLUE,
            ),
            (
                "SBIN",
                "Trend Continuation",
                GREEN,
            ),
        ]

        for (
            symbol,
            message,
            color,
        ) in alerts:

            row = QFrame()

            row.setStyleSheet(
                f"""
                QFrame {{
                    background: {PANEL_ALT};
                    border: none;
                    border-radius: 6px;
                }}
                """
            )

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                9, 8, 9, 8
            )

            layout.addWidget(
                self._text(
                    symbol,
                    TEXT,
                    12,
                    True,
                )
            )

            layout.addStretch()

            layout.addWidget(
                self._text(
                    message,
                    color,
                    11,
                    True,
                )
            )

            card.layout.addWidget(
                row
            )

        return card


    # =====================================================
    # INSTITUTIONAL FLOW
    # =====================================================

    def _institutional_flow(self):

        card = DashboardCard(
            "Institutional Flow"
        )

        subtitle = self._text(
            "Cash Market • ₹ Crore",
            MUTED,
            12,
            False,
        )

        card.layout.addWidget(
            subtitle
        )

        flows = [
            (
                "FII",
                "-1,248 Cr",
                RED,
                64,
            ),
            (
                "DII",
                "+1,622 Cr",
                GREEN,
                83,
            ),
            (
                "Net Flow",
                "+374 Cr",
                GREEN,
                55,
            ),
        ]

        for (
            name,
            value,
            color,
            strength,
        ) in flows:

            top = QHBoxLayout()

            top.addWidget(
                self._text(
                    name,
                    TEXT,
                    13,
                    True,
                )
            )

            top.addStretch()

            top.addWidget(
                self._text(
                    value,
                    color,
                    13,
                    True,
                )
            )

            card.layout.addLayout(
                top
            )

            track = QFrame()

            track.setFixedHeight(
                9
            )

            track.setStyleSheet(
                f"""
                background: {PANEL_ALT};
                border-radius: 4px;
                """
            )

            track_layout = QHBoxLayout(
                track
            )

            track_layout.setContentsMargins(
                0, 0, 0, 0
            )

            bar = QFrame()

            bar.setFixedWidth(
                max(
                    20,
                    strength * 2,
                )
            )

            bar.setStyleSheet(
                f"""
                background: {color};
                border-radius: 4px;
                """
            )

            track_layout.addWidget(
                bar
            )

            track_layout.addStretch()

            card.layout.addWidget(
                track
            )

        card.layout.addStretch()

        return card


    # =====================================================
    # DERIVATIVES PULSE
    # =====================================================

    def _derivatives_pulse(self):

        card = DashboardCard(
            "Derivatives Pulse"
        )

        gauge = DerivativesGauge(
            1.18
        )

        card.layout.addWidget(
            gauge
        )

        card.layout.addWidget(
            self._row(
                "Max Pain",
                "25,500",
                ORANGE,
            )
        )

        card.layout.addWidget(
            self._row(
                "Call OI",
                "12.8 Cr",
                RED,
            )
        )

        card.layout.addWidget(
            self._row(
                "Put OI",
                "15.1 Cr",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "Bias",
                "Mild Bullish",
                GREEN,
            )
        )

        return card


    # =====================================================
    # NIFTY OI CHART
    # =====================================================

    def _nifty_oi_chart(self):

        card = DashboardCard(
            "NIFTY OI Chart"
        )

        card.layout.addWidget(
            self._text(
                "Call OI vs Put OI by strike",
                MUTED,
                12,
            )
        )

        header = QHBoxLayout()

        header.addWidget(
            self._text(
                "STRIKE",
                MUTED,
                10,
                True,
            )
        )

        header.addStretch()

        header.addWidget(
            self._text(
                "CALL OI",
                RED,
                10,
                True,
            )
        )

        header.addSpacing(
            28
        )

        header.addWidget(
            self._text(
                "PUT OI",
                GREEN,
                10,
                True,
            )
        )

        card.layout.addLayout(
            header
        )

        strikes = [
            (
                "25,400",
                68,
                42,
            ),
            (
                "25,450",
                76,
                48,
            ),
            (
                "25,500",
                92,
                72,
            ),
            (
                "25,550",
                64,
                88,
            ),
            (
                "25,600",
                51,
                96,
            ),
        ]

        for (
            strike,
            call_oi,
            put_oi,
        ) in strikes:

            row = QWidget()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                0, 4, 0, 4
            )

            layout.setSpacing(
                8
            )

            strike_label = self._text(
                strike,
                TEXT,
                11,
                True,
            )

            strike_label.setFixedWidth(
                50
            )

            layout.addWidget(
                strike_label
            )

            call_track = QFrame()

            call_track.setMinimumHeight(
                12
            )

            call_track.setStyleSheet(
                f"""
                background: {PANEL_ALT};
                border-radius: 5px;
                """
            )

            call_layout = QHBoxLayout(
                call_track
            )

            call_layout.setContentsMargins(
                0, 0, 0, 0
            )

            call_bar = QFrame()

            call_bar.setFixedWidth(
                max(
                    8,
                    call_oi,
                )
            )

            call_bar.setStyleSheet(
                f"""
                background: {RED};
                border-radius: 5px;
                """
            )

            call_layout.addWidget(
                call_bar
            )

            call_layout.addStretch()

            layout.addWidget(
                call_track,
                1,
            )

            put_track = QFrame()

            put_track.setMinimumHeight(
                12
            )

            put_track.setStyleSheet(
                f"""
                background: {PANEL_ALT};
                border-radius: 5px;
                """
            )

            put_layout = QHBoxLayout(
                put_track
            )

            put_layout.setContentsMargins(
                0, 0, 0, 0
            )

            put_bar = QFrame()

            put_bar.setFixedWidth(
                max(
                    8,
                    put_oi,
                )
            )

            put_bar.setStyleSheet(
                f"""
                background: {GREEN};
                border-radius: 5px;
                """
            )

            put_layout.addWidget(
                put_bar
            )

            put_layout.addStretch()

            layout.addWidget(
                put_track,
                1,
            )

            card.layout.addWidget(
                row
            )

        legend = QHBoxLayout()

        legend.addWidget(
            self._text(
                "● CALL OI",
                RED,
                11,
                True,
            )
        )

        legend.addSpacing(
            16
        )

        legend.addWidget(
            self._text(
                "● PUT OI",
                GREEN,
                11,
                True,
            )
        )

        legend.addStretch()

        card.layout.addLayout(
            legend
        )

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


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "DashboardPage",
    "IndexCard",
]