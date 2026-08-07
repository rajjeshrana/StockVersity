"""
=========================================================
StockVersity Scanner Pro
Premium Dashboard UI
Default Production Dashboard
=========================================================
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from PySide6.QtCore import (
    Qt,
    Signal,
    QRectF,
    QPointF,
)

from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# =========================================================
# THEME
# =========================================================

BG = "#07101d"

PANEL = "#0c1727"
PANEL_ALT = "#101d30"

BORDER = "#1d2b40"
BORDER_HOVER = "#2d4262"

TEXT = "#e9eef7"
TEXT_SOFT = "#c7d1df"
MUTED = "#8190a6"

BLUE = "#3578ff"
GREEN = "#28d17c"
RED = "#ff5364"
ORANGE = "#ffad42"
PURPLE = "#8b6cff"
CYAN = "#29c7d8"

TRACK = "#17263a"


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

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.setMinimumHeight(255)

        self.setStyleSheet(
            f"""
            QFrame#dashboardCard {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}

            QFrame#dashboardCard:hover {{
                border: 1px solid {BORDER_HOVER};
            }}
            """
        )

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        self.layout.setSpacing(11)

        if title:

            self.title_label = QLabel(title)

            self.title_label.setStyleSheet(
                f"""
                color: {TEXT};
                font-family: "Segoe UI";
                font-size: 18px;
                font-weight: 700;
                border: none;
                background: transparent;
                """
            )

            self.layout.addWidget(
                self.title_label
            )


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

        layout.setContentsMargins(
            12,
            5,
            12,
            5,
        )

        layout.setSpacing(2)

        self.name_label = QLabel(name)

        self.name_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-family: "Segoe UI";
            font-size: 13px;
            font-weight: 700;
            """
        )

        self.value_label = QLabel("--")

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT};
            font-family: "Segoe UI";
            font-size: 18px;
            font-weight: 700;
            """
        )

        self.change_label = QLabel("--")

        self.change_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-family: "Segoe UI";
            font-size: 13px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            self.name_label
        )

        layout.addWidget(
            self.value_label
        )

        layout.addWidget(
            self.change_label
        )

    def update_data(
        self,
        value: float,
        change: float,
        history: Optional[List[float]] = None,
    ):

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        try:
            change = float(change)
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
            font-family: "Segoe UI";
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
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
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

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )


# =========================================================
# BREADTH GAUGE
# =========================================================

class BreadthGauge(QWidget):

    def __init__(
        self,
        value: float = 64,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.value = max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )

        self.setMinimumHeight(125)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()

        diameter = min(
            width - 30,
            180,
        )

        rect = QRectF(
            (width - diameter) / 2,
            22,
            diameter,
            diameter,
        )

        pen_width = 15

        painter.setPen(
            QPen(
                QColor(TRACK),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            rect,
            0,
            180 * 16,
        )

        if self.value >= 55:
            color = GREEN

        elif self.value <= 45:
            color = RED

        else:
            color = ORANGE

        span = int(
            180
            * self.value
            / 100
        )

        painter.setPen(
            QPen(
                QColor(color),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            rect,
            180 * 16,
            -span * 16,
        )

        painter.setPen(
            QColor(TEXT)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                24,
                QFont.Bold,
            )
        )

        painter.drawText(
            QRectF(
                0,
                55,
                width,
                40,
            ),
            Qt.AlignCenter,
            f"{self.value:.0f}%",
        )

        painter.setPen(
            QColor(color)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Bold,
            )
        )

        status = (
            "BULLISH"
            if self.value >= 55
            else
            "BEARISH"
            if self.value <= 45
            else
            "NEUTRAL"
        )

        painter.drawText(
            QRectF(
                0,
                92,
                width,
                24,
            ),
            Qt.AlignCenter,
            status,
        )


# =========================================================
# SCANNER DONUT
# =========================================================

class ScannerDonut(QWidget):

    def __init__(
        self,
        total: int = 127,
        buys: int = 74,
        sells: int = 53,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.total = total
        self.buys = buys
        self.sells = sells

        self.setMinimumHeight(145)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        diameter = min(
            120,
            self.width() - 25,
            self.height() - 15,
        )

        rect = QRectF(
            (
                self.width()
                - diameter
            ) / 2,
            6,
            diameter,
            diameter,
        )

        pen_width = 16

        painter.setPen(
            QPen(
                QColor(TRACK),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawEllipse(rect)

        signal_total = max(
            1,
            self.buys + self.sells,
        )

        buy_angle = (
            360
            * self.buys
            / signal_total
        )

        painter.setPen(
            QPen(
                QColor(GREEN),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            rect,
            90 * 16,
            int(
                -buy_angle * 16
            ),
        )

        painter.setPen(
            QPen(
                QColor(RED),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            rect,
            int(
                (
                    90
                    - buy_angle
                )
                * 16
            ),
            int(
                -(
                    360
                    - buy_angle
                )
                * 16
            ),
        )

        painter.setPen(
            QColor(TEXT)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                21,
                QFont.Bold,
            )
        )

        painter.drawText(
            QRectF(
                rect.left(),
                rect.top() + 30,
                rect.width(),
                38,
            ),
            Qt.AlignCenter,
            str(self.total),
        )

        painter.setPen(
            QColor(MUTED)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                9,
                QFont.Bold,
            )
        )

        painter.drawText(
            QRectF(
                rect.left(),
                rect.top() + 65,
                rect.width(),
                24,
            ),
            Qt.AlignCenter,
            "TOTAL",
        )


# =========================================================
# MARKET PULSE GRAPHIC
# =========================================================

class MarketPulseGraphic(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.setMinimumHeight(135)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()
        height = self.height()

        # -------------------------------------------------
        # BULL HEAD / HORNS
        # -------------------------------------------------

        center_x = width * 0.20
        center_y = height * 0.42

        painter.setPen(
            QPen(
                QColor(GREEN),
                4,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )

        painter.drawArc(
            QRectF(
                center_x - 27,
                center_y - 15,
                54,
                40,
            ),
            200 * 16,
            140 * 16,
        )

        painter.drawLine(
            QPointF(
                center_x - 23,
                center_y - 3,
            ),
            QPointF(
                center_x - 39,
                center_y - 22,
            ),
        )

        painter.drawLine(
            QPointF(
                center_x + 23,
                center_y - 3,
            ),
            QPointF(
                center_x + 39,
                center_y - 22,
            ),
        )

        painter.drawLine(
            QPointF(
                center_x - 14,
                center_y + 18,
            ),
            QPointF(
                center_x - 8,
                center_y + 31,
            ),
        )

        painter.drawLine(
            QPointF(
                center_x + 14,
                center_y + 18,
            ),
            QPointF(
                center_x + 8,
                center_y + 31,
            ),
        )

        # -------------------------------------------------
        # TREND AREA
        # -------------------------------------------------

        start_x = width * 0.36

        points = [
            QPointF(
                start_x,
                height * 0.74,
            ),
            QPointF(
                width * 0.47,
                height * 0.62,
            ),
            QPointF(
                width * 0.56,
                height * 0.69,
            ),
            QPointF(
                width * 0.66,
                height * 0.45,
            ),
            QPointF(
                width * 0.76,
                height * 0.53,
            ),
            QPointF(
                width * 0.87,
                height * 0.29,
            ),
            QPointF(
                width * 0.96,
                height * 0.17,
            ),
        ]

        line_path = QPainterPath()

        line_path.moveTo(
            points[0]
        )

        for point in points[1:]:
            line_path.lineTo(point)

        area_path = QPainterPath(
            line_path
        )

        area_path.lineTo(
            points[-1].x(),
            height - 12,
        )

        area_path.lineTo(
            points[0].x(),
            height - 12,
        )

        area_path.closeSubpath()

        gradient = QLinearGradient(
            0,
            0,
            0,
            height,
        )

        gradient.setColorAt(
            0,
            QColor(
                40,
                209,
                124,
                90,
            ),
        )

        gradient.setColorAt(
            1,
            QColor(
                40,
                209,
                124,
                3,
            ),
        )

        painter.fillPath(
            area_path,
            gradient,
        )

        painter.setPen(
            QPen(
                QColor(GREEN),
                4,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )

        painter.drawPath(
            line_path
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(GREEN)
        )

        painter.drawEllipse(
            points[-1],
            6,
            6,
        )


# =========================================================
# DERIVATIVES GAUGE
# =========================================================

class DerivativesGauge(QWidget):

    def __init__(
        self,
        score: float = 68,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.score = max(
            0.0,
            min(
                100.0,
                float(score),
            ),
        )

        self.setMinimumHeight(125)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()

        diameter = min(
            width - 30,
            170,
        )

        rect = QRectF(
            (
                width
                - diameter
            ) / 2,
            20,
            diameter,
            diameter,
        )

        pen_width = 13

        zones = [
            (
                RED,
                180,
                -60,
            ),
            (
                ORANGE,
                120,
                -60,
            ),
            (
                GREEN,
                60,
                -60,
            ),
        ]

        for (
            color,
            start,
            span,
        ) in zones:

            painter.setPen(
                QPen(
                    QColor(color),
                    pen_width,
                    Qt.SolidLine,
                    Qt.RoundCap,
                )
            )

            painter.drawArc(
                rect,
                start * 16,
                span * 16,
            )

        angle = (
            180
            - (
                self.score
                / 100
                * 180
            )
        )

        radians = math.radians(
            angle
        )

        center = QPointF(
            rect.center().x(),
            rect.center().y(),
        )

        radius = (
            diameter / 2
            - 20
        )

        endpoint = QPointF(
            center.x()
            + radius
            * math.cos(radians),
            center.y()
            - radius
            * math.sin(radians),
        )

        painter.setPen(
            QPen(
                QColor(TEXT),
                3,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawLine(
            center,
            endpoint,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(TEXT)
        )

        painter.drawEllipse(
            center,
            5,
            5,
        )

        painter.setPen(
            QColor(GREEN)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Bold,
            )
        )

        painter.drawText(
            QRectF(
                0,
                88,
                width,
                28,
            ),
            Qt.AlignCenter,
            "BULLISH",
        )


# =========================================================
# FLOW BAR
# =========================================================

class FlowBar(QWidget):

    def __init__(
        self,
        label: str,
        value: float,
        maximum: float,
        color: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.label = label
        self.value = value
        self.maximum = max(
            abs(maximum),
            1,
        )

        self.color = color

        self.setMinimumHeight(52)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()

        painter.setPen(
            QColor(TEXT_SOFT)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Bold,
            )
        )

        painter.drawText(
            QRectF(
                0,
                0,
                45,
                24,
            ),
            Qt.AlignLeft
            | Qt.AlignVCenter,
            self.label,
        )

        sign = (
            "+"
            if self.value > 0
            else ""
        )

        painter.setPen(
            QColor(self.color)
        )

        painter.drawText(
            QRectF(
                48,
                0,
                width - 48,
                24,
            ),
            Qt.AlignRight
            | Qt.AlignVCenter,
            f"{sign}₹{self.value:,.0f} Cr",
        )

        bar_rect = QRectF(
            0,
            31,
            width,
            11,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(TRACK)
        )

        painter.drawRoundedRect(
            bar_rect,
            5,
            5,
        )

        ratio = min(
            1.0,
            abs(self.value)
            / self.maximum,
        )

        painter.setBrush(
            QColor(self.color)
        )

        painter.drawRoundedRect(
            QRectF(
                0,
                31,
                width * ratio,
                11,
            ),
            5,
            5,
        )


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
        # MARKET CONTROLLER COMPATIBILITY
        # -------------------------------------------------

        self.index_cards: Dict[
            str,
            IndexCard,
        ] = {
            "NIFTY":
                IndexCard(
                    "NIFTY 50"
                ),

            "BANKNIFTY":
                IndexCard(
                    "BANK NIFTY"
                ),

            "FINNIFTY":
                IndexCard(
                    "FIN NIFTY"
                ),

            "INDIAVIX":
                IndexCard(
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
            0,
            0,
            0,
            0,
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
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background: {BG};
            }}

            QScrollBar:vertical {{
                background: {BG};
                width: 10px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background: #263850;
                border-radius: 5px;
                min-height: 40px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #355071;
            }}

            QScrollBar:horizontal {{
                background: {BG};
                height: 10px;
            }}

            QScrollBar::handle:horizontal {{
                background: #263850;
                border-radius: 5px;
                min-width: 40px;
            }}
            """
        )

        content = QWidget()

        content.setObjectName(
            "dashboardContent"
        )

        content.setMinimumWidth(
            1450
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
            20,
            18,
            20,
            22,
        )

        self.grid.setHorizontalSpacing(
            14
        )

        self.grid.setVerticalSpacing(
            14
        )

        # -------------------------------------------------
        # ROW 1
        # -------------------------------------------------

        self.grid.addWidget(
            self._top_opportunities(),
            0,
            0,
            1,
            2,
        )

        self.grid.addWidget(
            self._sector_strength(),
            0,
            2,
        )

        self.grid.addWidget(
            self._market_breadth(),
            0,
            3,
        )

        self.grid.addWidget(
            self._market_heatmap(),
            0,
            4,
        )

        # -------------------------------------------------
        # ROW 2
        # -------------------------------------------------

        self.grid.addWidget(
            self._scanner_summary(),
            1,
            0,
        )

        self.grid.addWidget(
            self._top_movers(),
            1,
            1,
        )

        self.grid.addWidget(
            self._live_alerts(),
            1,
            2,
            1,
            2,
        )

        self.grid.addWidget(
            self._watchlist(),
            1,
            4,
        )

        # -------------------------------------------------
        # ROW 3
        # -------------------------------------------------

        self.grid.addWidget(
            self._market_pulse(),
            2,
            0,
            1,
            2,
        )

        self.grid.addWidget(
            self._recent_news(),
            2,
            2,
        )

        self.grid.addWidget(
            self._institutional_flow(),
            2,
            3,
        )

        self.grid.addWidget(
            self._derivatives_pulse(),
            2,
            4,
        )

        # -------------------------------------------------
        # COLUMN RATIOS
        # -------------------------------------------------

        self.grid.setColumnStretch(
            0,
            13,
        )

        self.grid.setColumnStretch(
            1,
            13,
        )

        self.grid.setColumnStretch(
            2,
            11,
        )

        self.grid.setColumnStretch(
            3,
            11,
        )

        self.grid.setColumnStretch(
            4,
            11,
        )

        self.grid.setRowStretch(
            0,
            1,
        )

        self.grid.setRowStretch(
            1,
            1,
        )

        self.grid.setRowStretch(
            2,
            1,
        )

        self.scroll.setWidget(
            content
        )

        root.addWidget(
            self.scroll
        )


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

        label.setStyleSheet(
            f"""
            color: {color};
            font-size: {size}px;
            font-weight: {
                700
                if bold
                else 500
            };
            """
        )

        return label


    def _row(
        self,
        left: str,
        right: str,
        right_color: str = TEXT,
        height: int = 34,
    ):

        widget = QWidget()

        widget.setMinimumHeight(
            height
        )

        layout = QHBoxLayout(
            widget
        )

        layout.setContentsMargins(
            0,
            4,
            0,
            4,
        )

        layout.setSpacing(8)

        left_label = self._text(
            left,
            TEXT_SOFT,
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


    def _separator(self):

        line = QFrame()

        line.setFrameShape(
            QFrame.HLine
        )

        line.setStyleSheet(
            f"""
            background: {BORDER};
            max-height: 1px;
            border: none;
            """
        )

        return line


    def _progress(
        self,
        value: int,
        color: str,
    ):

        progress = QProgressBar()

        progress.setRange(
            0,
            100,
        )

        progress.setValue(
            value
        )

        progress.setTextVisible(
            False
        )

        progress.setFixedHeight(
            8
        )

        progress.setStyleSheet(
            f"""
            QProgressBar {{
                background: {TRACK};
                border: none;
                border-radius: 4px;
            }}

            QProgressBar::chunk {{
                background: {color};
                border-radius: 4px;
            }}
            """
        )

        return progress


    # =====================================================
    # TOP OPPORTUNITIES
    # =====================================================

    def _top_opportunities(self):

        card = DashboardCard(
            "Top Opportunities"
        )

        header = QWidget()

        layout = QHBoxLayout(
            header
        )

        layout.setContentsMargins(
            0,
            2,
            0,
            5,
        )

        symbol = self._text(
            "SYMBOL / SIGNAL",
            MUTED,
            11,
            True,
        )

        score = self._text(
            "SCORE / PRICE",
            MUTED,
            11,
            True,
        )

        layout.addWidget(
            symbol
        )

        layout.addStretch()

        layout.addWidget(
            score
        )

        card.layout.addWidget(
            header
        )

        opportunities = [
            (
                "RELIANCE",
                "BUY",
                92,
                "2,984.40",
            ),
            (
                "HDFCBANK",
                "BUY",
                88,
                "1,742.10",
            ),
            (
                "TCS",
                "BUY",
                86,
                "4,186.25",
            ),
            (
                "INFY",
                "SELL",
                82,
                "1,928.70",
            ),
            (
                "ICICIBANK",
                "BUY",
                79,
                "1,326.50",
            ),
        ]

        for (
            symbol,
            signal,
            score,
            price,
        ) in opportunities:

            color = (
                GREEN
                if signal == "BUY"
                else RED
            )

            card.layout.addWidget(
                self._row(
                    f"{symbol}   {signal}",
                    f"{score}   ₹{price}",
                    color,
                    37,
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

        sectors = [
            (
                "IT",
                88,
                "+1.8%",
                GREEN,
            ),
            (
                "BANK",
                76,
                "+1.2%",
                GREEN,
            ),
            (
                "AUTO",
                67,
                "+0.9%",
                GREEN,
            ),
            (
                "PHARMA",
                54,
                "+0.4%",
                BLUE,
            ),
            (
                "METAL",
                35,
                "-0.6%",
                RED,
            ),
        ]

        for (
            name,
            strength,
            change,
            color,
        ) in sectors:

            top = QWidget()

            row = QHBoxLayout(
                top
            )

            row.setContentsMargins(
                0,
                2,
                0,
                2,
            )

            row.addWidget(
                self._text(
                    name,
                    TEXT_SOFT,
                    13,
                    True,
                )
            )

            row.addStretch()

            row.addWidget(
                self._text(
                    change,
                    color,
                    13,
                    True,
                )
            )

            card.layout.addWidget(
                top
            )

            card.layout.addWidget(
                self._progress(
                    strength,
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

        self.breadth_gauge = (
            BreadthGauge(64)
        )

        card.layout.addWidget(
            self.breadth_gauge
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

        grid.setContentsMargins(
            0,
            2,
            0,
            0,
        )

        grid.setSpacing(7)

        items = [
            (
                "RELIANCE",
                "+1.6%",
                GREEN,
            ),
            (
                "TCS",
                "+1.2%",
                GREEN,
            ),
            (
                "HDFC",
                "+0.9%",
                GREEN,
            ),
            (
                "INFY",
                "-0.7%",
                RED,
            ),
            (
                "ICICI",
                "+1.1%",
                GREEN,
            ),
            (
                "SBIN",
                "+1.4%",
                GREEN,
            ),
            (
                "ITC",
                "-0.5%",
                RED,
            ),
            (
                "LT",
                "+0.8%",
                GREEN,
            ),
            (
                "AXIS",
                "+1.0%",
                GREEN,
            ),
        ]

        for (
            index,
            (
                symbol,
                change,
                color,
            ),
        ) in enumerate(items):

            tile = QLabel(
                f"{symbol}\n{change}"
            )

            tile.setAlignment(
                Qt.AlignCenter
            )

            tile.setMinimumHeight(
                58
            )

            tile.setStyleSheet(
                f"""
                QLabel {{
                    background: {color};
                    color: #ffffff;
                    border-radius: 7px;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 4px;
                }}
                """
            )

            grid.addWidget(
                tile,
                index // 3,
                index % 3,
            )

        card.layout.addLayout(
            grid
        )

        return card


    # =====================================================
    # SCANNER SUMMARY
    # =====================================================

    def _scanner_summary(self):

        card = DashboardCard(
            "Scanner Summary"
        )

        self.scanner_donut = (
            ScannerDonut(
                total=127,
                buys=74,
                sells=53,
            )
        )

        card.layout.addWidget(
            self.scanner_donut
        )

        stats = QHBoxLayout()

        stats.setSpacing(10)

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

        return card


    # =====================================================
    # TOP MOVERS
    # =====================================================

    def _top_movers(self):

        card = DashboardCard(
            "Top Movers"
        )

        movers = [
            (
                "TRENT",
                "+5.42%",
                GREEN,
            ),
            (
                "BEL",
                "+4.18%",
                GREEN,
            ),
            (
                "HAL",
                "+3.91%",
                GREEN,
            ),
            (
                "BAJFINANCE",
                "-2.64%",
                RED,
            ),
            (
                "TATASTEEL",
                "-2.12%",
                RED,
            ),
        ]

        for (
            symbol,
            value,
            color,
        ) in movers:

            card.layout.addWidget(
                self._row(
                    symbol,
                    value,
                    color,
                    39,
                )
            )

            card.layout.addWidget(
                self._progress(
                    min(
                        100,
                        int(
                            abs(
                                float(
                                    value.replace(
                                        "%",
                                        "",
                                    )
                                )
                            )
                            * 15
                        ),
                    ),
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
            (
                "RELIANCE",
                "Breakout above VWAP",
                GREEN,
            ),
            (
                "HDFCBANK",
                "Volume expansion",
                GREEN,
            ),
            (
                "INFY",
                "Momentum weakening",
                RED,
            ),
            (
                "TCS",
                "High confidence setup",
                BLUE,
            ),
        ]

        for (
            symbol,
            message,
            color,
        ) in alerts:

            container = QFrame()

            container.setStyleSheet(
                f"""
                QFrame {{
                    background: {PANEL_ALT};
                    border: 1px solid {BORDER};
                    border-radius: 7px;
                }}
                """
            )

            row = QHBoxLayout(
                container
            )

            row.setContentsMargins(
                12,
                9,
                12,
                9,
            )

            symbol_label = (
                self._text(
                    symbol,
                    TEXT,
                    13,
                    True,
                )
            )

            message_label = (
                self._text(
                    message,
                    color,
                    13,
                    True,
                )
            )

            row.addWidget(
                symbol_label
            )

            row.addStretch()

            row.addWidget(
                message_label
            )

            card.layout.addWidget(
                container
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

        stocks = [
            (
                "RELIANCE",
                "₹2,984.40",
                "+1.62%",
            ),
            (
                "HDFCBANK",
                "₹1,742.10",
                "+1.14%",
            ),
            (
                "TCS",
                "₹4,186.25",
                "+0.92%",
            ),
            (
                "SBIN",
                "₹842.30",
                "+1.43%",
            ),
            (
                "LT",
                "₹3,628.75",
                "+0.81%",
            ),
        ]

        for (
            symbol,
            price,
            change,
        ) in stocks:

            wrapper = QWidget()

            row = QHBoxLayout(
                wrapper
            )

            row.setContentsMargins(
                0,
                4,
                0,
                4,
            )

            left = QVBoxLayout()

            left.setSpacing(1)

            left.addWidget(
                self._text(
                    symbol,
                    TEXT,
                    13,
                    True,
                )
            )

            left.addWidget(
                self._text(
                    change,
                    GREEN,
                    11,
                    True,
                )
            )

            row.addLayout(
                left
            )

            row.addStretch()

            row.addWidget(
                self._text(
                    price,
                    TEXT_SOFT,
                    13,
                    True,
                )
            )

            card.layout.addWidget(
                wrapper
            )

        return card


    # =====================================================
    # MARKET PULSE
    # =====================================================

    def _market_pulse(self):

        card = DashboardCard(
            "Market Pulse"
        )

        header = QWidget()

        header_layout = QHBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        status = QLabel(
            "BULLISH"
        )

        status.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 28px;
            font-weight: 800;
            """
        )

        score = QLabel(
            "78 / 100"
        )

        score.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 17px;
            font-weight: 700;
            """
        )

        header_layout.addWidget(
            status
        )

        header_layout.addStretch()

        header_layout.addWidget(
            score
        )

        card.layout.addWidget(
            header
        )

        self.market_pulse_graphic = (
            MarketPulseGraphic()
        )

        card.layout.addWidget(
            self.market_pulse_graphic
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
    # NEWS
    # =====================================================

    def _recent_news(self):

        card = DashboardCard(
            "Recent News"
        )

        news = [
            (
                "10:21",
                "Markets trade higher on broad buying",
            ),
            (
                "10:08",
                "Banking stocks lead index gains",
            ),
            (
                "09:54",
                "IT shares see renewed momentum",
            ),
            (
                "09:41",
                "FII activity remains in focus",
            ),
        ]

        for (
            time,
            headline,
        ) in news:

            item = QWidget()

            row = QHBoxLayout(
                item
            )

            row.setContentsMargins(
                0,
                7,
                0,
                7,
            )

            time_label = (
                self._text(
                    time,
                    BLUE,
                    11,
                    True,
                )
            )

            headline_label = (
                self._text(
                    headline,
                    TEXT_SOFT,
                    13,
                    False,
                )
            )

            headline_label.setWordWrap(
                True
            )

            row.addWidget(
                time_label
            )

            row.addWidget(
                headline_label,
                1,
            )

            card.layout.addWidget(
                item
            )

            card.layout.addWidget(
                self._separator()
            )

        card.layout.addStretch()

        return card


    # =====================================================
    # INSTITUTIONAL FLOW
    # =====================================================

    def _institutional_flow(self):

        card = DashboardCard(
            "Institutional Flow"
        )

        self.fii_flow = FlowBar(
            "FII",
            -1842,
            2500,
            RED,
        )

        self.dii_flow = FlowBar(
            "DII",
            2216,
            2500,
            GREEN,
        )

        card.layout.addWidget(
            self.fii_flow
        )

        card.layout.addWidget(
            self.dii_flow
        )

        card.layout.addWidget(
            self._separator()
        )

        card.layout.addWidget(
            self._row(
                "Net Flow",
                "+₹374 Cr",
                GREEN,
            )
        )

        card.layout.addWidget(
            self._row(
                "Bias",
                "Domestic Support",
                BLUE,
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

        self.derivatives_gauge = (
            DerivativesGauge(68)
        )

        card.layout.addWidget(
            self.derivatives_gauge
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
                TEXT_SOFT,
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