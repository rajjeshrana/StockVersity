"""
StockVersity Scanner Pro
Frozen Dashboard UI

Approved layout:
ROW 1
    Market Pulse
    Sector Strength
    Market Breadth
    Market Heatmap

ROW 2
    Top Opportunities
    Scanner Summary
    Top Movers
    Live Scanner Alerts

ROW 3
    Institutional Flow
    Derivatives Pulse
    NIFTY OI Chart

Compatibility preserved for:
    MarketController
    LiveMarketBridge
    ui.app
"""

from __future__ import annotations
from datetime import datetime

import math
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    Signal,
)

from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# =========================================================
# COLORS
# =========================================================

BG = "#07101d"
PANEL = "#0b1829"
PANEL_ALT = "#0d1d30"
ROW_BG = "#0a1626"

BORDER = "#1c3047"
BORDER_SOFT = "#15283d"

TEXT = "#f4f7fb"
MUTED = "#8ba0bd"

BLUE = "#3182ff"
CYAN = "#18bfff"

GREEN = "#20d77a"
GREEN_DARK = "#087b46"

RED = "#ff4f62"
RED_DARK = "#8e1726"

ORANGE = "#ffad1f"
YELLOW = "#ffd02a"
PURPLE = "#8b62ff"

TRACK = "#172a42"


# =========================================================
# HELPERS
# =========================================================

def movement_color(value: float) -> str:
    if value > 0:
        return GREEN

    if value < 0:
        return RED

    return MUTED


def percentage_text(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def make_label(
    text: str,
    size: int = 13,
    color: str = TEXT,
    bold: bool = False,
) -> QLabel:

    label = QLabel(text)

    weight = 700 if bold else 400

    label.setStyleSheet(
        f"""
        QLabel {{
            background: transparent;
            border: none;
            color: {color};
            font-size: {size}px;
            font-weight: {weight};
        }}
        """
    )

    return label


def horizontal_line() -> QFrame:

    line = QFrame()

    line.setFixedHeight(1)

    line.setStyleSheet(
        f"""
        background: {BORDER_SOFT};
        border: none;
        """
    )

    return line


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
                border-radius: 10px;
            }}
            """
        )

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        self.layout.setSpacing(9)

        if title:

            title_label = QLabel(title)

            title_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {TEXT};
                    background: transparent;
                    border: none;
                    font-size: 17px;
                    font-weight: 800;
                }}
                """
            )

            self.layout.addWidget(
                title_label
            )


