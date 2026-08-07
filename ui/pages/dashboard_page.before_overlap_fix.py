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
            150,
            150,
        )

        self.setMaximumHeight(
            175
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
            145
        )

        self.setMaximumHeight(
            175
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
            self.width() - 28,
            220,
        )

        rect = QRectF(
            (self.width() - width) / 2,
            22,
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
                22,
                QFont.Bold,
            )
        )

        text_rect = QRectF(
            rect.x(),
            rect.y() + 35,
            rect.width(),
            80,
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
        self.setMinimumSize(190, 132)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
            175
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
            self.width() - 20,
            180,
        )

        rect = QRectF(
            (self.width() - size) / 2,
            25,
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
            210
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
            35,
            18,
            -18,
            -28,
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

        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(0)

        # -------------------------------------------------
        # IMPORTANT:
        #
        # No QScrollArea here.
        #
        # This prevents the unwanted horizontal scrollbar
        # that appeared in the previous build.
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

        self.grid = QGridLayout(
            content
        )

        self.grid.setContentsMargins(
            12,
            10,
            12,
            10,
        )

        self.grid.setHorizontalSpacing(
            10
        )

        self.grid.setVerticalSpacing(
            10
        )

        # =================================================
        # ROW 1
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

        self.grid.addWidget(
            self.market_pulse_card,
            0,
            0,
            1,
            2,
        )

        self.grid.addWidget(
            self.sector_strength_card,
            0,
            2,
        )

        self.grid.addWidget(
            self.market_breadth_card,
            0,
            3,
        )

        self.grid.addWidget(
            self.market_heatmap_card,
            0,
            4,
        )

        # =================================================
        # ROW 2
        # =================================================

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

        self.grid.addWidget(
            self.top_opportunities_card,
            1,
            0,
            1,
            2,
        )

        self.grid.addWidget(
            self.scanner_summary_card,
            1,
            2,
        )

        self.grid.addWidget(
            self.top_movers_card,
            1,
            3,
        )

        self.grid.addWidget(
            self.live_alerts_card,
            1,
            4,
        )

        # =================================================
        # ROW 3
        # =================================================

        self.institutional_flow_card = (
            self._institutional_flow()
        )

        self.derivatives_card = (
            self._derivatives_pulse()
        )

        self.nifty_oi_card = (
            self._nifty_oi_chart()
        )

        self.grid.addWidget(
            self.institutional_flow_card,
            2,
            0,
            1,
            2,
        )

        self.grid.addWidget(
            self.derivatives_card,
            2,
            2,
        )

        self.grid.addWidget(
            self.nifty_oi_card,
            2,
            3,
            1,
            2,
        )

        # -------------------------------------------------
        # COLUMN PROPORTIONS
        #
        # 5 logical columns:
        #
        # 0 + 1 = wide card
        # 2     = medium
        # 3     = medium
        # 4     = medium
        # -------------------------------------------------

        self.grid.setColumnStretch(
            0,
            1,
        )

        self.grid.setColumnStretch(
            1,
            1,
        )

        self.grid.setColumnStretch(
            2,
            1,
        )

        self.grid.setColumnStretch(
            3,
            1,
        )

        self.grid.setColumnStretch(
            4,
            1,
        )

        # -------------------------------------------------
        # ROW PROPORTIONS
        # -------------------------------------------------

        self.grid.setRowStretch(
            0,
            10,
        )

        self.grid.setRowStretch(
            1,
            10,
        )

        self.grid.setRowStretch(
            2,
            9,
        )

        root.addWidget(
            content
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

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

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

        header.addSpacing(
            8
        )

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
                GREEN,
            ),
            (
                "METAL",
                35,
                "-0.6%",
                RED,
            ),
        ]

        for (
            sector,
            strength,
            change,
            color,
        ) in sectors:

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

            layout.setSpacing(
                7
            )

            sector_label = make_label(
                sector,
                12,
                TEXT,
                True,
            )

            sector_label.setFixedWidth(
                58
            )

            bar = StrengthBar(
                strength,
                color,
            )

            strength_label = make_label(
                str(strength),
                12,
                color,
                True,
            )

            strength_label.setFixedWidth(
                26
            )

            change_label = make_label(
                change,
                12,
                color,
                True,
            )

            change_label.setFixedWidth(
                48
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

        card.layout.addStretch(
            1
        )

        return card


    # =====================================================
    # ROW 1 — MARKET BREADTH
    # =====================================================

    def _market_breadth(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "MARKET BREADTH"
        )

        gauge = BreadthGauge(
            64
        )

        card.layout.addWidget(
            gauge,
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

        card.layout.addStretch(
            1
        )

        grid = QGridLayout()

        grid.setHorizontalSpacing(
            5
        )

        grid.setVerticalSpacing(
            5
        )

        items = [
            (
                "RELIANCE\n+1.62%",
                GREEN_DARK,
            ),
            (
                "HDFC\n+0.90%",
                GREEN_DARK,
            ),
            (
                "TCS\n+1.20%",
                GREEN_DARK,
            ),
            (
                "INFY\n-0.70%",
                RED_DARK,
            ),
            (
                "ICICI\n+1.10%",
                GREEN_DARK,
            ),
            (
                "SBIN\n+1.40%",
                GREEN_DARK,
            ),
            (
                "ITC\n-0.50%",
                RED_DARK,
            ),
            (
                "LT\n+0.80%",
                GREEN_DARK,
            ),
            (
                "AXIS\n+1.00%",
                GREEN_DARK,
            ),
        ]

        for i, (
            text,
            color,
        ) in enumerate(items):

            tile = QLabel(text)

            tile.setAlignment(
                Qt.AlignCenter
            )

            tile.setMinimumHeight(
                48
            )

            tile.setStyleSheet(
                f"""
                QLabel {{
                    background: {color};
                    border: 1px solid {
                        GREEN
                        if color == GREEN_DARK
                        else RED
                    };
                    border-radius: 5px;
                    color: #ffffff;
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

        card.layout.addLayout(
            grid
        )

        card.layout.addStretch(
            1
        )

        return card
        # =====================================================
    # ROW 3 — INSTITUTIONAL FLOW
    # =====================================================
    # ROW 2 — TOP OPPORTUNITIES
    # =====================================================

    def _top_opportunities(self) -> DashboardCard:
        card = DashboardCard("TOP OPPORTUNITIES")

        header = QHBoxLayout()
        for text, stretch in (("STOCK", 3), ("SIGNAL", 2), ("SCORE", 1), ("PRICE", 2)):
            label = make_label(text, 10, MUTED, True)
            if text in ("SCORE", "PRICE"):
                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            header.addWidget(label, stretch)
        card.layout.addLayout(header)

        rows = [
            ("RELIANCE", "BUY", "92", "₹2,984.40"),
            ("HDFCBANK", "BUY", "88", "₹1,742.10"),
            ("TCS", "BUY", "86", "₹4,186.25"),
            ("INFY", "SELL", "82", "₹1,928.70"),
            ("ICICIBANK", "BUY", "79", "₹1,326.50"),
        ]

        for symbol, signal, score, price in rows:
            row = self._table_row_frame()
            layout = QHBoxLayout(row)
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(8)

            symbol_label = self._table_cell(symbol)
            signal_label = self._table_cell(signal, GREEN if signal == "BUY" else RED)
            score_label = self._table_cell(score, BLUE)
            price_label = self._table_cell(price)
            score_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            layout.addWidget(symbol_label, 3)
            layout.addWidget(signal_label, 2)
            layout.addWidget(score_label, 1)
            layout.addWidget(price_label, 2)
            card.layout.addWidget(row)

        return card


    # =====================================================
    # ROW 2 — SCANNER SUMMARY
    # =====================================================

    def _scanner_summary(self) -> DashboardCard:
        card = DashboardCard("SCANNER SUMMARY")
        donut = DonutChart(total=127, buy=74, sell=53)
        card.layout.addWidget(donut, 1)

        stats = QHBoxLayout()
        stats.setSpacing(6)
        for title, value, color in (("BUY", "74", GREEN), ("SELL", "53", RED), ("AVG", "81", BLUE)):
            box = QFrame()
            box.setStyleSheet(f"QFrame {{ background:{ROW_BG}; border:1px solid {BORDER_SOFT}; border-radius:5px; }}")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(5, 4, 5, 4)
            box_layout.setSpacing(0)
            t = make_label(title, 9, MUTED, True)
            v = make_label(value, 14, color, True)
            t.setAlignment(Qt.AlignCenter)
            v.setAlignment(Qt.AlignCenter)
            box_layout.addWidget(t)
            box_layout.addWidget(v)
            stats.addWidget(box)
        card.layout.addLayout(stats)

        button = QPushButton("OPEN SCANNER")
        button.setFixedHeight(30)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"QPushButton {{ background:{BLUE}; border:none; border-radius:5px; color:white; font-size:11px; font-weight:800; }} QPushButton:hover {{ background:#4a89ff; }}")
        button.clicked.connect(lambda: self.scanner_requested.emit("scanner"))
        card.layout.addWidget(button)
        return card


    # =====================================================
    # ROW 2 — TOP MOVERS
    # =====================================================

    def _top_movers(self) -> DashboardCard:
        card = DashboardCard("TOP MOVERS")
        for symbol, change, color in (
            ("TRENT", "+5.42%", GREEN),
            ("BEL", "+4.18%", GREEN),
            ("HAL", "+3.91%", GREEN),
            ("BAJFINANCE", "-2.64%", RED),
            ("TATASTEEL", "-2.12%", RED),
        ):
            row = self._table_row_frame()
            layout = QHBoxLayout(row)
            layout.setContentsMargins(10, 5, 10, 5)
            layout.addWidget(self._table_cell(symbol), 1)
            change_label = self._table_cell(change, color)
            change_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(change_label)
            card.layout.addWidget(row)
        card.layout.addStretch(1)
        return card


    # =====================================================
    # ROW 2 — LIVE SCANNER ALERTS
    # =====================================================

    def _live_scanner_alerts(self) -> DashboardCard:
        card = DashboardCard("LIVE SCANNER ALERTS")

        header = QHBoxLayout()
        header.addWidget(make_label("SYMBOL", 10, MUTED, True))
        header.addStretch(1)
        header.addWidget(make_label("TRIGGER", 10, MUTED, True))
        card.layout.addLayout(header)

        alerts = (
            ("RELIANCE", "VWAP Breakout", GREEN),
            ("HDFCBANK", "Volume Expansion", GREEN),
            ("INFY", "Weak Momentum", RED),
            ("TCS", "High Confidence", BLUE),
            ("SBIN", "Trend Continuation", GREEN),
        )
        for symbol, trigger, color in alerts:
            row = self._table_row_frame()
            layout = QHBoxLayout(row)
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(8)
            layout.addWidget(self._table_cell(symbol), 1)
            trigger_label = self._table_cell(trigger, color)
            trigger_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(trigger_label, 2)
            card.layout.addWidget(row)
        card.layout.addStretch(1)
        return card


    # =====================================================

    def _institutional_flow(
        self,
    ) -> DashboardCard:

        card = DashboardCard(
            "INSTITUTIONAL FLOW"
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

        fii_header.addWidget(
            make_label(
                "+₹1,842 Cr",
                14,
                GREEN,
                True,
            )
        )

        card.layout.addLayout(
            fii_header
        )

        fii_bar = StrengthBar(
            78,
            GREEN,
        )

        fii_bar.setFixedHeight(
            15
        )

        card.layout.addWidget(
            fii_bar
        )

        fii_detail = QHBoxLayout()

        fii_detail.addWidget(
            make_label(
                "BUY ₹8,426 Cr",
                10,
                GREEN,
                True,
            )
        )

        fii_detail.addStretch(1)

        fii_detail.addWidget(
            make_label(
                "SELL ₹6,584 Cr",
                10,
                RED,
                True,
            )
        )

        card.layout.addLayout(
            fii_detail
        )

        card.layout.addWidget(
            horizontal_line()
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

        dii_header.addWidget(
            make_label(
                "+₹684 Cr",
                14,
                GREEN,
                True,
            )
        )

        card.layout.addLayout(
            dii_header
        )

        dii_bar = StrengthBar(
            61,
            BLUE,
        )

        dii_bar.setFixedHeight(
            15
        )

        card.layout.addWidget(
            dii_bar
        )

        dii_detail = QHBoxLayout()

        dii_detail.addWidget(
            make_label(
                "BUY ₹5,918 Cr",
                10,
                GREEN,
                True,
            )
        )

        dii_detail.addStretch(1)

        dii_detail.addWidget(
            make_label(
                "SELL ₹5,234 Cr",
                10,
                RED,
                True,
            )
        )

        card.layout.addLayout(
            dii_detail
        )

        card.layout.addStretch(
            1
        )

        # -------------------------------------------------
        # NET FLOW
        # -------------------------------------------------

        net_box = QFrame()

        net_box.setStyleSheet(
            f"""
            QFrame {{
                background: #0c2b22;
                border: 1px solid #17553d;
                border-radius: 6px;
            }}
            """
        )

        net_layout = QHBoxLayout(
            net_box
        )

        net_layout.setContentsMargins(
            10,
            7,
            10,
            7,
        )

        net_layout.addWidget(
            make_label(
                "NET INSTITUTIONAL FLOW",
                10,
                MUTED,
                True,
            )
        )

        net_layout.addStretch(1)

        net_layout.addWidget(
            make_label(
                "+₹2,526 Cr",
                15,
                GREEN,
                True,
            )
        )

        card.layout.addWidget(
            net_box
        )

        return card


    # =====================================================
    # ROW 3 — DERIVATIVES PULSE
    # =====================================================

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

        card.layout.addWidget(
            gauge,
            1,
        )

        status = QLabel(
            "BULLISH"
        )

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet(
            f"""
            QLabel {{
                color: {GREEN};
                background: transparent;
                border: none;
                font-size: 17px;
                font-weight: 900;
            }}
            """
        )

        card.layout.addWidget(
            status
        )

        # -------------------------------------------------
        # Derivative statistics
        # -------------------------------------------------

        stats = QGridLayout()

        stats.setHorizontalSpacing(
            10
        )

        stats.setVerticalSpacing(
            5
        )

        labels = [
            (
                "PCR",
                "1.18",
                GREEN,
            ),
            (
                "MAX PAIN",
                "25,500",
                BLUE,
            ),
            (
                "FUT OI",
                "+4.2%",
                GREEN,
            ),
            (
                "VIX",
                "12.42",
                GREEN,
            ),
        ]

        for i, (
            title,
            value,
            color,
        ) in enumerate(labels):

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

            layout = QVBoxLayout(
                box
            )

            layout.setContentsMargins(
                6,
                4,
                6,
                4,
            )

            layout.setSpacing(
                0
            )

            title_label = make_label(
                title,
                9,
                MUTED,
                True,
            )

            title_label.setAlignment(
                Qt.AlignCenter
            )

            value_label = make_label(
                value,
                12,
                color,
                True,
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


    # =====================================================
    # ROW 3 — NIFTY OI CHART
    # =====================================================

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

            box_layout.setContentsMargins(
                7,
                4,
                7,
                4,
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