# =========================================================
# INDEX CARD
# Used by ui.app header + MarketController
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

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

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
            8,
            3,
            8,
            3,
        )

        layout.setSpacing(1)

        self.name_label = QLabel(name)

        self.name_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 12px;
            font-weight: 800;
            """
        )

        self.value_label = QLabel("--")

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 17px;
            font-weight: 800;
            """
        )

        self.change_label = QLabel("--")

        self.change_label.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 11px;
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
    ) -> None:

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

        color = movement_color(
            change
        )

        self.change_label.setText(
            percentage_text(change)
        )

        self.change_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 11px;
            font-weight: 800;
            """
        )

        self.history = list(
            history or []
        )


# =========================================================
# MARKET BREADTH VALUE CARD
#
# IMPORTANT:
# MarketController searches for these by objectName:
#
# advance_card
# decline_card
# unchanged_card
#
# and calls set_value()
# =========================================================

class BreadthValue(QWidget):

    def __init__(
        self,
        object_name: str,
        title: str,
        value: str,
        value_color: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.setObjectName(
            object_name
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            2,
            0,
            2,
        )

        self.title_label = make_label(
            title,
            12,
            TEXT,
            True,
        )

        self.value_label = make_label(
            value,
            13,
            value_color,
            True,
        )

        layout.addWidget(
            self.title_label
        )

        layout.addStretch(1)

        layout.addWidget(
            self.value_label
        )

    def set_value(
        self,
        value: str,
    ) -> None:

        self.value_label.setText(
            str(value)
        )


# =========================================================
# PROGRESS BAR
# =========================================================

class StrengthBar(QWidget):

    def __init__(
        self,
        value: float = 50,
        color: str = GREEN,
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

        self.bar_color = QColor(
            color
        )

        self.setFixedHeight(12)

    def set_value(
        self,
        value: float,
    ) -> None:

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0

        self.value = max(
            0,
            min(
                100,
                value,
            ),
        )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect().adjusted(
            0,
            2,
            0,
            -2,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(TRACK)
        )

        painter.drawRoundedRect(
            rect,
            4,
            4,
        )

        width = int(
            rect.width()
            * self.value
            / 100
        )

        if width > 0:

            fill_rect = QRectF(
                rect.x(),
                rect.y(),
                width,
                rect.height(),
            )

            painter.setBrush(
                self.bar_color
            )

            painter.drawRoundedRect(
                fill_rect,
                4,
                4,
            )


# =========================================================
# SCANNER SUMMARY DONUT
# =========================================================

class DonutChart(QWidget):

    def __init__(
        self,
        total: int = 127,
        buy: int = 74,
        sell: int = 53,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.total = total
        self.buy = buy
        self.sell = sell

        self.setMinimumSize(
            115,
            115,
        )

        self.setMaximumHeight(
            125
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        size = min(
            self.width(),
            self.height(),
        ) - 24

        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        pen = QPen()

        pen.setWidth(16)
        pen.setCapStyle(
            Qt.RoundCap
        )

        # Background
        pen.setColor(
            QColor(TRACK)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            0,
            360 * 16,
        )

        total_parts = max(
            self.buy + self.sell,
            1,
        )

        buy_angle = int(
            360
            * self.buy
            / total_parts
            * 16
        )

        sell_angle = (
            360 * 16
            - buy_angle
        )

        # BUY
        pen.setColor(
            QColor(GREEN)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            90 * 16,
            -buy_angle,
        )

        # SELL
        pen.setColor(
            QColor(RED)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            (90 * 16) - buy_angle,
            -sell_angle,
        )

        painter.setPen(
            QColor(TEXT)
        )

        font = QFont(
            "Segoe UI",
            21,
            QFont.Bold,
        )

        painter.setFont(font)

        painter.drawText(
            rect,
            Qt.AlignCenter,
            str(self.total),
        )


# =========================================================
# MARKET BREADTH GAUGE
# =========================================================

class BreadthGauge(QWidget):

    def __init__(
        self,
        value: float = 64,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.value = value

        self.setMinimumHeight(
            100
        )

        self.setMaximumHeight(
            115
        )

    def set_value(
        self,
        value: float,
    ) -> None:

        try:
            self.value = float(value)
        except (TypeError, ValueError):
            self.value = 0

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = min(
            self.width() - 42,
            138,
        )

        rect = QRectF(
            (self.width() - width) / 2,
            5,
            width,
            width,
        )

        pen = QPen()

        pen.setWidth(14)

        pen.setCapStyle(
            Qt.RoundCap
        )

        # Background semicircle
        pen.setColor(
            QColor(TRACK)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            0,
            180 * 16,
        )

        value = max(
            0,
            min(
                100,
                self.value,
            ),
        )

        angle = int(
            180
            * value
            / 100
            * 16
        )

        pen.setColor(
            QColor(GREEN)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            180 * 16,
            -angle,
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

        text_rect = QRectF(
            rect.x(),
            rect.y() + 30,
            rect.width(),
            46,
        )

        painter.drawText(
            text_rect,
            Qt.AlignCenter,
            f"{int(value)}%",
        )


# =========================================================
# MARKET PULSE TREND GRAPH
# =========================================================

class PulseTrendGraph(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.values = [
            32,
            39,
            35,
            48,
            44,
            55,
            61,
            58,
            70,
            66,
            79,
        ]

        self.setMinimumHeight(
            88
        )

        self.setMaximumHeight(
            105
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        area = self.rect().adjusted(
            8,
            12,
            -8,
            -12,
        )

        # Grid
        grid_pen = QPen(
            QColor("#18324d")
        )

        grid_pen.setWidth(1)

        painter.setPen(
            grid_pen
        )

        for i in range(4):

            y = (
                area.top()
                + (
                    area.height()
                    * i
                    / 3
                )
            )

            painter.drawLine(
                QPointF(
                    area.left(),
                    y,
                ),
                QPointF(
                    area.right(),
                    y,
                ),
            )

        if len(self.values) < 2:
            return

        minimum = min(
            self.values
        )

        maximum = max(
            self.values
        )

        spread = max(
            maximum - minimum,
            1,
        )

        points: List[QPointF] = []

        for i, value in enumerate(
            self.values
        ):

            x = (
                area.left()
                + (
                    area.width()
                    * i
                    / (
                        len(self.values)
                        - 1
                    )
                )
            )

            normalized = (
                value - minimum
            ) / spread

            y = (
                area.bottom()
                - (
                    normalized
                    * area.height()
                    * 0.75
                )
                - 8
            )

            points.append(
                QPointF(
                    x,
                    y,
                )
            )

        path = QPainterPath()

        path.moveTo(
            points[0]
        )

        for point in points[1:]:
            path.lineTo(point)

        pen = QPen(
            QColor(GREEN)
        )

        pen.setWidth(3)

        painter.setPen(pen)

        painter.drawPath(path)

        # small endpoint dots
        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(GREEN)
        )

        for point in points:
            painter.drawEllipse(
                point,
                3.5,
                3.5,
            )


# =========================================================
# APPROVED BULL / BEAR MARKET SYMBOL
# =========================================================

class MarketAnimalGraphic(QWidget):

    """Approved image-based bull / bear Market Pulse graphic."""

    def __init__(
        self,
        bullish: bool = True,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.bullish = bool(bullish)
        self.setMinimumSize(145, 95)
        self.setMaximumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Assets live in: ui/assets/market/
        self._asset_dir = Path(__file__).resolve().parents[1] / "assets" / "market"
        self._bull_path = self._asset_dir / "bull.png"
        self._bear_path = self._asset_dir / "bear.png"

        self._bull_pixmap = QPixmap(str(self._bull_path))
        self._bear_pixmap = QPixmap(str(self._bear_path))

    def set_bullish(self, bullish: bool) -> None:
        self.bullish = bool(bullish)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        pixmap = self._bull_pixmap if self.bullish else self._bear_pixmap

        if pixmap.isNull():
            # Clear fallback if an asset was accidentally not copied.
            painter.setPen(QColor(GREEN if self.bullish else RED))
            font = QFont("Segoe UI", 13, QFont.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "BULL" if self.bullish else "BEAR")
            return

        margin = 4
        target = self.rect().adjusted(margin, margin, -margin, -margin)
        scaled = pixmap.scaled(
            target.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        x = target.x() + (target.width() - scaled.width()) // 2
        y = target.y() + (target.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)


# =========================================================
# DERIVATIVES GAUGE
# =========================================================

class DerivativesGauge(QWidget):

    def __init__(
        self,
        value: float = 0.72,
        bullish: bool = True,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.value = max(
            0.0,
            min(
                1.0,
                value,
            ),
        )

        self.bullish = bullish

        self.setMinimumHeight(
            105
        )

        self.setMaximumHeight(
            120
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        size = min(
            self.width() - 36,
            135,
        )

        rect = QRectF(
            (self.width() - size) / 2,
            6,
            size,
            size,
        )

        pen = QPen()

        pen.setWidth(16)

        pen.setCapStyle(
            Qt.RoundCap
        )

        # red zone
        pen.setColor(
            QColor(RED)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            180 * 16,
            -55 * 16,
        )

        # yellow zone
        pen.setColor(
            QColor(YELLOW)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            125 * 16,
            -55 * 16,
        )

        # green zone
        pen.setColor(
            QColor(GREEN)
        )

        painter.setPen(pen)

        painter.drawArc(
            rect,
            70 * 16,
            -70 * 16,
        )

        # Needle
        angle_deg = (
            180
            - (
                180
                * self.value
            )
        )

        angle = math.radians(
            angle_deg
        )

        center = QPointF(
            rect.center().x(),
            rect.center().y(),
        )

        radius = (
            rect.width()
            * 0.38
        )

        end = QPointF(
            center.x()
            + radius
            * math.cos(angle),
            center.y()
            - radius
            * math.sin(angle),
        )

        needle_pen = QPen(
            QColor(TEXT)
        )

        needle_pen.setWidth(4)

        painter.setPen(
            needle_pen
        )

        painter.drawLine(
            center,
            end,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(TEXT)
        )

        painter.drawEllipse(
            center,
            7,
            7,
        )


# =========================================================
# NIFTY OI CHART
# =========================================================

class NiftyOIChart(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.setMinimumHeight(
            105
        )

        self.setMaximumHeight(
            135
        )

        self.call_values = [
            11,
            14,
            18,
            13,
            9,
            16,
            21,
            17,
            12,
            20,
            15,
            19,
        ]

        self.put_values = [
            8,
            11,
            14,
            17,
            19,
            13,
            16,
            22,
            18,
            15,
            21,
            23,
        ]

        self.price_values = [
            42,
            45,
            49,
            53,
            57,
            59,
            61,
            60,
            63,
            68,
            73,
            80,
        ]

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        area = self.rect().adjusted(
            28,
            10,
            -14,
            -12,
        )

        count = len(
            self.call_values
        )

        if count == 0:
            return

        group_width = (
            area.width()
            / count
        )

        max_oi = max(
            max(self.call_values),
            max(self.put_values),
            1,
        )

        # horizontal grid
        grid_pen = QPen(
            QColor("#17304a")
        )

        grid_pen.setWidth(1)

        painter.setPen(
            grid_pen
        )

        for i in range(4):

            y = (
                area.top()
                + (
                    area.height()
                    * i
                    / 3
                )
            )

            painter.drawLine(
                QPointF(
                    area.left(),
                    y,
                ),
                QPointF(
                    area.right(),
                    y,
                ),
            )

        # bars
        for i in range(count):

            base_x = (
                area.left()
                + i
                * group_width
            )

            call_h = (
                area.height()
                * 0.55
                * self.call_values[i]
                / max_oi
            )

            put_h = (
                area.height()
                * 0.55
                * self.put_values[i]
                / max_oi
            )

            bar_w = max(
                4,
                group_width * 0.22,
            )

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                QColor(GREEN)
            )

            painter.drawRect(
                QRectF(
                    base_x
                    + group_width * 0.20,
                    area.bottom()
                    - call_h,
                    bar_w,
                    call_h,
                )
            )

            painter.setBrush(
                QColor(RED)
            )

            painter.drawRect(
                QRectF(
                    base_x
                    + group_width * 0.52,
                    area.bottom()
                    - put_h,
                    bar_w,
                    put_h,
                )
            )

        # Price line
        minimum = min(
            self.price_values
        )

        maximum = max(
            self.price_values
        )

        spread = max(
            maximum - minimum,
            1,
        )

        path = QPainterPath()

        for i, value in enumerate(
            self.price_values
        ):

            x = (
                area.left()
                + group_width
                * (
                    i + 0.5
                )
            )

            normalized = (
                value - minimum
            ) / spread

            y = (
                area.top()
                + area.height()
                * 0.45
                * (
                    1 - normalized
                )
            )

            point = QPointF(
                x,
                y,
            )

            if i == 0:
                path.moveTo(
                    point
                )
            else:
                path.lineTo(
                    point
                )

        price_pen = QPen(
            QColor(BLUE)
        )

        price_pen.setWidth(3)

        painter.setPen(
            price_pen
        )

        painter.drawPath(
            path
        )


# =========================================================
# END OF PART 1
# =========================================================
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
            "dashboardPage"
        )

        self.setStyleSheet(
            f"""
            QWidget#dashboardPage {{
                background: {BG};
            }}

            QLabel {{
                font-family: "Segoe UI";
            }}
            """
        )

        # -------------------------------------------------
        # LIVE INDEX CARDS
        #
        # IMPORTANT:
        # app.py and MarketController use these directly.
        #
        # FINNIFTY deliberately NOT included.
        # -------------------------------------------------

        self.index_cards: Dict[str, IndexCard] = {
            "NIFTY": IndexCard("NIFTY 50"),
            "BANKNIFTY": IndexCard("BANK NIFTY"),
            "INDIAVIX": IndexCard("INDIA VIX"),
        }

        # -------------------------------------------------
        # Dynamic references
        # -------------------------------------------------

        self.advance_card = None
        self.decline_card = None
        self.unchanged_card = None

        self.market_pulse_status = None
        self.market_animal = None

        self._build_ui()


    # =====================================================
    # BUILD COMPLETE DASHBOARD
    # =====================================================

    def _build_ui(self) -> None:
        """
        Build StockVersity professional dashboard.

        Layout:
            3 cards per row
            4 dashboard rows

        Scrolling:
            ONLY dashboard card area scrolls vertically.

        Fixed outside this widget:
            Main header
            Sidebar
            Bottom status bar

        Live-market card references are preserved.
        """

        # -------------------------------------------------
        # Local import
        #
        # Keeping QScrollArea local means we do not need
        # to modify the existing Qt import block.
        # -------------------------------------------------

        from PySide6.QtWidgets import QScrollArea

        # -------------------------------------------------
        # ROOT
        # -------------------------------------------------

        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(0)

        # -------------------------------------------------
        # SCROLL AREA
        #
        # IMPORTANT:
        # Only DashboardPage content scrolls.
        # Header/sidebar/footer remain controlled by app.py
        # and therefore remain fixed.
        # -------------------------------------------------

        self.dashboard_scroll = QScrollArea()

        self.dashboard_scroll.setObjectName(
            "dashboardScroll"
        )

        self.dashboard_scroll.setWidgetResizable(
            True
        )

        self.dashboard_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.dashboard_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.dashboard_scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.dashboard_scroll.setStyleSheet(
            f"""
            QScrollArea#dashboardScroll {{
                background: {BG};
                border: none;
            }}

            QScrollArea#dashboardScroll > QWidget > QWidget {{
                background: {BG};
            }}

            QScrollBar:vertical {{
                background: {BG};
                width: 10px;
                margin: 2px 2px 2px 2px;
            }}

            QScrollBar::handle:vertical {{
                background: #263b55;
                min-height: 45px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #345170;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        # -------------------------------------------------
        # SCROLL CONTENT
        # -------------------------------------------------

        content = QWidget()

        content.setObjectName(
            "dashboardContent"
        )

        content.setStyleSheet(
            f"""
            QWidget#dashboardContent {{
                background: {BG};
            }}
            """
        )

        # Four proper dashboard rows.
        #
        # This intentionally makes the content taller than
        # the normal viewport so row 4 can be reached with
        # one smooth vertical scroll.

        content.setMinimumHeight(
            1080
        )

        self.grid = QGridLayout(
            content
        )

        self.grid.setContentsMargins(
            14,
            12,
            14,
            14,
        )

        self.grid.setHorizontalSpacing(
            12
        )

        self.grid.setVerticalSpacing(
            12
        )

        # =================================================
        # CREATE ALL CARDS
        # =================================================

        self.market_pulse_card = (
            self._market_pulse()
        )

        self.sector_strength_card = (
            self._sector_strength()
        )

        self.market_breadth_card = (
            self._market_breadth()
        )

        self.market_heatmap_card = (
            self._market_heatmap()
        )

        self.top_opportunities_card = (
            self._top_opportunities()
        )

        self.scanner_summary_card = (
            self._scanner_summary()
        )

        self.top_movers_card = (
            self._top_movers()
        )

        self.live_alerts_card = (
            self._live_scanner_alerts()
        )

        self.institutional_flow_card = (
            self._institutional_flow()
        )

        self.derivatives_card = (
            self._derivatives_pulse()
        )

        self.nifty_oi_card = (
            self._nifty_oi_chart()
        )

        # =================================================
        # ROW 1
        #
        # MARKET PULSE
        # SECTOR STRENGTH
        # MARKET BREADTH
        # =================================================

        self.grid.addWidget(
            self.market_pulse_card,
            0,
            0,
        )

        self.grid.addWidget(
            self.sector_strength_card,
            0,
            1,
        )

        self.grid.addWidget(
            self.market_breadth_card,
            0,
            2,
        )

        # =================================================
        # ROW 2
        #
        # MARKET HEATMAP
        # TOP OPPORTUNITIES
        # SCANNER SUMMARY
        # =================================================

        self.grid.addWidget(
            self.market_heatmap_card,
            1,
            0,
        )

        self.grid.addWidget(
            self.top_opportunities_card,
            1,
            1,
        )

        self.grid.addWidget(
            self.scanner_summary_card,
            1,
            2,
        )

        # =================================================
        # ROW 3
        #
        # TOP MOVERS
        # LIVE ALERTS
        # INSTITUTIONAL FLOW
        # =================================================

        self.grid.addWidget(
            self.top_movers_card,
            2,
            0,
        )

        self.grid.addWidget(
            self.live_alerts_card,
            2,
            1,
        )

        self.grid.addWidget(
            self.institutional_flow_card,
            2,
            2,
        )

        # =================================================
        # ROW 4
        #
        # DERIVATIVES = 1 COLUMN
        # NIFTY OI    = 2 COLUMNS
        #
        # NIFTY OI intentionally receives double width.
        # =================================================

        self.grid.addWidget(
            self.derivatives_card,
            3,
            0,
        )

        self.grid.addWidget(
            self.nifty_oi_card,
            3,
            1,
            1,
            2,
        )

        # =================================================
        # THREE EQUAL COLUMNS
        # =================================================

        for column in range(3):

            self.grid.setColumnStretch(
                column,
                1,
            )

            self.grid.setColumnMinimumWidth(
                column,
                300,
            )

        # =================================================
        # FOUR COMFORTABLE ROWS
        #
        # Larger cards allow readable text, gauges,
        # graphics and tables without overlap.
        # =================================================

        for row in range(4):

            self.grid.setRowStretch(
                row,
                1,
            )

            self.grid.setRowMinimumHeight(
                row,
                250,
            )

        # -------------------------------------------------
        # INSTALL CONTENT INTO SCROLL AREA
        # -------------------------------------------------

        self.dashboard_scroll.setWidget(
            content
        )

        root.addWidget(
            self.dashboard_scroll,
            1,
        )


    # =====================================================
    # GENERIC ROW
    # =====================================================

    def _simple_row(
        self,
        left: str,
        right: str,
        right_color: str = TEXT,
        left_size: int = 12,
        right_size: int = 12,
    ) -> QWidget:

        row = QWidget()

        row.setStyleSheet(
            "background: transparent;"
        )

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            3,
            0,
            3,
        )

        layout.setSpacing(
            6
        )

        left_label = make_label(
            left,
            left_size,
            TEXT,
            True,
        )

        right_label = make_label(
            right,
            right_size,
            right_color,
            True,
        )

        layout.addWidget(
            left_label
        )

        layout.addStretch(1)

        layout.addWidget(
            right_label
        )

        return row


    # =====================================================
    # TABLE ROW
    # =====================================================

    def _table_cell(
        self,
        text: str,
        color: str = TEXT,
        bold: bool = True,
    ) -> QLabel:

        label = QLabel(text)

        label.setAlignment(
            Qt.AlignVCenter
            | Qt.AlignLeft
        )

        label.setStyleSheet(
            f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {color};
                font-size: 12px;
                font-weight: {
                    700 if bold else 500
                };
            }}
            """
        )

        return label


    def _table_row_frame(
        self,
    ) -> QFrame:

        row = QFrame()

        row.setObjectName(
            "tableRow"
        )

        row.setMinimumHeight(
            34
        )

        row.setStyleSheet(
            f"""
            QFrame#tableRow {{
                background: {PANEL_ALT};
                border: none;
                border-radius: 5px;
            }}
            """
        )

        return row


    # =====================================================
    # ROW 1 — MARKET PULSE
    # =====================================================

    def _market_pulse(self) -> DashboardCard:

        card = DashboardCard(
            "MARKET PULSE"
        )

        # -------------------------------------------------
        # Header status
        # -------------------------------------------------

        header = QHBoxLayout()

        self.market_pulse_status = QLabel(
            "BULLISH"
        )

        self.market_pulse_status.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 21px;
            font-weight: 900;
            """
        )

        score = QLabel(
            "78 / 100"
        )

        score.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 16px;
            font-weight: 800;
            """
        )

        header.addWidget(
            self.market_pulse_status
        )

        header.addStretch(1)

        header.addWidget(
            score
        )

        card.layout.addLayout(
            header
        )

        # -------------------------------------------------
        # Graphic section
        # -------------------------------------------------

        graphics = QHBoxLayout()

        graphics.setSpacing(
            12
        )

        self.market_animal = (
            MarketAnimalGraphic(
                bullish=True
            )
        )

        trend = PulseTrendGraph()

        graphics.addWidget(
            self.market_animal,
            2,
        )

        graphics.addWidget(
            trend,
            4,
        )

        card.layout.addLayout(
            graphics,
            1,
        )

        # -------------------------------------------------
        # Bottom statistics
        # -------------------------------------------------

        stats = QHBoxLayout()

        stats.setSpacing(
            8
        )

        for title, value, color in (
            (
                "Momentum",
                "Strong",
                GREEN,
            ),
            (
                "Trend",
                "Positive",
                GREEN,
            ),
            (
                "Volatility",
                "Low",
                BLUE,
            ),
            (
                "Breadth",
                "Healthy",
                GREEN,
            ),
        ):

            box = QFrame()

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            box_layout = QVBoxLayout(
                box
            )

            box_layout.setContentsMargins(
                8,
                5,
                8,
                5,
            )

            box_layout.setSpacing(
                1
            )

            title_label = make_label(
                title,
                10,
                MUTED,
                False,
            )

            value_label = make_label(
                value,
                14,
                color,
                True,
            )

            box_layout.addWidget(
                title_label
            )

            box_layout.addWidget(
                value_label
            )

            stats.addWidget(
                box
            )

        card.layout.addLayout(
            stats
        )

        return card


    # =====================================================
    # ROW 1 — SECTOR STRENGTH
    # =====================================================


    def _sector_strength(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "SECTOR STRENGTH"
        )

        header = QHBoxLayout()

        header.addWidget(
            make_label(
                "SECTOR",
                10,
                MUTED,
                True,
            )
        )

        header.addStretch(1)

        header.addWidget(
            make_label(
                "STRENGTH",
                10,
                MUTED,
                True,
            )
        )

        header.addSpacing(8)

        header.addWidget(
            make_label(
                "CHANGE",
                10,
                MUTED,
                True,
            )
        )

        card.layout.addLayout(
            header
        )

        self.live_sector_rows = []

        for _ in range(5):

            row = QWidget()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                0,
                4,
                0,
                4,
            )

            layout.setSpacing(7)

            sector_label = make_label(
                "--",
                12,
                TEXT,
                True,
            )

            sector_label.setFixedWidth(
                78
            )

            bar = StrengthBar(
                0,
                MUTED,
            )

            strength_label = make_label(
                "0",
                12,
                MUTED,
                True,
            )

            strength_label.setFixedWidth(
                28
            )

            change_label = make_label(
                "0.00%",
                12,
                MUTED,
                True,
            )

            change_label.setFixedWidth(
                58
            )

            change_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                sector_label
            )

            layout.addWidget(
                bar,
                1,
            )

            layout.addWidget(
                strength_label
            )

            layout.addWidget(
                change_label
            )

            card.layout.addWidget(
                row
            )

            self.live_sector_rows.append(
                {
                    "sector": sector_label,
                    "bar": bar,
                    "strength": strength_label,
                    "change": change_label,
                }
            )

        card.layout.addStretch(1)

        return card

    def _market_breadth(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "MARKET BREADTH"
        )

        self.breadth_gauge = BreadthGauge(
            0
        )

        card.layout.addWidget(
            self.breadth_gauge,
            1,
        )

        # -------------------------------------------------
        # IMPORTANT COMPATIBILITY OBJECTS
        # -------------------------------------------------

        self.advance_card = BreadthValue(
            "advance_card",
            "Advances",
            "1,247",
            GREEN,
        )

        self.decline_card = BreadthValue(
            "decline_card",
            "Declines",
            "684",
            RED,
        )

        self.unchanged_card = BreadthValue(
            "unchanged_card",
            "Unchanged",
            "91",
            MUTED,
        )

        card.layout.addWidget(
            self.advance_card
        )

        card.layout.addWidget(
            horizontal_line()
        )

        card.layout.addWidget(
            self.decline_card
        )

        card.layout.addWidget(
            horizontal_line()
        )

        card.layout.addWidget(
            self.unchanged_card
        )

        return card


    # =====================================================
    # ROW 1 — MARKET HEATMAP
    # =====================================================


    def _market_heatmap(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "MARKET HEATMAP"
        )

        card.layout.addStretch(1)

        grid = QGridLayout()

        grid.setHorizontalSpacing(5)
        grid.setVerticalSpacing(5)

        self.live_heatmap_tiles = []

        for i in range(9):

            tile = QLabel(
                "--\n0.00%"
            )

            tile.setAlignment(
                Qt.AlignCenter
            )

            tile.setMinimumHeight(
                48
            )

            tile.setStyleSheet(
                f"""
                QLabel {{
                    background: #0d2035;
                    border: 1px solid {BORDER};
                    border-radius: 5px;
                    color: {MUTED};
                    font-size: 11px;
                    font-weight: 800;
                }}
                """
            )

            grid.addWidget(
                tile,
                i // 3,
                i % 3,
            )

            self.live_heatmap_tiles.append(
                tile
            )

        card.layout.addLayout(
            grid
        )

        card.layout.addStretch(1)

        return card

    def _top_opportunities(self) -> DashboardCard:
        """
        Live scanner Top Opportunities card.

        Rows are created once and updated from the existing
        ApplicationController scannerCompleted signal.
        """

        card = DashboardCard(
            "TOP OPPORTUNITIES"
        )

        header = QHBoxLayout()

        for text, stretch in (
            ("STOCK", 3),
            ("SIGNAL", 2),
            ("SCORE", 1),
            ("PRICE", 2),
        ):

            label = make_label(
                text,
                10,
                MUTED,
                True,
            )

            if text in (
                "SCORE",
                "PRICE",
            ):
                label.setAlignment(
                    Qt.AlignRight
                    | Qt.AlignVCenter
                )

            header.addWidget(
                label,
                stretch,
            )

        card.layout.addLayout(
            header
        )

        self.live_opportunity_rows = []

        for _ in range(5):

            row = self._table_row_frame()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                10,
                5,
                10,
                5,
            )

            layout.setSpacing(8)

            symbol_label = self._table_cell(
                "--"
            )

            signal_label = self._table_cell(
                "--",
                MUTED,
            )

            score_label = self._table_cell(
                "--",
                BLUE,
            )

            price_label = self._table_cell(
                "--"
            )

            score_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            price_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                symbol_label,
                3,
            )

            layout.addWidget(
                signal_label,
                2,
            )

            layout.addWidget(
                score_label,
                1,
            )

            layout.addWidget(
                price_label,
                2,
            )

            card.layout.addWidget(
                row
            )

            self.live_opportunity_rows.append(
                {
                    "row": row,
                    "symbol": symbol_label,
                    "signal": signal_label,
                    "score": score_label,
                    "price": price_label,
                }
            )

        card.layout.addStretch(1)

        return card


    # =====================================================
    # ROW 2 — SCANNER SUMMARY
    # =====================================================

    def _scanner_summary(self) -> DashboardCard:
        """
        Live scanner summary.

        Uses the same opportunities delivered to the
        Intraday Scanner page.
        """

        card = DashboardCard(
            "SCANNER SUMMARY"
        )

        self.live_scanner_donut = DonutChart(
            total=0,
            buy=0,
            sell=0,
        )

        self.live_scanner_donut.setMinimumHeight(
            92
        )

        self.live_scanner_donut.setMaximumHeight(
            105
        )

        card.layout.addWidget(
            self.live_scanner_donut,
            0,
            Qt.AlignHCenter,
        )

        stats = QHBoxLayout()
        stats.setSpacing(6)

        self.live_scanner_summary_labels = {}

        for title, color in (
            ("BUY", GREEN),
            ("SELL", RED),
            ("AVG", BLUE),
        ):

            box = QFrame()

            box.setFixedHeight(
                45
            )

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            box_layout = QVBoxLayout(
                box
            )

            box_layout.setContentsMargins(
                5,
                2,
                5,
                2,
            )

            box_layout.setSpacing(0)

            title_label = make_label(
                title,
                8,
                MUTED,
                True,
            )

            value_label = make_label(
                "0",
                13,
                color,
                True,
            )

            title_label.setAlignment(
                Qt.AlignCenter
            )

            value_label.setAlignment(
                Qt.AlignCenter
            )

            box_layout.addWidget(
                title_label
            )

            box_layout.addWidget(
                value_label
            )

            stats.addWidget(
                box,
                1,
            )

            self.live_scanner_summary_labels[
                title
            ] = value_label

        card.layout.addLayout(
            stats
        )

        button = QPushButton(
            "OPEN SCANNER"
        )

        button.setFixedHeight(
            30
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setStyleSheet(
            f"""
            QPushButton {{
                background: {BLUE};
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 11px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                background: #4a89ff;
            }}
            """
        )

        button.clicked.connect(
            lambda:
            self.scanner_requested.emit(
                "scanner"
            )
        )

        card.layout.addWidget(
            button
        )

        return card


    def _top_movers(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "TOP MOVERS"
        )

        self.live_mover_rows = []

        for _ in range(6):

            row = self._table_row_frame()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                10,
                5,
                10,
                5,
            )

            symbol_label = self._table_cell(
                "--"
            )

            price_label = self._table_cell(
                "--"
            )

            change_label = self._table_cell(
                "0.00%",
                MUTED,
            )

            price_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            change_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                symbol_label,
                2,
            )

            layout.addWidget(
                price_label,
                1,
            )

            layout.addWidget(
                change_label,
                1,
            )

            card.layout.addWidget(
                row
            )

            self.live_mover_rows.append(
                {
                    "symbol": symbol_label,
                    "price": price_label,
                    "change": change_label,
                }
            )

        card.layout.addStretch(1)

        return card

    def _live_scanner_alerts(self) -> DashboardCard:
        """
        Latest real scanner alerts.
        """

        card = DashboardCard(
            "LIVE SCANNER ALERTS"
        )

        header = QHBoxLayout()

        header.addWidget(
            make_label(
                "SYMBOL",
                10,
                MUTED,
                True,
            )
        )

        header.addStretch(1)

        header.addWidget(
            make_label(
                "TRIGGER",
                10,
                MUTED,
                True,
            )
        )

        card.layout.addLayout(
            header
        )

        self.live_scanner_alert_rows = []

        for _ in range(5):

            row = self._table_row_frame()

            layout = QHBoxLayout(
                row
            )

            layout.setContentsMargins(
                10,
                5,
                10,
                5,
            )

            layout.setSpacing(8)

            symbol_label = self._table_cell(
                "--"
            )

            trigger_label = self._table_cell(
                "--",
                MUTED,
            )

            trigger_label.setAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.addWidget(
                symbol_label,
                1,
            )

            layout.addWidget(
                trigger_label,
                2,
            )

            card.layout.addWidget(
                row
            )

            self.live_scanner_alert_rows.append(
                {
                    "row": row,
                    "symbol": symbol_label,
                    "trigger": trigger_label,
                }
            )

        card.layout.addStretch(1)

        return card


    # =====================================================


    def update_scanner_results(
        self,
        opportunities,
    ) -> None:
        """
        Update dashboard scanner widgets from the existing
        scannerCompleted result list.

        No scanner execution happens here.
        """

        if opportunities is None:
            opportunities = []

        try:
            opportunities = list(
                opportunities
            )
        except TypeError:
            opportunities = []

        # --------------------------------------------------
        # Helpers
        # --------------------------------------------------

        def safe_float(
            value,
            default=0.0,
        ):

            try:
                return float(value)

            except (
                TypeError,
                ValueError,
            ):
                return default

        def get_signal(item):

            return str(
                item.get(
                    "signal",
                    "",
                )
            ).upper()

        # --------------------------------------------------
        # Sort best opportunities first
        # --------------------------------------------------

        ranked = sorted(
            opportunities,
            key=lambda item: safe_float(
                item.get(
                    "score",
                    item.get(
                        "confidence",
                        0,
                    ),
                )
            ),
            reverse=True,
        )

        # --------------------------------------------------
        # TOP OPPORTUNITIES
        # --------------------------------------------------

        for index, row_data in enumerate(
            self.live_opportunity_rows
        ):

            if index < len(ranked):

                item = ranked[index]

                symbol = str(
                    item.get(
                        "symbol",
                        "--",
                    )
                )

                signal = get_signal(
                    item
                ) or "--"

                score_value = safe_float(
                    item.get(
                        "score",
                        item.get(
                            "confidence",
                            0,
                        ),
                    )
                )

                entry_value = safe_float(
                    item.get(
                        "entry",
                        item.get(
                            "price",
                            item.get(
                                "ltp",
                                0,
                            ),
                        ),
                    )
                )

                row_data[
                    "symbol"
                ].setText(
                    symbol
                )

                row_data[
                    "signal"
                ].setText(
                    signal
                )

                row_data[
                    "score"
                ].setText(
                    f"{score_value:.0f}"
                )

                if entry_value:

                    row_data[
                        "price"
                    ].setText(
                        f"₹{entry_value:,.2f}"
                    )

                else:

                    row_data[
                        "price"
                    ].setText(
                        "--"
                    )

                if signal == "BUY":

                    signal_color = GREEN

                elif signal == "SELL":

                    signal_color = RED

                else:

                    signal_color = MUTED

                row_data[
                    "signal"
                ].setStyleSheet(
                    f"""
                    color: {signal_color};
                    background: transparent;
                    border: none;
                    """
                )

                row_data[
                    "row"
                ].show()

            else:

                row_data[
                    "symbol"
                ].setText("--")

                row_data[
                    "signal"
                ].setText("--")

                row_data[
                    "score"
                ].setText("--")

                row_data[
                    "price"
                ].setText("--")

        # --------------------------------------------------
        # SCANNER SUMMARY
        # --------------------------------------------------

        buy_count = sum(
            1
            for item in opportunities
            if get_signal(item) == "BUY"
        )

        sell_count = sum(
            1
            for item in opportunities
            if get_signal(item) == "SELL"
        )

        scores = [
            safe_float(
                item.get(
                    "score",
                    item.get(
                        "confidence",
                        0,
                    ),
                )
            )
            for item in opportunities
        ]

        avg_score = (
            sum(scores)
            / len(scores)
            if scores
            else 0
        )

        self.live_scanner_summary_labels[
            "BUY"
        ].setText(
            str(buy_count)
        )

        self.live_scanner_summary_labels[
            "SELL"
        ].setText(
            str(sell_count)
        )

        self.live_scanner_summary_labels[
            "AVG"
        ].setText(
            f"{avg_score:.0f}"
        )

        self.live_scanner_donut.total = len(
            opportunities
        )

        self.live_scanner_donut.buy = (
            buy_count
        )

        self.live_scanner_donut.sell = (
            sell_count
        )

        self.live_scanner_donut.update()

        # --------------------------------------------------
        # LIVE SCANNER ALERTS
        # --------------------------------------------------

        for index, row_data in enumerate(
            self.live_scanner_alert_rows
        ):

            if index < len(ranked):

                item = ranked[index]

                symbol = str(
                    item.get(
                        "symbol",
                        "--",
                    )
                )

                signal = get_signal(
                    item
                )

                pattern = item.get(
                    "pattern"
                )

                trigger = ""

                if isinstance(
                    pattern,
                    dict,
                ):

                    trigger = str(
                        pattern.get(
                            "pattern",
                            pattern.get(
                                "name",
                                "",
                            ),
                        )
                    )

                elif pattern:

                    trigger = str(
                        pattern
                    )

                if not trigger:

                    confidence = safe_float(
                        item.get(
                            "confidence",
                            0,
                        )
                    )

                    if confidence >= 90:

                        trigger = (
                            "High Confidence"
                        )

                    elif signal == "BUY":

                        trigger = (
                            "BUY Opportunity"
                        )

                    elif signal == "SELL":

                        trigger = (
                            "SELL Opportunity"
                        )

                    else:

                        trigger = (
                            "Scanner Match"
                        )

                if signal == "BUY":

                    trigger_color = GREEN

                elif signal == "SELL":

                    trigger_color = RED

                else:

                    trigger_color = BLUE

                row_data[
                    "symbol"
                ].setText(
                    symbol
                )

                row_data[
                    "trigger"
                ].setText(
                    trigger
                )

                row_data[
                    "trigger"
                ].setStyleSheet(
                    f"""
                    color: {trigger_color};
                    background: transparent;
                    border: none;
                    """
                )

            else:

                row_data[
                    "symbol"
                ].setText("--")

                row_data[
                    "trigger"
                ].setText("--")


    def update_live_market_cards(
        self,
        sectors=None,
        heatmap=None,
        gainers=None,
        losers=None,
        institutional=None,
    ) -> None:

        sectors = sectors or []
        heatmap = heatmap or []
        gainers = gainers or []
        losers = losers or []
        institutional = institutional or {}

        # -------------------------------------------------
        # Sector Strength
        # -------------------------------------------------

        sector_rows = getattr(
            self,
            "live_sector_rows",
            [],
        )

        for i, widgets in enumerate(
            sector_rows
        ):

            if i < len(sectors):

                data = sectors[i]

                name = str(
                    data.get(
                        "name",
                        data.get(
                            "industry",
                            "--",
                        ),
                    )
                )

                change = float(
                    data.get(
                        "change",
                        data.get(
                            "average_change_percent",
                            0.0,
                        ),
                    )
                    or 0.0
                )

                advance = int(
                    data.get(
                        "advance",
                        0,
                    )
                    or 0
                )

                decline = int(
                    data.get(
                        "decline",
                        0,
                    )
                    or 0
                )

                unchanged = int(
                    data.get(
                        "unchanged",
                        0,
                    )
                    or 0
                )

                total = (
                    advance
                    + decline
                    + unchanged
                )

                if total > 0:
                    strength = int(
                        round(
                            advance
                            / total
                            * 100.0
                        )
                    )
                else:
                    strength = 0

                strength = max(
                    0,
                    min(
                        100,
                        strength,
                    ),
                )

                color = (
                    GREEN
                    if change >= 0
                    else RED
                )

                widgets[
                    "sector"
                ].setText(
                    name[:12]
                )

                widgets[
                    "strength"
                ].setText(
                    str(strength)
                )

                widgets[
                    "change"
                ].setText(
                    f"{change:+.2f}%"
                )

                widgets[
                    "strength"
                ].setStyleSheet(
                    f"""
                    color: {color};
                    font-size: 12px;
                    font-weight: 700;
                    """
                )

                widgets[
                    "change"
                ].setStyleSheet(
                    f"""
                    color: {color};
                    font-size: 12px;
                    font-weight: 700;
                    """
                )

                bar = widgets["bar"]

                if hasattr(
                    bar,
                    "value",
                ):
                    bar.value = strength

                if hasattr(
                    bar,
                    "color",
                ):
                    bar.color = color

                bar.update()

            else:

                widgets[
                    "sector"
                ].setText("--")

                widgets[
                    "strength"
                ].setText("0")

                widgets[
                    "change"
                ].setText("0.00%")

        # -------------------------------------------------
        # Heatmap
        # -------------------------------------------------

        tiles = getattr(
            self,
            "live_heatmap_tiles",
            [],
        )

        for i, tile in enumerate(
            tiles
        ):

            if i < len(heatmap):

                data = heatmap[i]

                symbol = str(
                    data.get(
                        "symbol",
                        "--",
                    )
                )

                change = float(
                    data.get(
                        "change_percent",
                        data.get(
                            "change",
                            0.0,
                        ),
                    )
                    or 0.0
                )

                positive = (
                    change >= 0
                )

                bg = (
                    GREEN_DARK
                    if positive
                    else RED_DARK
                )

                border = (
                    GREEN
                    if positive
                    else RED
                )

                tile.setText(
                    f"{symbol}\n"
                    f"{change:+.2f}%"
                )

                tile.setStyleSheet(
                    f"""
                    QLabel {{
                        background: {bg};
                        border: 1px solid {border};
                        border-radius: 5px;
                        color: #ffffff;
                        font-size: 11px;
                        font-weight: 800;
                    }}
                    """
                )

            else:

                tile.setText(
                    "--\n0.00%"
                )

                tile.setStyleSheet(
                    f"""
                    QLabel {{
                        background: #0d2035;
                        border: 1px solid {BORDER};
                        border-radius: 5px;
                        color: {MUTED};
                        font-size: 11px;
                        font-weight: 800;
                    }}
                    """
                )

        # -------------------------------------------------
        # Top Movers
        # 3 gainers + 3 losers
        # -------------------------------------------------

        movers = (
            list(gainers[:3])
            + list(losers[:3])
        )

        mover_rows = getattr(
            self,
            "live_mover_rows",
            [],
        )

        for i, widgets in enumerate(
            mover_rows
        ):

            if i < len(movers):

                data = movers[i]

                symbol = str(
                    data.get(
                        "symbol",
                        "--",
                    )
                )

                price = float(
                    data.get(
                        "ltp",
                        data.get(
                            "last_price",
                            0.0,
                        ),
                    )
                    or 0.0
                )

                change = float(
                    data.get(
                        "change_percent",
                        0.0,
                    )
                    or 0.0
                )

                color = (
                    GREEN
                    if change >= 0
                    else RED
                )

                widgets[
                    "symbol"
                ].setText(
                    symbol
                )

                widgets[
                    "price"
                ].setText(
                    f"₹{price:,.2f}"
                )

                widgets[
                    "change"
                ].setText(
                    f"{change:+.2f}%"
                )

                widgets[
                    "change"
                ].setStyleSheet(
                    f"""
                    color: {color};
                    font-size: 12px;
                    font-weight: 700;
                    """
                )

            else:

                widgets[
                    "symbol"
                ].setText("--")

                widgets[
                    "price"
                ].setText("--")

                widgets[
                    "change"
                ].setText("0.00%")

        # -------------------------------------------------
        # Institutional Flow
        # -------------------------------------------------

        if isinstance(
            institutional,
            dict,
        ):

            fii = institutional.get(
                "fii",
                {},
            )

            dii = institutional.get(
                "dii",
                {},
            )

            if not isinstance(fii, dict):
                fii = {}

            if not isinstance(dii, dict):
                dii = {}

            def safe_number(value):

                try:
                    return float(value or 0.0)

                except (
                    TypeError,
                    ValueError,
                ):
                    return 0.0

            fii_buy = safe_number(
                fii.get("buy")
            )

            fii_sell = safe_number(
                fii.get("sell")
            )

            fii_net = safe_number(
                fii.get("net")
            )

            dii_buy = safe_number(
                dii.get("buy")
            )

            dii_sell = safe_number(
                dii.get("sell")
            )

            dii_net = safe_number(
                dii.get("net")
            )

            total_net = safe_number(
                institutional.get(
                    "net",
                    fii_net + dii_net,
                )
            )

            # ---------------------------------------------
            # Institutional session date
            # ---------------------------------------------

            raw_date = str(
                institutional.get(
                    "date",
                    "",
                )
                or ""
            ).strip()

            display_date = "--"

            if raw_date:

                parsed = None

                for fmt in (
                    "%Y-%m-%d",
                    "%d-%m-%Y",
                    "%d/%m/%Y",
                    "%d-%b-%Y",
                    "%d %b %Y",
                ):

                    try:

                        parsed = datetime.strptime(
                            raw_date,
                            fmt,
                        )

                        break

                    except ValueError:
                        pass

                if parsed is not None:

                    display_date = parsed.strftime(
                        "%d %b %Y"
                    )

                else:
                    display_date = raw_date

            if hasattr(
                self,
                "institutional_date_label",
            ):

                self.institutional_date_label.setText(
                    display_date
                )

            # ---------------------------------------------
            # Formatting
            # ---------------------------------------------

            def money(value):

                sign = (
                    "+"
                    if value > 0
                    else ""
                )

                return (
                    f"{sign}₹{value:,.0f} Cr"
                )

            def flow_color(value):

                if value > 0:
                    return GREEN

                if value < 0:
                    return RED

                return MUTED

            if hasattr(
                self,
                "fii_buy_label",
            ):

                self.fii_buy_label.setText(
                    f"BUY ₹{fii_buy:,.0f} Cr"
                )

            if hasattr(
                self,
                "fii_sell_label",
            ):

                self.fii_sell_label.setText(
                    f"SELL ₹{fii_sell:,.0f} Cr"
                )

            if hasattr(
                self,
                "fii_net_label",
            ):

                self.fii_net_label.setText(
                    money(fii_net)
                )

                self.fii_net_label.setStyleSheet(
                    f"""
                    color: {flow_color(fii_net)};
                    font-size: 14px;
                    font-weight: 800;
                    """
                )

            if hasattr(
                self,
                "dii_buy_label",
            ):

                self.dii_buy_label.setText(
                    f"BUY ₹{dii_buy:,.0f} Cr"
                )

            if hasattr(
                self,
                "dii_sell_label",
            ):

                self.dii_sell_label.setText(
                    f"SELL ₹{dii_sell:,.0f} Cr"
                )

            if hasattr(
                self,
                "dii_net_label",
            ):

                self.dii_net_label.setText(
                    money(dii_net)
                )

                self.dii_net_label.setStyleSheet(
                    f"""
                    color: {flow_color(dii_net)};
                    font-size: 14px;
                    font-weight: 800;
                    """
                )

            if hasattr(
                self,
                "institutional_net_label",
            ):

                self.institutional_net_label.setText(
                    money(total_net)
                )

                self.institutional_net_label.setStyleSheet(
                    f"""
                    color: {flow_color(total_net)};
                    font-size: 15px;
                    font-weight: 900;
                    """
                )


    def _institutional_flow(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "INSTITUTIONAL FLOW"
        )

        # -------------------------------------------------
        # Session date
        # -------------------------------------------------

        self.institutional_date_label = make_label(
            "--",
            11,
            MUTED,
            True,
        )

        self.institutional_date_label.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        card.layout.addWidget(
            self.institutional_date_label
        )

        # -------------------------------------------------
        # FII
        # -------------------------------------------------

        fii_header = QHBoxLayout()

        fii_header.addWidget(
            make_label(
                "FII",
                13,
                TEXT,
                True,
            )
        )

        fii_header.addStretch(1)

        self.fii_net_label = make_label(
            "--",
            14,
            MUTED,
            True,
        )

        fii_header.addWidget(
            self.fii_net_label
        )

        card.layout.addLayout(
            fii_header
        )

        fii_values = QHBoxLayout()

        self.fii_buy_label = make_label(
            "BUY --",
            11,
            MUTED,
            True,
        )

        self.fii_sell_label = make_label(
            "SELL --",
            11,
            MUTED,
            True,
        )

        fii_values.addWidget(
            self.fii_buy_label
        )

        fii_values.addStretch(1)

        fii_values.addWidget(
            self.fii_sell_label
        )

        card.layout.addLayout(
            fii_values
        )

        # -------------------------------------------------
        # DII
        # -------------------------------------------------

        dii_header = QHBoxLayout()

        dii_header.addWidget(
            make_label(
                "DII",
                13,
                TEXT,
                True,
            )
        )

        dii_header.addStretch(1)

        self.dii_net_label = make_label(
            "--",
            14,
            MUTED,
            True,
        )

        dii_header.addWidget(
            self.dii_net_label
        )

        card.layout.addLayout(
            dii_header
        )

        dii_values = QHBoxLayout()

        self.dii_buy_label = make_label(
            "BUY --",
            11,
            MUTED,
            True,
        )

        self.dii_sell_label = make_label(
            "SELL --",
            11,
            MUTED,
            True,
        )

        dii_values.addWidget(
            self.dii_buy_label
        )

        dii_values.addStretch(1)

        dii_values.addWidget(
            self.dii_sell_label
        )

        card.layout.addLayout(
            dii_values
        )

        # -------------------------------------------------
        # Net institutional flow
        # -------------------------------------------------

        card.layout.addStretch(1)

        net_row = QHBoxLayout()

        net_row.addWidget(
            make_label(
                "NET INSTITUTIONAL FLOW",
                11,
                MUTED,
                True,
            )
        )

        net_row.addStretch(1)

        self.institutional_net_label = make_label(
            "--",
            15,
            MUTED,
            True,
        )

        net_row.addWidget(
            self.institutional_net_label
        )

        card.layout.addLayout(
            net_row
        )

        return card

    def _derivatives_pulse(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "DERIVATIVES PULSE"
        )

        gauge = DerivativesGauge(
            value=0.72,
            bullish=True,
        )

        gauge.setMinimumHeight(82)
        gauge.setMaximumHeight(92)

        card.layout.addWidget(
            gauge,
            0,
        )

        status = QLabel(
            "BULLISH"
        )

        status.setFixedHeight(22)

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet(
            f"""
            QLabel {{
                color: {GREEN};
                background: transparent;
                border: none;
                font-size: 15px;
                font-weight: 900;
            }}
            """
        )

        card.layout.addWidget(
            status
        )

        stats = QGridLayout()

        stats.setHorizontalSpacing(8)
        stats.setVerticalSpacing(4)

        labels = [
            ("PCR", "1.18", GREEN),
            ("MAX PAIN", "25,500", BLUE),
            ("FUT OI", "+4.2%", GREEN),
            ("VIX", "12.42", GREEN),
        ]

        for i, (
            title,
            value,
            color,
        ) in enumerate(labels):

            box = QFrame()

            box.setFixedHeight(34)

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            layout = QVBoxLayout(
                box
            )

            layout.setContentsMargins(
                4,
                1,
                4,
                1,
            )

            layout.setSpacing(0)

            title_label = make_label(
                title,
                7,
                MUTED,
                True,
            )

            value_label = make_label(
                value,
                10,
                color,
                True,
            )

            title_label.setAlignment(
                Qt.AlignCenter
            )

            value_label.setAlignment(
                Qt.AlignCenter
            )

            layout.addWidget(
                title_label
            )

            layout.addWidget(
                value_label
            )

            stats.addWidget(
                box,
                i // 2,
                i % 2,
            )

        card.layout.addLayout(
            stats
        )

        return card

    def _nifty_oi_chart(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "NIFTY OI CHART"
        )

        # -------------------------------------------------
        # Chart header / legend
        # -------------------------------------------------

        legend = QHBoxLayout()

        legend.setSpacing(
            12
        )

        legend.addWidget(
            make_label(
                "25,488.90",
                17,
                TEXT,
                True,
            )
        )

        legend.addWidget(
            make_label(
                "+0.97%",
                12,
                GREEN,
                True,
            )
        )

        legend.addStretch(
            1
        )

        call_legend = QLabel(
            "■ CALL OI"
        )

        call_legend.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 9px;
            font-weight: 800;
            """
        )

        put_legend = QLabel(
            "■ PUT OI"
        )

        put_legend.setStyleSheet(
            f"""
            color: {RED};
            font-size: 9px;
            font-weight: 800;
            """
        )

        price_legend = QLabel(
            "━ PRICE"
        )

        price_legend.setStyleSheet(
            f"""
            color: {BLUE};
            font-size: 9px;
            font-weight: 800;
            """
        )

        legend.addWidget(
            call_legend
        )

        legend.addWidget(
            put_legend
        )

        legend.addWidget(
            price_legend
        )

        card.layout.addLayout(
            legend
        )

        chart = NiftyOIChart()

        card.layout.addWidget(
            chart,
            1,
        )

        # -------------------------------------------------
        # Bottom OI information
        # -------------------------------------------------

        bottom = QHBoxLayout()

        bottom.setSpacing(
            8
        )

        for title, value, color in (
            (
                "CALL WALL",
                "25,600",
                RED,
            ),
            (
                "MAX PAIN",
                "25,500",
                BLUE,
            ),
            (
                "PUT WALL",
                "25,300",
                GREEN,
            ),
        ):

            box = QFrame()

            box.setStyleSheet(
                f"""
                QFrame {{
                    background: {ROW_BG};
                    border: 1px solid {BORDER_SOFT};
                    border-radius: 5px;
                }}
                """
            )

            box_layout = QVBoxLayout(
                box
            )

            box.setFixedHeight(38)

            box_layout.setContentsMargins(
                5,
                2,
                5,
                2,
            )

            box_layout.setSpacing(
                0
            )

            title_label = make_label(
                title,
                8,
                MUTED,
                True,
            )

            title_label.setAlignment(
                Qt.AlignCenter
            )

            value_label = make_label(
                value,
                11,
                color,
                True,
            )

            value_label.setAlignment(
                Qt.AlignCenter
            )

            box_layout.addWidget(
                title_label
            )

            box_layout.addWidget(
                value_label
            )

            bottom.addWidget(
                box
            )

        card.layout.addLayout(
            bottom
        )

        return card


    # =====================================================
    # MARKET PULSE UPDATE
    # =====================================================

    def set_market_pulse(
        self,
        bullish: bool,
        score: Optional[int] = None,
    ) -> None:

        if self.market_pulse_status is not None:

            if bullish:

                self.market_pulse_status.setText(
                    "BULLISH"
                )

                self.market_pulse_status.setStyleSheet(
                    f"""
                    color: {GREEN};
                    font-size: 21px;
                    font-weight: 900;
                    """
                )

            else:

                self.market_pulse_status.setText(
                    "BEARISH"
                )

                self.market_pulse_status.setStyleSheet(
                    f"""
                    color: {RED};
                    font-size: 21px;
                    font-weight: 900;
                    """
                )

        if self.market_animal is not None:

            self.market_animal.set_bullish(
                bullish
            )


    # =====================================================
    # NOTIFICATION
    #
    # Required by MarketController.notify_dashboard()
    # =====================================================

    def show_notification(
        self,
        message: str,
    ) -> None:

        if not message:
            return

        # -------------------------------------------------
        # Lightweight notification.
        #
        # We deliberately do not use QMessageBox because
        # live scanner messages must not block the UI.
        # -------------------------------------------------

        if not hasattr(
            self,
            "_notification_label",
        ):

            self._notification_label = QLabel(
                self
            )

            self._notification_label.setAlignment(
                Qt.AlignCenter
            )

            self._notification_label.setStyleSheet(
                f"""
                QLabel {{
                    background: #102642;
                    border: 1px solid #285c96;
                    border-radius: 6px;
                    color: #d9eaff;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 7px 14px;
                }}
                """
            )

        self._notification_label.setText(
            str(message)
        )

        self._notification_label.adjustSize()

        x = max(
            10,
            (
                self.width()
                - self._notification_label.width()
            )
            // 2,
        )

        self._notification_label.move(
            x,
            8,
        )

        self._notification_label.raise_()

        self._notification_label.show()


    # =====================================================
    # OPTIONAL REFRESH
    # =====================================================

    def request_refresh(
        self,
    ) -> None:

        self.refresh_requested.emit()


    # =====================================================
    # RESIZE
    # =====================================================

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "_notification_label",
        ):

            label = (
                self._notification_label
            )

            if label.isVisible():

                x = max(
                    10,
                    (
                        self.width()
                        - label.width()
                    )
                    // 2,
                )

                label.move(
                    x,
                    8,
                )
