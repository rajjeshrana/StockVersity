"""
StockVersity Pro
Premium Market Command Center

File:
    ui/pages/dashboard_page.py

Purpose:
    Main StockVersity dashboard.

The dashboard provides:
    - Market index overview
    - Trading opportunities
    - Market intelligence
    - Sector strength
    - Breadth analysis
    - Market heatmap
    - Intraday / Swing / Positional scanner summary
    - Top gainers / losers
    - Watchlist intelligence
    - Live scanner alerts
    - Market pulse
    - Intraday momentum
    - Trading setup intelligence
    - Risk / reward visualization
    - FII / DII flow
    - Derivatives intelligence
    - Market regime analysis

NOTE:
    Market values in this UI version are demonstration values.
    They will be replaced by live StockVersity service data
    during the integration phase.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PySide6.QtCore import (
    QDateTime,
    QPointF,
    QRectF,
    QTime,
    Qt,
    QTimer,
    Signal,
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
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# THEME
# ==========================================================

BACKGROUND = "#06101D"

CARD_BACKGROUND = "#0A1526"

CARD_BACKGROUND_HOVER = "#0E1B30"

CARD_BORDER = "#1B2A42"

CARD_BORDER_LIGHT = "#223550"

TEXT_PRIMARY = "#F1F5F9"

TEXT_SECONDARY = "#A9B8CC"

TEXT_MUTED = "#65758B"

BLUE = "#4C8DFF"

CYAN = "#35D0FF"

GREEN = "#24E57A"

RED = "#FF4D5E"

ORANGE = "#FFAA33"

PURPLE = "#9B7BFF"

FONT_FAMILY = "Segoe UI"


# ==========================================================
# HELPERS
# ==========================================================

def clear_layout(
    layout: QVBoxLayout | QHBoxLayout | QGridLayout,
) -> None:
    """
    Delete all widgets contained inside a layout.
    """

    while layout.count():

        item = layout.takeAt(0)

        widget = item.widget()

        child_layout = item.layout()

        if widget is not None:

            widget.deleteLater()

        elif child_layout is not None:

            clear_layout(child_layout)


def percentage_text(
    value: float,
) -> str:

    sign = "+" if value > 0 else ""

    return f"{sign}{value:.2f}%"


def movement_color(
    value: float,
) -> str:

    if value > 0:
        return GREEN

    if value < 0:
        return RED

    return TEXT_MUTED


# ==========================================================
# DASHBOARD CARD
# ==========================================================

class DashboardCard(QFrame):
    """
    Base premium dashboard card.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "DashboardCard"
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        self.setStyleSheet(
            f"""
            QFrame#DashboardCard {{
                background-color: {CARD_BACKGROUND};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
            """
        )


# ==========================================================
# SECTION HEADER
# ==========================================================

class SectionHeader(QWidget):

    action_clicked = Signal()

    def __init__(
        self,
        title: str,
        action_text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(8)

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 11px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            title_label
        )

        layout.addStretch(1)

        if action_text:

            button = QPushButton(
                action_text
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.setStyleSheet(
                f"""
                QPushButton {{
                    color: {CYAN};
                    background: transparent;
                    border: none;
                    font-size: 8px;
                    font-weight: 700;
                    padding: 2px 4px;
                }}

                QPushButton:hover {{
                    color: {TEXT_PRIMARY};
                }}
                """
            )

            button.clicked.connect(
                self.action_clicked.emit
            )

            layout.addWidget(
                button
            )


# ==========================================================
# SIGNAL BADGE
# ==========================================================

class SignalBadge(QLabel):

    def __init__(
        self,
        signal: str = "WATCH",
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setMinimumWidth(
            58
        )

        self.setFixedHeight(
            24
        )

        self.set_signal(
            signal
        )

    def set_signal(
        self,
        signal: str,
    ) -> None:

        signal = (
            signal
            .strip()
            .upper()
        )

        self.setText(
            signal
        )

        if signal in (
            "BUY",
            "STRONG BUY",
        ):

            color = GREEN

            background = (
                "rgba(36,229,122,0.09)"
            )

        elif signal in (
            "SELL",
            "STRONG SELL",
        ):

            color = RED

            background = (
                "rgba(255,77,94,0.09)"
            )

        else:

            color = ORANGE

            background = (
                "rgba(255,170,51,0.09)"
            )

        self.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: {background};
                border: 1px solid {color};
                border-radius: 5px;
                padding: 2px 6px;
                font-size: 7px;
                font-weight: 900;
            }}
            """
        )


# ==========================================================
# PATTERN BADGE
# ==========================================================

class PatternBadge(QLabel):

    def __init__(
        self,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(text, parent)

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setStyleSheet(
            f"""
            QLabel {{
                color: {PURPLE};
                background:
                    rgba(155,123,255,0.09);
                border:
                    1px solid rgba(155,123,255,0.22);
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 7px;
                font-weight: 800;
            }}
            """
        )


# ==========================================================
# SPARKLINE
# ==========================================================

class SparklineWidget(QWidget):
    """
    Lightweight custom-painted sparkline.

    No external chart library is required.
    """

    def __init__(
        self,
        values: Optional[List[float]] = None,
        positive: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._values = (
            list(values)
            if values
            else []
        )

        self._positive = positive

        self.setMinimumSize(
            60,
            30,
        )

    def set_values(
        self,
        values: List[float],
    ) -> None:

        self._values = list(values)

        if len(values) >= 2:

            self._positive = (
                values[-1]
                >= values[0]
            )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        if len(self._values) < 2:
            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = self.rect().adjusted(
            3,
            4,
            -3,
            -4,
        )

        minimum = min(
            self._values
        )

        maximum = max(
            self._values
        )

        spread = maximum - minimum

        if spread == 0:
            spread = 1.0

        step = (
            rect.width()
            / (
                len(self._values) - 1
            )
        )

        points: List[QPointF] = []

        for index, value in enumerate(
            self._values
        ):

            normalized = (
                value - minimum
            ) / spread

            x = (
                rect.left()
                + index * step
            )

            y = (
                rect.bottom()
                - normalized
                * rect.height()
            )

            points.append(
                QPointF(x, y)
            )

        color = QColor(
            GREEN
            if self._positive
            else RED
        )

        # Area gradient

        area = QPainterPath()

        area.moveTo(
            points[0]
        )

        for point in points[1:]:

            area.lineTo(
                point
            )

        area.lineTo(
            QPointF(
                points[-1].x(),
                rect.bottom(),
            )
        )

        area.lineTo(
            QPointF(
                points[0].x(),
                rect.bottom(),
            )
        )

        area.closeSubpath()

        gradient = QLinearGradient(
            0,
            rect.top(),
            0,
            rect.bottom(),
        )

        top_color = QColor(color)

        top_color.setAlpha(55)

        bottom_color = QColor(color)

        bottom_color.setAlpha(0)

        gradient.setColorAt(
            0,
            top_color,
        )

        gradient.setColorAt(
            1,
            bottom_color,
        )

        painter.fillPath(
            area,
            gradient,
        )

        # Main line

        path = QPainterPath()

        path.moveTo(
            points[0]
        )

        for point in points[1:]:

            path.lineTo(
                point
            )

        painter.setPen(
            QPen(
                color,
                1.7,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )

        painter.drawPath(
            path
        )

        # Last point

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            color
        )

        painter.drawEllipse(
            points[-1],
            3,
            3,
        )


# ==========================================================
# MARKET STATUS PILL
# ==========================================================

class MarketStatusPill(QLabel):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setFixedHeight(
            30
        )

        self.setMinimumWidth(
            110
        )

        self.set_market_open(
            False
        )

    def set_market_open(
        self,
        is_open: bool,
    ) -> None:

        if is_open:

            text = "●  MARKET OPEN"

            color = GREEN

            background = (
                "rgba(36,229,122,0.09)"
            )

            border = (
                "rgba(36,229,122,0.25)"
            )

        else:

            text = "●  MARKET CLOSED"

            color = RED

            background = (
                "rgba(255,77,94,0.09)"
            )

            border = (
                "rgba(255,77,94,0.25)"
            )

        self.setText(
            text
        )

        self.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: {background};
                border: 1px solid {border};
                border-radius: 7px;
                padding: 3px 10px;
                font-size: 8px;
                font-weight: 900;
            }}
            """
        )


# ==========================================================
# REFRESH BUTTON
# ==========================================================

class DashboardRefreshButton(QPushButton):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(
            "↻  Refresh",
            parent,
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setFixedHeight(
            32
        )

        self.setMinimumWidth(
            92
        )

        self.setStyleSheet(
            f"""
            QPushButton {{
                color: {TEXT_SECONDARY};
                background-color: #101C2E;
                border: 1px solid #223550;
                border-radius: 7px;
                padding: 4px 11px;
                font-size: 9px;
                font-weight: 700;
            }}

            QPushButton:hover {{
                color: {TEXT_PRIMARY};
                background-color: #15243B;
                border: 1px solid {BLUE};
            }}

            QPushButton:pressed {{
                background-color: #0B1628;
            }}

            QPushButton:disabled {{
                color: {TEXT_MUTED};
                border: 1px solid #17243A;
            }}
            """
        )

    def set_loading(
        self,
        loading: bool,
    ) -> None:

        self.setEnabled(
            not loading
        )

        self.setText(
            "↻  Updating..."
            if loading
            else "↻  Refresh"
        )


# ==========================================================
# DASHBOARD HERO
# ==========================================================

class DashboardHero(QFrame):

    refresh_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "DashboardHero"
        )

        self.setMinimumHeight(
            96
        )

        self.setStyleSheet(
            f"""
            QFrame#DashboardHero {{
                background-color: #0B1628;
                border: 1px solid {CARD_BORDER};
                border-radius: 13px;
            }}
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            18,
            13,
            18,
            13,
        )

        layout.setSpacing(
            14
        )

        # LEFT

        left = QVBoxLayout()

        left.setSpacing(
            3
        )

        title_row = QHBoxLayout()

        title = QLabel(
            "Market Command Center"
        )

        title.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 19px;
            font-weight: 900;
            """
        )

        title_row.addWidget(
            title
        )

        badge = QLabel(
            "STOCKVERSITY PRO"
        )

        badge.setStyleSheet(
            f"""
            QLabel {{
                color: {CYAN};
                background:
                    rgba(53,208,255,0.08);
                border:
                    1px solid rgba(53,208,255,0.18);
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 7px;
                font-weight: 900;
            }}
            """
        )

        title_row.addWidget(
            badge
        )

        title_row.addStretch(1)

        left.addLayout(
            title_row
        )

        subtitle = QLabel(
            "Scanner intelligence • Market structure • "
            "Momentum • Risk • Institutional confirmation"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 9px;
            """
        )

        left.addWidget(
            subtitle
        )

        session_row = QHBoxLayout()

        session_row.setSpacing(
            7
        )

        self.session_label = QLabel(
            "NSE • OFF MARKET"
        )

        self.session_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 8px;
            font-weight: 700;
            """
        )

        session_row.addWidget(
            self.session_label
        )

        separator = QLabel("•")

        separator.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            """
        )

        session_row.addWidget(
            separator
        )

        self.last_update_label = QLabel(
            "Last update: --"
        )

        self.last_update_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        session_row.addWidget(
            self.last_update_label
        )

        session_row.addStretch(1)

        left.addLayout(
            session_row
        )

        layout.addLayout(
            left,
            1,
        )

        # RIGHT

        self.market_status = (
            MarketStatusPill()
        )

        layout.addWidget(
            self.market_status
        )

        self.refresh_button = (
            DashboardRefreshButton()
        )

        self.refresh_button.clicked.connect(
            self.refresh_requested.emit
        )

        layout.addWidget(
            self.refresh_button
        )

    def set_last_update(
        self,
        text: str,
    ) -> None:

        self.last_update_label.setText(
            f"Last update: {text}"
        )


# ==========================================================
# INDEX CARD
# ==========================================================

class IndexCard(DashboardCard):
    """
    Premium market-index card.
    """

    clicked = Signal(str)

    def __init__(
        self,
        symbol: str,
        name: str,
        value: float,
        change: float,
        history: List[float],
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.symbol = symbol

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(
            128
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            11,
            14,
            11,
        )

        layout.setSpacing(
            4
        )

        # Title

        top = QHBoxLayout()

        self.name_label = QLabel(
            name
        )

        self.name_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 8px;
            font-weight: 800;
            """
        )

        top.addWidget(
            self.name_label
        )

        top.addStretch(1)

        self.direction_label = QLabel()

        top.addWidget(
            self.direction_label
        )

        layout.addLayout(
            top
        )

        # Value

        self.value_label = QLabel(
            f"{value:,.2f}"
        )

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            self.value_label
        )

        # Change + sparkline

        bottom = QHBoxLayout()

        self.change_label = QLabel()

        bottom.addWidget(
            self.change_label
        )

        bottom.addStretch(1)

        self.sparkline = SparklineWidget(
            history,
            positive=change >= 0,
        )

        self.sparkline.setFixedSize(
            90,
            38,
        )

        bottom.addWidget(
            self.sparkline
        )

        layout.addLayout(
            bottom
        )

        self.update_data(
            value,
            change,
            history,
        )

    def update_data(
        self,
        value: float,
        change: float,
        history: Optional[List[float]] = None,
    ) -> None:

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
            font-size: 9px;
            font-weight: 800;
            """
        )

        self.direction_label.setText(
            "▲"
            if change > 0
            else (
                "▼"
                if change < 0
                else "•"
            )
        )

        self.direction_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 10px;
            font-weight: 900;
            """
        )

        if history:

            self.sparkline.set_values(
                history
            )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.symbol
            )

        super().mouseReleaseEvent(
            event
        )


# ==========================================================
# OPPORTUNITY ROW
# ==========================================================

class OpportunityRow(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        rank: int,
        symbol: str,
        score: int,
        signal: str,
        pattern: str,
        rr: str,
        timeframe: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.symbol = symbol

        self.setObjectName(
            "OpportunityRow"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(
            49
        )

        self.setStyleSheet(
            """
            QFrame#OpportunityRow {
                background: transparent;
                border: none;
                border-bottom: 1px solid #17243A;
            }

            QFrame#OpportunityRow:hover {
                background:
                    rgba(76,141,255,0.055);
            }
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            7,
            4,
            7,
            4,
        )

        layout.setSpacing(
            8
        )

        # Rank

        rank_label = QLabel(
            f"#{rank}"
        )

        rank_label.setFixedWidth(
            28
        )

        rank_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            rank_label
        )

        # Stock

        stock = QLabel(
            symbol
        )

        stock.setMinimumWidth(
            80
        )

        stock.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 10px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            stock
        )

        # Score

        score_label = QLabel(
            str(score)
        )

        score_label.setAlignment(
            Qt.AlignCenter
        )

        score_label.setFixedSize(
            34,
            25,
        )

        if score >= 90:
            score_color = GREEN

        elif score >= 75:
            score_color = CYAN

        elif score >= 60:
            score_color = ORANGE

        else:
            score_color = RED

        score_label.setStyleSheet(
            f"""
            QLabel {{
                color: {score_color};
                background:
                    rgba(255,255,255,0.035);
                border-radius: 6px;
                font-size: 9px;
                font-weight: 900;
            }}
            """
        )

        layout.addWidget(
            score_label
        )

        layout.addWidget(
            SignalBadge(signal)
        )

        pattern_label = QLabel(
            pattern
        )

        pattern_label.setMinimumWidth(
            105
        )

        pattern_label.setStyleSheet(
            f"""
            color: {PURPLE};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            pattern_label
        )

        layout.addStretch(1)

        timeframe_label = QLabel(
            timeframe
        )

        timeframe_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            timeframe_label
        )

        rr_label = QLabel(
            rr
        )

        rr_label.setMinimumWidth(
            52
        )

        rr_label.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        rr_label.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 9px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            rr_label
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.symbol
            )

        super().mouseReleaseEvent(
            event
        )


# ==========================================================
# TOP OPPORTUNITIES CARD
# ==========================================================

class TopOpportunitiesCard(DashboardCard):

    stock_requested = Signal(str)

    scanner_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            335
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            12,
        )

        layout.setSpacing(
            7
        )

        header = SectionHeader(
            "TOP OPPORTUNITIES",
            "Open Scanner  →",
        )

        header.action_clicked.connect(
            self.scanner_requested.emit
        )

        layout.addWidget(
            header
        )

        subtitle = QLabel(
            "Highest-ranked setups across Intraday, Swing and Positional scanners"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(
            subtitle
        )

        # Column headings

        columns = QHBoxLayout()

        columns.setContentsMargins(
            7,
            2,
            7,
            2,
        )

        headings = [
            ("RANK", 28),
            ("STOCK", 80),
            ("SCORE", 34),
            ("SIGNAL", 58),
            ("PATTERN", 105),
        ]

        for text, width in headings:

            label = QLabel(text)

            label.setFixedWidth(
                width
            )

            label.setStyleSheet(
                f"""
                color: {TEXT_MUTED};
                font-size: 7px;
                font-weight: 800;
                """
            )

            columns.addWidget(
                label
            )

        columns.addStretch(1)

        tf = QLabel(
            "TF"
        )

        tf.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        columns.addWidget(tf)

        rr = QLabel(
            "R:R"
        )

        rr.setFixedWidth(
            52
        )

        rr.setAlignment(
            Qt.AlignRight
        )

        rr.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        columns.addWidget(rr)

        layout.addLayout(
            columns
        )

        self.rows_layout = QVBoxLayout()

        self.rows_layout.setSpacing(
            0
        )

        layout.addLayout(
            self.rows_layout
        )

        layout.addStretch(1)

    def set_opportunities(
        self,
        opportunities: List[Dict],
    ) -> None:

        clear_layout(
            self.rows_layout
        )

        for index, item in enumerate(
            opportunities,
            start=1,
        ):

            row = OpportunityRow(
                rank=index,
                symbol=item.get(
                    "symbol",
                    "",
                ),
                score=int(
                    item.get(
                        "score",
                        0,
                    )
                ),
                signal=item.get(
                    "signal",
                    "WATCH",
                ),
                pattern=item.get(
                    "pattern",
                    "--",
                ),
                rr=item.get(
                    "rr",
                    "--",
                ),
                timeframe=item.get(
                    "timeframe",
                    "--",
                ),
            )

            row.clicked.connect(
                self.stock_requested.emit
            )

            self.rows_layout.addWidget(
                row
            )


# ==========================================================
# SECTOR BAR
# ==========================================================

class SectorBar(QWidget):

    def __init__(
        self,
        name: str,
        value: float,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.name = name
        self.value = value

        self.setMinimumHeight(
            37
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        # Labels

        painter.setPen(
            QColor(TEXT_SECONDARY)
        )

        font = QFont(
            FONT_FAMILY,
            8,
        )

        font.setBold(True)

        painter.setFont(font)

        painter.drawText(
            QRectF(
                0,
                0,
                90,
                17,
            ),
            Qt.AlignLeft
            | Qt.AlignVCenter,
            self.name,
        )

        color = QColor(
            movement_color(
                self.value
            )
        )

        painter.setPen(
            color
        )

        painter.drawText(
            QRectF(
                self.width() - 55,
                0,
                55,
                17,
            ),
            Qt.AlignRight
            | Qt.AlignVCenter,
            percentage_text(
                self.value
            ),
        )

        track = QRectF(
            0,
            22,
            self.width(),
            7,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor("#17253A")
        )

        painter.drawRoundedRect(
            track,
            3.5,
            3.5,
        )

        ratio = min(
            abs(self.value) / 4.0,
            1.0,
        )

        active = QRectF(
            track.left(),
            track.top(),
            track.width() * ratio,
            track.height(),
        )

        painter.setBrush(
            color
        )

        painter.drawRoundedRect(
            active,
            3.5,
            3.5,
        )


# ==========================================================
# SECTOR STRENGTH CARD
# ==========================================================

class SectorStrengthCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            305
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            7
        )

        layout.addWidget(
            SectionHeader(
                "SECTOR ROTATION"
            )
        )

        subtitle = QLabel(
            "Relative sector performance"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(
            subtitle
        )

        self.sectors_layout = QVBoxLayout()

        self.sectors_layout.setSpacing(
            4
        )

        layout.addLayout(
            self.sectors_layout
        )

        layout.addStretch(1)

    def set_sectors(
        self,
        sectors: List[Dict],
    ) -> None:

        clear_layout(
            self.sectors_layout
        )

        for sector in sectors:

            self.sectors_layout.addWidget(
                SectorBar(
                    sector.get(
                        "name",
                        "",
                    ),
                    float(
                        sector.get(
                            "change",
                            0.0,
                        )
                    ),
                )
            )


# ==========================================================
# MARKET BREADTH VISUAL
# ==========================================================

class BreadthVisual(QWidget):

    def __init__(
        self,
        advances: int = 0,
        declines: int = 0,
        unchanged: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.advances = advances
        self.declines = declines
        self.unchanged = unchanged

        self.setMinimumHeight(
            105
        )

    def set_values(
        self,
        advances: int,
        declines: int,
        unchanged: int,
    ) -> None:

        self.advances = advances
        self.declines = declines
        self.unchanged = unchanged

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        total = (
            self.advances
            + self.declines
            + self.unchanged
        )

        if total <= 0:
            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        track = QRectF(
            8,
            43,
            self.width() - 16,
            15,
        )

        advance_ratio = (
            self.advances / total
        )

        decline_ratio = (
            self.declines / total
        )

        advance_width = (
            track.width()
            * advance_ratio
        )

        decline_width = (
            track.width()
            * decline_ratio
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(GREEN)
        )

        painter.drawRoundedRect(
            QRectF(
                track.left(),
                track.top(),
                advance_width,
                track.height(),
            ),
            6,
            6,
        )

        painter.setBrush(
            QColor(TEXT_MUTED)
        )

        neutral_start = (
            track.left()
            + advance_width
        )

        neutral_width = (
            track.width()
            - advance_width
            - decline_width
        )

        if neutral_width > 0:

            painter.drawRect(
                QRectF(
                    neutral_start,
                    track.top(),
                    neutral_width,
                    track.height(),
                )
            )

        painter.setBrush(
            QColor(RED)
        )

        painter.drawRoundedRect(
            QRectF(
                track.right()
                - decline_width,
                track.top(),
                decline_width,
                track.height(),
            ),
            6,
            6,
        )

        font = QFont(
            FONT_FAMILY,
            9,
        )

        font.setBold(True)

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(GREEN)
        )

        painter.drawText(
            QRectF(
                8,
                10,
                110,
                22,
            ),
            Qt.AlignLeft,
            f"{self.advances} Advances",
        )

        painter.setPen(
            QColor(RED)
        )

        painter.drawText(
            QRectF(
                self.width() - 120,
                10,
                112,
                22,
            ),
            Qt.AlignRight,
            f"{self.declines} Declines",
        )

        painter.setPen(
            QColor(TEXT_MUTED)
        )

        painter.drawText(
            QRectF(
                0,
                68,
                self.width(),
                20,
            ),
            Qt.AlignCenter,
            f"{self.unchanged} unchanged",
        )


# ==========================================================
# MARKET BREADTH CARD
# ==========================================================

class MarketBreadthCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            305
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            SectionHeader(
                "MARKET BREADTH"
            )
        )

        self.visual = BreadthVisual()

        layout.addWidget(
            self.visual
        )

        self.ratio_label = QLabel(
            "A/D RATIO  --"
        )

        self.ratio_label.setAlignment(
            Qt.AlignCenter
        )

        self.ratio_label.setStyleSheet(
            f"""
            color: {CYAN};
            background:
                rgba(53,208,255,0.06);
            border-radius: 6px;
            padding: 6px;
            font-size: 9px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.ratio_label
        )

        self.status_label = QLabel(
            "Waiting for breadth data"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        self.status_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            self.status_label
        )

        layout.addStretch(1)

    def set_breadth(
        self,
        advances: int,
        declines: int,
        unchanged: int,
    ) -> None:

        self.visual.set_values(
            advances,
            declines,
            unchanged,
        )

        ratio = (
            advances / declines
            if declines > 0
            else float(advances)
        )

        self.ratio_label.setText(
            f"A/D RATIO  {ratio:.2f}"
        )

        if ratio >= 1.5:

            status = "STRONG PARTICIPATION"
            color = GREEN

        elif ratio <= 0.67:

            status = "WEAK PARTICIPATION"
            color = RED

        else:

            status = "MIXED PARTICIPATION"
            color = ORANGE

        self.status_label.setText(
            status
        )

        self.status_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 8px;
            font-weight: 800;
            """
        )


# ==========================================================
# MARKET INTELLIGENCE CONTAINER
# ==========================================================

class MarketIntelligencePanel(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        layout = QGridLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setHorizontalSpacing(
            12
        )

        layout.setVerticalSpacing(
            12
        )

        self.sector_strength = (
            SectorStrengthCard()
        )

        self.market_breadth = (
            MarketBreadthCard()
        )

        layout.addWidget(
            self.sector_strength,
            0,
            0,
        )

        layout.addWidget(
            self.market_breadth,
            0,
            1,
        )

        layout.setColumnStretch(
            0,
            1,
        )

        layout.setColumnStretch(
            1,
            1,
        )


# ==========================================================
# HEATMAP TILE
# ==========================================================

class HeatmapTile(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        symbol: str,
        change_percent: float,
        weight: int = 1,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.symbol = symbol

        self.change_percent = (
            change_percent
        )

        self.weight = max(
            1,
            weight,
        )

        self.setObjectName(
            "HeatmapTile"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(
            72
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        layout.setSpacing(
            2
        )

        layout.addStretch(1)

        self.symbol_label = QLabel(
            self.symbol
        )

        self.symbol_label.setAlignment(
            Qt.AlignCenter
        )

        self.symbol_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            background: transparent;
            border: none;
            font-size: 10px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            self.symbol_label
        )

        self.change_label = QLabel()

        self.change_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.change_label
        )

        layout.addStretch(1)

        self._apply_style()

    def _tile_colors(
        self,
    ) -> tuple[str, str, str]:

        magnitude = min(
            abs(self.change_percent),
            6.0,
        )

        strength = magnitude / 6.0

        if self.change_percent > 0:

            alpha = int(
                45 + 125 * strength
            )

            background = (
                f"rgba(14,137,75,{alpha})"
            )

            border = (
                "rgba(36,229,122,0.40)"
            )

            text = GREEN

        elif self.change_percent < 0:

            alpha = int(
                45 + 125 * strength
            )

            background = (
                f"rgba(169,31,53,{alpha})"
            )

            border = (
                "rgba(255,77,94,0.40)"
            )

            text = RED

        else:

            background = (
                "rgba(100,116,139,0.14)"
            )

            border = (
                "rgba(148,163,184,0.22)"
            )

            text = TEXT_SECONDARY

        return (
            background,
            border,
            text,
        )

    def _apply_style(
        self,
    ) -> None:

        background, border, text = (
            self._tile_colors()
        )

        self.change_label.setText(
            percentage_text(
                self.change_percent
            )
        )

        self.change_label.setStyleSheet(
            f"""
            color: {text};
            background: transparent;
            border: none;
            font-size: 9px;
            font-weight: 900;
            """
        )

        self.setStyleSheet(
            f"""
            QFrame#HeatmapTile {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: 8px;
            }}

            QFrame#HeatmapTile:hover {{
                border: 1px solid {CYAN};
            }}
            """
        )

    def update_change(
        self,
        change_percent: float,
    ) -> None:

        self.change_percent = (
            change_percent
        )

        self._apply_style()

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.symbol
            )

        super().mouseReleaseEvent(
            event
        )


# ==========================================================
# HEATMAP LEGEND
# ==========================================================

class HeatmapLegend(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            6
        )

        label = QLabel(
            "Performance"
        )

        label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            label
        )

        values = [
            ("< -3%", RED),
            ("-1%", "#B63A49"),
            ("0%", TEXT_MUTED),
            ("+1%", "#18A95E"),
            ("> +3%", GREEN),
        ]

        for text, color in values:

            indicator = QLabel(
                text
            )

            indicator.setStyleSheet(
                f"""
                QLabel {{
                    color: {color};
                    background:
                        rgba(255,255,255,0.025);
                    border-radius: 4px;
                    padding: 2px 5px;
                    font-size: 7px;
                    font-weight: 700;
                }}
                """
            )

            layout.addWidget(
                indicator
            )

        layout.addStretch(1)


# ==========================================================
# MARKET HEATMAP CARD
# ==========================================================

class MarketHeatmapCard(DashboardCard):

    stock_requested = Signal(str)

    view_all_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.tiles: Dict[
            str,
            HeatmapTile,
        ] = {}

        self.setMinimumHeight(
            350
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            10
        )

        header = SectionHeader(
            "MARKET HEATMAP",
            "Full Market  →",
        )

        header.action_clicked.connect(
            self.view_all_requested.emit
        )

        layout.addWidget(
            header
        )

        subtitle_row = QHBoxLayout()

        subtitle = QLabel(
            "NIFTY 50 • Today's Performance"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 9px;
            font-weight: 600;
            """
        )

        subtitle_row.addWidget(
            subtitle
        )

        subtitle_row.addStretch(1)

        self.market_bias_label = QLabel(
            "MIXED"
        )

        subtitle_row.addWidget(
            self.market_bias_label
        )

        layout.addLayout(
            subtitle_row
        )

        self.heatmap_container = QWidget()

        self.heatmap_grid = QGridLayout(
            self.heatmap_container
        )

        self.heatmap_grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.heatmap_grid.setSpacing(
            5
        )

        layout.addWidget(
            self.heatmap_container,
            1,
        )

        layout.addWidget(
            HeatmapLegend()
        )

    def set_stocks(
        self,
        stocks: List[Dict],
    ) -> None:

        clear_layout(
            self.heatmap_grid
        )

        self.tiles.clear()

        if not stocks:
            return

        columns = 6

        for index, stock in enumerate(
            stocks
        ):

            symbol = stock.get(
                "symbol",
                "",
            )

            change = float(
                stock.get(
                    "change_percent",
                    0.0,
                )
            )

            weight = int(
                stock.get(
                    "weight",
                    1,
                )
            )

            tile = HeatmapTile(
                symbol=symbol,
                change_percent=change,
                weight=weight,
            )

            tile.clicked.connect(
                self.stock_requested.emit
            )

            self.tiles[
                symbol
            ] = tile

            row = index // columns

            column = index % columns

            self.heatmap_grid.addWidget(
                tile,
                row,
                column,
            )

        for column in range(
            columns
        ):

            self.heatmap_grid.setColumnStretch(
                column,
                1,
            )

        self._update_market_bias(
            stocks
        )

    def _update_market_bias(
        self,
        stocks: List[Dict],
    ) -> None:

        positive = sum(
            1
            for stock in stocks
            if float(
                stock.get(
                    "change_percent",
                    0,
                )
            ) > 0
        )

        negative = sum(
            1
            for stock in stocks
            if float(
                stock.get(
                    "change_percent",
                    0,
                )
            ) < 0
        )

        if positive > negative * 1.5:

            text = "BULLISH"
            color = GREEN

        elif negative > positive * 1.5:

            text = "BEARISH"
            color = RED

        else:

            text = "MIXED"
            color = ORANGE

        self.market_bias_label.setText(
            text
        )

        self.market_bias_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border: 1px solid {color};
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 8px;
                font-weight: 800;
            }}
            """
        )


# ==========================================================
# SCANNER METRIC CARD
# ==========================================================

class ScannerMetricCard(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        scanner_type: str,
        title: str,
        accent: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.scanner_type = scanner_type
        self.accent = accent

        self.setObjectName(
            "ScannerMetricCard"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(
            150
        )

        self.setStyleSheet(
            f"""
            QFrame#ScannerMetricCard {{
                background-color: #0A1526;
                border: 1px solid #1B2A42;
                border-radius: 11px;
            }}

            QFrame#ScannerMetricCard:hover {{
                background-color: #0E1B30;
                border: 1px solid {accent};
            }}
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        layout.setSpacing(
            7
        )

        top = QHBoxLayout()

        self.title_label = QLabel(
            title
        )

        self.title_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 11px;
            font-weight: 800;
            """
        )

        top.addWidget(
            self.title_label
        )

        top.addStretch(1)

        status_dot = QLabel("●")

        status_dot.setStyleSheet(
            f"""
            color: {accent};
            font-size: 10px;
            """
        )

        top.addWidget(
            status_dot
        )

        layout.addLayout(top)

        number_row = QHBoxLayout()

        self.count_label = QLabel(
            "0"
        )

        self.count_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 28px;
            font-weight: 900;
            """
        )

        number_row.addWidget(
            self.count_label
        )

        description = QLabel(
            "opportunities"
        )

        description.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 9px;
            """
        )

        number_row.addWidget(
            description,
            alignment=Qt.AlignBottom,
        )

        number_row.addStretch(1)

        layout.addLayout(
            number_row
        )

        score_row = QHBoxLayout()

        score_title = QLabel(
            "BEST SCORE"
        )

        score_title.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 700;
            """
        )

        score_row.addWidget(
            score_title
        )

        score_row.addStretch(1)

        self.best_score_label = QLabel(
            "--"
        )

        self.best_score_label.setStyleSheet(
            f"""
            color: {accent};
            font-size: 12px;
            font-weight: 900;
            """
        )

        score_row.addWidget(
            self.best_score_label
        )

        layout.addLayout(
            score_row
        )

        signals = QHBoxLayout()

        self.buy_label = QLabel(
            "BUY 0"
        )

        self.sell_label = QLabel(
            "SELL 0"
        )

        signals.addWidget(
            self.buy_label
        )

        signals.addWidget(
            self.sell_label
        )

        signals.addStretch(1)

        self.bias_label = QLabel(
            "MIXED"
        )

        signals.addWidget(
            self.bias_label
        )

        layout.addLayout(
            signals
        )

        self.update_data(
            0,
            0,
            0,
            0,
        )

    def update_data(
        self,
        count: int,
        best_score: int,
        buys: int,
        sells: int,
    ) -> None:

        self.count_label.setText(
            str(count)
        )

        self.best_score_label.setText(
            str(best_score)
            if best_score
            else "--"
        )

        self.buy_label.setText(
            f"BUY {buys}"
        )

        self.sell_label.setText(
            f"SELL {sells}"
        )

        self.buy_label.setStyleSheet(
            f"""
            QLabel {{
                color: {GREEN};
                background:
                    rgba(36,229,122,0.09);
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 8px;
                font-weight: 800;
            }}
            """
        )

        self.sell_label.setStyleSheet(
            f"""
            QLabel {{
                color: {RED};
                background:
                    rgba(255,77,94,0.09);
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 8px;
                font-weight: 800;
            }}
            """
        )

        if buys > sells * 1.5:

            bias = "BULLISH"
            color = GREEN

        elif sells > buys * 1.5:

            bias = "BEARISH"
            color = RED

        else:

            bias = "MIXED"
            color = ORANGE

        self.bias_label.setText(
            bias
        )

        self.bias_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border-radius: 5px;
                padding: 3px 7px;
                font-size: 8px;
                font-weight: 800;
            }}
            """
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.scanner_type
            )

        super().mouseReleaseEvent(
            event
        )
        # ==========================================================
# SCANNER SUMMARY CARD
# ==========================================================

class ScannerSummaryCard(DashboardCard):

    scanner_requested = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(235)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16, 14, 16, 14
        )

        layout.setSpacing(10)

        layout.addWidget(
            SectionHeader(
                "SCANNER ENGINE"
            )
        )

        subtitle = QLabel(
            "Real-time opportunity discovery across trading horizons"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(subtitle)

        cards = QHBoxLayout()

        cards.setSpacing(10)

        self.intraday_card = ScannerMetricCard(
            scanner_type="intraday",
            title="INTRADAY",
            accent=CYAN,
        )

        self.swing_card = ScannerMetricCard(
            scanner_type="swing",
            title="SWING",
            accent=GREEN,
        )

        self.positional_card = ScannerMetricCard(
            scanner_type="positional",
            title="POSITIONAL",
            accent=PURPLE,
        )

        self.intraday_card.clicked.connect(
            self.scanner_requested.emit
        )

        self.swing_card.clicked.connect(
            self.scanner_requested.emit
        )

        self.positional_card.clicked.connect(
            self.scanner_requested.emit
        )

        cards.addWidget(
            self.intraday_card,
            1,
        )

        cards.addWidget(
            self.swing_card,
            1,
        )

        cards.addWidget(
            self.positional_card,
            1,
        )

        layout.addLayout(cards)

    def set_scanner_data(
        self,
        data: Dict,
    ) -> None:

        intraday = data.get(
            "intraday",
            {},
        )

        swing = data.get(
            "swing",
            {},
        )

        positional = data.get(
            "positional",
            {},
        )

        self.intraday_card.update_data(
            count=int(
                intraday.get(
                    "count",
                    0,
                )
            ),
            best_score=int(
                intraday.get(
                    "best_score",
                    0,
                )
            ),
            buys=int(
                intraday.get(
                    "buys",
                    0,
                )
            ),
            sells=int(
                intraday.get(
                    "sells",
                    0,
                )
            ),
        )

        self.swing_card.update_data(
            count=int(
                swing.get(
                    "count",
                    0,
                )
            ),
            best_score=int(
                swing.get(
                    "best_score",
                    0,
                )
            ),
            buys=int(
                swing.get(
                    "buys",
                    0,
                )
            ),
            sells=int(
                swing.get(
                    "sells",
                    0,
                )
            ),
        )

        self.positional_card.update_data(
            count=int(
                positional.get(
                    "count",
                    0,
                )
            ),
            best_score=int(
                positional.get(
                    "best_score",
                    0,
                )
            ),
            buys=int(
                positional.get(
                    "buys",
                    0,
                )
            ),
            sells=int(
                positional.get(
                    "sells",
                    0,
                )
            ),
        )


# ==========================================================
# MOVER ROW
# ==========================================================

class MoverRow(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        symbol: str,
        price: float,
        change: float,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.symbol = symbol

        self.setObjectName(
            "MoverRow"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(44)

        self.setStyleSheet(
            """
            QFrame#MoverRow {
                background: transparent;
                border: none;
                border-bottom: 1px solid #17243A;
            }

            QFrame#MoverRow:hover {
                background:
                    rgba(76,141,255,0.05);
            }
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            7, 3, 7, 3
        )

        symbol_label = QLabel(
            symbol
        )

        symbol_label.setMinimumWidth(78)

        symbol_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 9px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            symbol_label
        )

        layout.addStretch(1)

        price_label = QLabel(
            f"₹{price:,.2f}"
        )

        price_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            price_label
        )

        change_label = QLabel(
            percentage_text(change)
        )

        change_label.setMinimumWidth(62)

        change_label.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        change_label.setStyleSheet(
            f"""
            color: {movement_color(change)};
            font-size: 9px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            change_label
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.symbol
            )

        super().mouseReleaseEvent(
            event
        )


# ==========================================================
# TOP MOVERS CARD
# ==========================================================

class TopMoversCard(DashboardCard):

    stock_requested = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(330)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16, 14, 16, 14
        )

        layout.setSpacing(8)

        layout.addWidget(
            SectionHeader(
                "TOP MOVERS"
            )
        )

        subtitle = QLabel(
            "Strongest price movement in the active universe"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(subtitle)

        columns = QHBoxLayout()

        columns.setContentsMargins(
            7, 2, 7, 2
        )

        stock_heading = QLabel(
            "STOCK"
        )

        stock_heading.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        columns.addWidget(
            stock_heading
        )

        columns.addStretch(1)

        price_heading = QLabel(
            "PRICE"
        )

        price_heading.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        columns.addWidget(
            price_heading
        )

        change_heading = QLabel(
            "CHANGE"
        )

        change_heading.setMinimumWidth(
            62
        )

        change_heading.setAlignment(
            Qt.AlignRight
        )

        change_heading.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        columns.addWidget(
            change_heading
        )

        layout.addLayout(columns)

        self.rows_layout = QVBoxLayout()

        self.rows_layout.setSpacing(0)

        layout.addLayout(
            self.rows_layout
        )

        layout.addStretch(1)

    def set_movers(
        self,
        movers: List[Dict],
    ) -> None:

        clear_layout(
            self.rows_layout
        )

        for mover in movers:

            row = MoverRow(
                symbol=mover.get(
                    "symbol",
                    "",
                ),
                price=float(
                    mover.get(
                        "price",
                        0.0,
                    )
                ),
                change=float(
                    mover.get(
                        "change",
                        0.0,
                    )
                ),
            )

            row.clicked.connect(
                self.stock_requested.emit
            )

            self.rows_layout.addWidget(
                row
            )


# ==========================================================
# WATCHLIST ROW
# ==========================================================

class WatchlistRow(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        symbol: str,
        price: float,
        change: float,
        signal: str,
        score: int,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.symbol = symbol

        self.setObjectName(
            "WatchlistRow"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(49)

        self.setStyleSheet(
            """
            QFrame#WatchlistRow {
                background: transparent;
                border: none;
                border-bottom: 1px solid #17243A;
            }

            QFrame#WatchlistRow:hover {
                background:
                    rgba(53,208,255,0.04);
            }
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            7, 4, 7, 4
        )

        layout.setSpacing(8)

        symbol_label = QLabel(
            symbol
        )

        symbol_label.setMinimumWidth(
            72
        )

        symbol_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 9px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            symbol_label
        )

        price_label = QLabel(
            f"₹{price:,.2f}"
        )

        price_label.setMinimumWidth(
            75
        )

        price_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            price_label
        )

        change_label = QLabel(
            percentage_text(change)
        )

        change_label.setMinimumWidth(
            58
        )

        change_label.setStyleSheet(
            f"""
            color: {movement_color(change)};
            font-size: 8px;
            font-weight: 900;
            """
        )

        layout.addWidget(
            change_label
        )

        layout.addStretch(1)

        score_label = QLabel(
            str(score)
        )

        score_label.setAlignment(
            Qt.AlignCenter
        )

        score_label.setFixedSize(
            31,
            24,
        )

        score_color = (
            GREEN
            if score >= 85
            else (
                CYAN
                if score >= 70
                else ORANGE
            )
        )

        score_label.setStyleSheet(
            f"""
            QLabel {{
                color: {score_color};
                background:
                    rgba(255,255,255,0.035);
                border-radius: 5px;
                font-size: 8px;
                font-weight: 900;
            }}
            """
        )

        layout.addWidget(
            score_label
        )

        layout.addWidget(
            SignalBadge(signal)
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.symbol
            )

        super().mouseReleaseEvent(
            event
        )


# ==========================================================
# WATCHLIST CARD
# ==========================================================

class WatchlistCard(DashboardCard):

    stock_requested = Signal(str)

    watchlist_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            335
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16, 14, 16, 14
        )

        layout.setSpacing(7)

        header = SectionHeader(
            "SMART WATCHLIST",
            "Manage  →",
        )

        header.action_clicked.connect(
            self.watchlist_requested.emit
        )

        layout.addWidget(header)

        subtitle = QLabel(
            "Your stocks ranked by current setup quality"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(subtitle)

        self.rows_layout = QVBoxLayout()

        self.rows_layout.setSpacing(0)

        layout.addLayout(
            self.rows_layout
        )

        layout.addStretch(1)

    def set_watchlist(
        self,
        stocks: List[Dict],
    ) -> None:

        clear_layout(
            self.rows_layout
        )

        for stock in stocks:

            row = WatchlistRow(
                symbol=stock.get(
                    "symbol",
                    "",
                ),
                price=float(
                    stock.get(
                        "price",
                        0.0,
                    )
                ),
                change=float(
                    stock.get(
                        "change",
                        0.0,
                    )
                ),
                signal=stock.get(
                    "signal",
                    "WATCH",
                ),
                score=int(
                    stock.get(
                        "score",
                        0,
                    )
                ),
            )

            row.clicked.connect(
                self.stock_requested.emit
            )

            self.rows_layout.addWidget(
                row
            )


# ==========================================================
# ALERT ROW
# ==========================================================

class AlertRow(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        time_text: str,
        symbol: str,
        message: str,
        alert_type: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.symbol = symbol

        self.setObjectName(
            "AlertRow"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setMinimumHeight(
            59
        )

        self.setStyleSheet(
            """
            QFrame#AlertRow {
                background:
                    rgba(255,255,255,0.016);
                border: 1px solid #17243A;
                border-radius: 7px;
            }

            QFrame#AlertRow:hover {
                background:
                    rgba(76,141,255,0.05);
            }
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            9, 6, 9, 6
        )

        layout.setSpacing(8)

        alert_type = (
            alert_type
            .strip()
            .upper()
        )

        if alert_type in (
            "BREAKOUT",
            "BUY",
        ):

            accent = GREEN
            icon = "▲"

        elif alert_type in (
            "BREAKDOWN",
            "SELL",
        ):

            accent = RED
            icon = "▼"

        else:

            accent = CYAN
            icon = "●"

        icon_label = QLabel(
            icon
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setFixedSize(
            27,
            27,
        )

        icon_label.setStyleSheet(
            f"""
            QLabel {{
                color: {accent};
                background:
                    rgba(255,255,255,0.035);
                border-radius: 13px;
                font-size: 10px;
                font-weight: 900;
            }}
            """
        )

        layout.addWidget(
            icon_label
        )

        text_box = QVBoxLayout()

        text_box.setSpacing(1)

        top = QHBoxLayout()

        symbol_label = QLabel(
            symbol
        )

        symbol_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 9px;
            font-weight: 900;
            """
        )

        top.addWidget(
            symbol_label
        )

        top.addStretch(1)

        time_label = QLabel(
            time_text
        )

        time_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            """
        )

        top.addWidget(
            time_label
        )

        text_box.addLayout(top)

        message_label = QLabel(
            message
        )

        message_label.setWordWrap(True)

        message_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 8px;
            """
        )

        text_box.addWidget(
            message_label
        )

        layout.addLayout(
            text_box,
            1,
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.symbol
            )

        super().mouseReleaseEvent(
            event
        )


# ==========================================================
# LIVE ALERTS CARD
# ==========================================================

class LiveAlertsCard(DashboardCard):

    stock_requested = Signal(str)

    alerts_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            335
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16, 14, 16, 14
        )

        layout.setSpacing(7)

        header = SectionHeader(
            "LIVE SCANNER ALERTS",
            "View All  →",
        )

        header.action_clicked.connect(
            self.alerts_requested.emit
        )

        layout.addWidget(header)

        top = QHBoxLayout()

        subtitle = QLabel(
            "High-priority scanner events"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        top.addWidget(subtitle)

        top.addStretch(1)

        live = QLabel(
            "● LIVE"
        )

        live.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 7px;
            font-weight: 900;
            """
        )

        top.addWidget(live)

        layout.addLayout(top)

        self.rows_layout = QVBoxLayout()

        self.rows_layout.setSpacing(6)

        layout.addLayout(
            self.rows_layout
        )

        layout.addStretch(1)

    def set_alerts(
        self,
        alerts: List[Dict],
    ) -> None:

        clear_layout(
            self.rows_layout
        )

        for alert in alerts:

            row = AlertRow(
                time_text=alert.get(
                    "time",
                    "--",
                ),
                symbol=alert.get(
                    "symbol",
                    "",
                ),
                message=alert.get(
                    "message",
                    "",
                ),
                alert_type=alert.get(
                    "type",
                    "INFO",
                ),
            )

            row.clicked.connect(
                self.stock_requested.emit
            )

            self.rows_layout.addWidget(
                row
            )


# ==========================================================
# MARKET PULSE GAUGE
# ==========================================================

class MarketPulseGauge(QWidget):

    def __init__(
        self,
        score: int = 50,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._score = max(
            0,
            min(100, score),
        )

        self.setMinimumSize(
            250,
            175,
        )

    def set_score(
        self,
        score: int,
    ) -> None:

        self._score = max(
            0,
            min(
                100,
                int(score),
            ),
        )

        self.update()

    def score(
        self,
    ) -> int:

        return self._score

    def _state(
        self,
    ) -> tuple[str, str]:

        if self._score >= 76:

            return (
                "STRONG BULLISH",
                GREEN,
            )

        if self._score >= 56:

            return (
                "BULLISH",
                CYAN,
            )

        if self._score >= 46:

            return (
                "NEUTRAL",
                ORANGE,
            )

        if self._score >= 26:

            return (
                "FEAR",
                "#FF8A4C",
            )

        return (
            "EXTREME FEAR",
            RED,
        )

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        width = min(
            self.width() - 45,
            250,
        )

        height = 135

        left = (
            self.width() - width
        ) / 2

        gauge_rect = QRectF(
            left,
            28,
            width,
            height,
        )

        pen_width = 18

        # Base arc

        painter.setPen(
            QPen(
                QColor("#1A293E"),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            gauge_rect,
            0,
            180 * 16,
        )

        # Sentiment segments

        segments = [
            (0, 25, RED),
            (25, 45, "#FF8A4C"),
            (45, 55, ORANGE),
            (55, 75, CYAN),
            (75, 100, GREEN),
        ]

        for start, end, color in segments:

            segment_color = QColor(
                color
            )

            segment_color.setAlpha(
                75
            )

            painter.setPen(
                QPen(
                    segment_color,
                    7,
                    Qt.SolidLine,
                    Qt.RoundCap,
                )
            )

            start_angle = (
                180
                - start * 1.8
            )

            span = (
                end - start
            ) * 1.8

            painter.drawArc(
                gauge_rect.adjusted(
                    8,
                    8,
                    -8,
                    -8,
                ),
                int(
                    start_angle * 16
                ),
                int(
                    -span * 16
                ),
            )

        state, state_color = (
            self._state()
        )

        active_angle = (
            self._score * 1.8
        )

        painter.setPen(
            QPen(
                QColor(
                    state_color
                ),
                pen_width,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            gauge_rect,
            180 * 16,
            int(
                -active_angle * 16
            ),
        )

        score_font = QFont(
            FONT_FAMILY,
            24,
        )

        score_font.setBold(True)

        painter.setFont(
            score_font
        )

        painter.setPen(
            QColor(TEXT_PRIMARY)
        )

        painter.drawText(
            QRectF(
                0,
                78,
                self.width(),
                38,
            ),
            Qt.AlignCenter,
            str(self._score),
        )

        state_font = QFont(
            FONT_FAMILY,
            8,
        )

        state_font.setBold(True)

        painter.setFont(
            state_font
        )

        painter.setPen(
            QColor(
                state_color
            )
        )

        painter.drawText(
            QRectF(
                0,
                113,
                self.width(),
                22,
            ),
            Qt.AlignCenter,
            state,
        )


# ==========================================================
# MARKET TREND CURVE
# ==========================================================

class MarketTrendCurve(QWidget):

    def __init__(
        self,
        values: Optional[List[float]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._values = (
            list(values)
            if values
            else []
        )

        self.setMinimumHeight(
            135
        )

    def set_values(
        self,
        values: List[float],
    ) -> None:

        self._values = list(values)

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        if len(self._values) < 2:
            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = self.rect().adjusted(
            8,
            10,
            -8,
            -20,
        )

        # Grid

        painter.setPen(
            QPen(
                QColor("#17243A"),
                1,
            )
        )

        for index in range(
            1,
            4,
        ):

            y = (
                rect.top()
                + rect.height()
                * index
                / 4
            )

            painter.drawLine(
                QPointF(
                    rect.left(),
                    y,
                ),
                QPointF(
                    rect.right(),
                    y,
                ),
            )

        minimum = min(
            self._values
        )

        maximum = max(
            self._values
        )

        spread = maximum - minimum

        if spread == 0:
            spread = 1.0

        step = (
            rect.width()
            / (
                len(self._values) - 1
            )
        )

        points: List[
            QPointF
        ] = []

        for index, value in enumerate(
            self._values
        ):

            normalized = (
                value - minimum
            ) / spread

            x = (
                rect.left()
                + index * step
            )

            y = (
                rect.bottom()
                - normalized
                * rect.height()
            )

            points.append(
                QPointF(
                    x,
                    y,
                )
            )

        positive = (
            self._values[-1]
            >= self._values[0]
        )

        color = QColor(
            GREEN
            if positive
            else RED
        )

        # Area

        area = QPainterPath()

        area.moveTo(
            points[0]
        )

        for point in points[1:]:

            area.lineTo(
                point
            )

        area.lineTo(
            QPointF(
                points[-1].x(),
                rect.bottom(),
            )
        )

        area.lineTo(
            QPointF(
                points[0].x(),
                rect.bottom(),
            )
        )

        area.closeSubpath()

        gradient = QLinearGradient(
            0,
            rect.top(),
            0,
            rect.bottom(),
        )

        top_color = QColor(
            color
        )

        top_color.setAlpha(
            75
        )

        bottom_color = QColor(
            color
        )

        bottom_color.setAlpha(
            0
        )

        gradient.setColorAt(
            0,
            top_color,
        )

        gradient.setColorAt(
            1,
            bottom_color,
        )

        painter.fillPath(
            area,
            gradient,
        )

        # Curve

        path = QPainterPath()

        path.moveTo(
            points[0]
        )

        for point in points[1:]:

            path.lineTo(
                point
            )

        painter.setPen(
            QPen(
                color,
                2.0,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )

        painter.drawPath(
            path
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            color
        )

        painter.drawEllipse(
            points[-1],
            4,
            4,
        )


# ==========================================================
# INTELLIGENCE METRIC
# ==========================================================

class IntelligenceMetric(QFrame):

    def __init__(
        self,
        title: str,
        value: str,
        status: str,
        color: str,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "IntelligenceMetric"
        )

        self.setMinimumHeight(
            78
        )

        self.setStyleSheet(
            """
            QFrame#IntelligenceMetric {
                background:
                    rgba(255,255,255,0.022);
                border:
                    1px solid #18273C;
                border-radius: 9px;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            11,
            8,
            11,
            8,
        )

        layout.setSpacing(2)

        self.title_label = QLabel(
            title
        )

        self.title_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 700;
            """
        )

        layout.addWidget(
            self.title_label
        )

        self.value_label = QLabel(
            value
        )

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.value_label
        )

        self.status_label = QLabel(
            status
        )

        self.status_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 8px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.status_label
        )

    def set_metric(
        self,
        value: str,
        status: str,
        color: str,
    ) -> None:

        self.value_label.setText(
            value
        )

        self.status_label.setText(
            status
        )

        self.status_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 8px;
            font-weight: 800;
            """
        )


# ==========================================================
# MARKET PULSE CARD
# ==========================================================

class MarketPulseCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            345
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            9
        )

        layout.addWidget(
            SectionHeader(
                "MARKET PULSE"
            )
        )

        subtitle = QLabel(
            "Composite momentum, breadth, volatility "
            "and institutional positioning"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 9px;
            """
        )

        layout.addWidget(
            subtitle
        )

        content = QHBoxLayout()

        content.setSpacing(
            14
        )

        self.pulse_gauge = (
            MarketPulseGauge()
        )

        content.addWidget(
            self.pulse_gauge,
            2,
        )

        metrics = QGridLayout()

        metrics.setSpacing(
            8
        )

        self.trend_metric = (
            IntelligenceMetric(
                "NIFTY TREND",
                "--",
                "Waiting for data",
                TEXT_MUTED,
            )
        )

        self.volatility_metric = (
            IntelligenceMetric(
                "VOLATILITY",
                "--",
                "Waiting for data",
                TEXT_MUTED,
            )
        )

        self.institution_metric = (
            IntelligenceMetric(
                "INSTITUTIONAL BIAS",
                "--",
                "Waiting for data",
                TEXT_MUTED,
            )
        )

        self.momentum_metric = (
            IntelligenceMetric(
                "MOMENTUM",
                "--",
                "Waiting for data",
                TEXT_MUTED,
            )
        )

        metrics.addWidget(
            self.trend_metric,
            0,
            0,
        )

        metrics.addWidget(
            self.volatility_metric,
            0,
            1,
        )

        metrics.addWidget(
            self.institution_metric,
            1,
            0,
        )

        metrics.addWidget(
            self.momentum_metric,
            1,
            1,
        )

        content.addLayout(
            metrics,
            3,
        )

        layout.addLayout(
            content
        )

    def set_pulse(
        self,
        score: int,
        trend_value: str,
        trend_status: str,
        volatility_value: str,
        volatility_status: str,
        institution_value: str,
        institution_status: str,
        momentum_value: str,
        momentum_status: str,
    ) -> None:

        self.pulse_gauge.set_score(
            score
        )

        self.trend_metric.set_metric(
            trend_value,
            trend_status,
            GREEN
            if "UP" in trend_value.upper()
            else ORANGE,
        )

        self.volatility_metric.set_metric(
            volatility_value,
            volatility_status,
            CYAN,
        )

        institution_color = (
            GREEN
            if (
                "POSITIVE"
                in institution_value.upper()
                or "ACCUM"
                in institution_value.upper()
            )
            else (
                RED
                if (
                    "NEGATIVE"
                    in institution_value.upper()
                    or "DISTRIB"
                    in institution_value.upper()
                )
                else ORANGE
            )
        )

        self.institution_metric.set_metric(
            institution_value,
            institution_status,
            institution_color,
        )

        self.momentum_metric.set_metric(
            momentum_value,
            momentum_status,
            PURPLE,
        )


# ==========================================================
# INTRADAY MOMENTUM CARD
# ==========================================================

class IntradayMomentumCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            345
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            SectionHeader(
                "INTRADAY MOMENTUM"
            )
        )

        price_row = QHBoxLayout()

        price_box = QVBoxLayout()

        self.index_label = QLabel(
            "NIFTY 50"
        )

        self.index_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 800;
            """
        )

        price_box.addWidget(
            self.index_label
        )

        self.price_label = QLabel(
            "--"
        )

        self.price_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 800;
            """
        )

        price_box.addWidget(
            self.price_label
        )

        price_row.addLayout(
            price_box
        )

        price_row.addStretch(1)

        self.change_badge = QLabel(
            "--"
        )

        price_row.addWidget(
            self.change_badge
        )

        layout.addLayout(
            price_row
        )

        self.curve = (
            MarketTrendCurve()
        )

        layout.addWidget(
            self.curve,
            1,
        )

        times = QHBoxLayout()

        time_labels = (
            "09:15",
            "10:30",
            "12:00",
            "13:30",
            "15:30",
        )

        for index, text in enumerate(
            time_labels
        ):

            label = QLabel(
                text
            )

            label.setStyleSheet(
                f"""
                color: {TEXT_MUTED};
                font-size: 7px;
                """
            )

            times.addWidget(
                label
            )

            if index < (
                len(time_labels) - 1
            ):

                times.addStretch(1)

        layout.addLayout(
            times
        )

        self.set_market_data(
            index_name="NIFTY 50",
            price=0,
            change=0,
            values=[],
        )

    def set_market_data(
        self,
        index_name: str,
        price: float,
        change: float,
        values: List[float],
    ) -> None:

        self.index_label.setText(
            index_name
        )

        self.price_label.setText(
            f"{price:,.2f}"
            if price
            else "--"
        )

        color = movement_color(
            change
        )

        self.change_badge.setText(
            percentage_text(change)
            if price
            else "--"
        )

        self.change_badge.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border: 1px solid {color};
                border-radius: 6px;
                padding: 5px 9px;
                font-size: 9px;
                font-weight: 800;
            }}
            """
        )

        self.curve.set_values(
            values
        )


# ==========================================================
# SETUP METRIC
# ==========================================================

class SetupMetric(QFrame):

    def __init__(
        self,
        title: str,
        value: str = "--",
        status: str = "",
        accent: str = TEXT_SECONDARY,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "SetupMetric"
        )

        self.setMinimumHeight(
            72
        )

        self.setStyleSheet(
            """
            QFrame#SetupMetric {
                background:
                    rgba(255,255,255,0.025);
                border:
                    1px solid #18273C;
                border-radius: 9px;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10, 8, 10, 8
        )

        layout.setSpacing(2)

        self.title_label = QLabel(
            title
        )

        self.title_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.title_label
        )

        self.value_label = QLabel(
            value
        )

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.value_label
        )

        self.status_label = QLabel(
            status
        )

        layout.addWidget(
            self.status_label
        )

        self.update_metric(
            value,
            status,
            accent,
        )

    def update_metric(
        self,
        value: str,
        status: str,
        accent: str,
    ) -> None:

        self.value_label.setText(
            value
        )

        self.status_label.setText(
            status
        )

        self.status_label.setStyleSheet(
            f"""
            color: {accent};
            font-size: 8px;
            font-weight: 700;
            """
        )


# ==========================================================
# RISK / REWARD VISUAL
# ==========================================================

class RiskRewardVisual(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.entry = 0.0
        self.stop = 0.0
        self.target1 = 0.0
        self.target2 = 0.0
        self.target3 = 0.0

        self.setMinimumSize(
            250,
            285,
        )

    def set_levels(
        self,
        entry: float,
        stop: float,
        target1: float,
        target2: float,
        target3: float,
    ) -> None:

        self.entry = entry
        self.stop = stop
        self.target1 = target1
        self.target2 = target2
        self.target3 = target3

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        if self.entry <= 0:
            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = self.rect().adjusted(
            30,
            20,
            -25,
            -20,
        )

        levels = [
            self.stop,
            self.entry,
            self.target1,
            self.target2,
            self.target3,
        ]

        minimum = min(levels)
        maximum = max(levels)

        spread = (
            maximum - minimum
        )

        if spread == 0:
            spread = 1.0

        def price_to_y(
            price: float,
        ) -> float:

            normalized = (
                price - minimum
            ) / spread

            return (
                rect.bottom()
                - normalized
                * rect.height()
            )

        stop_y = price_to_y(
            self.stop
        )

        entry_y = price_to_y(
            self.entry
        )

        t1_y = price_to_y(
            self.target1
        )

        t2_y = price_to_y(
            self.target2
        )

        t3_y = price_to_y(
            self.target3
        )

        # Reward zone

        reward_top_y = min(
            entry_y,
            t3_y,
        )

        reward_bottom_y = max(
            entry_y,
            t3_y,
        )

        reward_rect = QRectF(
            rect.left(),
            reward_top_y,
            rect.width(),
            reward_bottom_y
            - reward_top_y,
        )

        reward_gradient = (
            QLinearGradient(
                0,
                reward_rect.top(),
                0,
                reward_rect.bottom(),
            )
        )

        reward_top = QColor(
            GREEN
        )

        reward_top.setAlpha(
            48
        )

        reward_bottom = QColor(
            GREEN
        )

        reward_bottom.setAlpha(
            6
        )

        reward_gradient.setColorAt(
            0,
            reward_top,
        )

        reward_gradient.setColorAt(
            1,
            reward_bottom,
        )

        painter.fillRect(
            reward_rect,
            reward_gradient,
        )

        # Risk zone

        risk_top_y = min(
            entry_y,
            stop_y,
        )

        risk_bottom_y = max(
            entry_y,
            stop_y,
        )

        risk_rect = QRectF(
            rect.left(),
            risk_top_y,
            rect.width(),
            risk_bottom_y
            - risk_top_y,
        )

        risk_gradient = (
            QLinearGradient(
                0,
                risk_rect.top(),
                0,
                risk_rect.bottom(),
            )
        )

        risk_start = QColor(
            RED
        )

        risk_start.setAlpha(
            7
        )

        risk_end = QColor(
            RED
        )

        risk_end.setAlpha(
            55
        )

        risk_gradient.setColorAt(
            0,
            risk_start,
        )

        risk_gradient.setColorAt(
            1,
            risk_end,
        )

        painter.fillRect(
            risk_rect,
            risk_gradient,
        )

        center_x = (
            rect.left()
            + rect.width() * 0.16
        )

        painter.setPen(
            QPen(
                QColor("#263A57"),
                3,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(
                center_x,
                min(
                    t3_y,
                    stop_y,
                ),
            ),
            QPointF(
                center_x,
                max(
                    t3_y,
                    stop_y,
                ),
            ),
        )

        def draw_level(
            y: float,
            label: str,
            price: float,
            color: str,
            width_ratio: float = 1.0,
        ) -> None:

            level_color = QColor(
                color
            )

            painter.setPen(
                QPen(
                    level_color,
                    1.5,
                )
            )

            end_x = (
                rect.left()
                + rect.width()
                * width_ratio
            )

            painter.drawLine(
                QPointF(
                    center_x,
                    y,
                ),
                QPointF(
                    end_x,
                    y,
                ),
            )

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                level_color
            )

            painter.drawEllipse(
                QPointF(
                    center_x,
                    y,
                ),
                4,
                4,
            )

            font = QFont(
                FONT_FAMILY,
                8,
            )

            font.setBold(True)

            painter.setFont(font)

            painter.setPen(
                level_color
            )

            painter.drawText(
                QRectF(
                    center_x + 10,
                    y - 17,
                    rect.width() - 30,
                    16,
                ),
                Qt.AlignLeft
                | Qt.AlignVCenter,
                label,
            )

            painter.setPen(
                QColor(TEXT_PRIMARY)
            )

            painter.drawText(
                QRectF(
                    center_x + 10,
                    y,
                    rect.width() - 30,
                    17,
                ),
                Qt.AlignLeft
                | Qt.AlignVCenter,
                f"₹{price:,.2f}",
            )

        draw_level(
            t3_y,
            "TARGET 3",
            self.target3,
            GREEN,
            1.0,
        )

        draw_level(
            t2_y,
            "TARGET 2",
            self.target2,
            GREEN,
            0.90,
        )

        draw_level(
            t1_y,
            "TARGET 1",
            self.target1,
            CYAN,
            0.80,
        )

        draw_level(
            entry_y,
            "ENTRY",
            self.entry,
            BLUE,
            1.0,
        )

        draw_level(
            stop_y,
            "STOP LOSS",
            self.stop,
            RED,
            1.0,
        )


# ==========================================================
# CONFIDENCE RING
# ==========================================================

class ConfidenceRing(QWidget):

    def __init__(
        self,
        score: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._score = max(
            0,
            min(100, score),
        )

        self.setFixedSize(
            112,
            112,
        )

    def set_score(
        self,
        score: int,
    ) -> None:

        self._score = max(
            0,
            min(
                100,
                int(score),
            ),
        )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = QRectF(
            13,
            13,
            self.width() - 26,
            self.height() - 26,
        )

        painter.setPen(
            QPen(
                QColor("#1D2A3F"),
                9,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        painter.drawArc(
            rect,
            90 * 16,
            -360 * 16,
        )

        if self._score >= 85:
            color = GREEN

        elif self._score >= 70:
            color = CYAN

        elif self._score >= 55:
            color = ORANGE

        else:
            color = RED

        painter.setPen(
            QPen(
                QColor(color),
                9,
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )

        span = int(
            -360
            * self._score
            / 100
            * 16
        )

        painter.drawArc(
            rect,
            90 * 16,
            span,
        )

        score_font = QFont(
            FONT_FAMILY,
            18,
        )

        score_font.setBold(True)

        painter.setFont(
            score_font
        )

        painter.setPen(
            QColor(TEXT_PRIMARY)
        )

        painter.drawText(
            QRectF(
                0,
                30,
                self.width(),
                32,
            ),
            Qt.AlignCenter,
            str(self._score),
        )

        caption_font = QFont(
            FONT_FAMILY,
            7,
        )

        caption_font.setBold(True)

        painter.setFont(
            caption_font
        )

        painter.setPen(
            QColor(TEXT_MUTED)
        )

        painter.drawText(
            QRectF(
                0,
                62,
                self.width(),
                20,
            ),
            Qt.AlignCenter,
            "CONFIDENCE",
        )
        # ==========================================================
# TRADING SETUP CARD
# ==========================================================

class TradingSetupCard(DashboardCard):

    stock_requested = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(430)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16, 14, 16, 14
        )

        layout.setSpacing(10)

        # Header

        header_row = QHBoxLayout()

        title_box = QVBoxLayout()

        title = QLabel(
            "TRADING SETUP INTELLIGENCE"
        )

        title.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 900;
            """
        )

        title_box.addWidget(title)

        self.setup_subtitle = QLabel(
            "Highest-ranked active setup"
        )

        self.setup_subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        title_box.addWidget(
            self.setup_subtitle
        )

        header_row.addLayout(
            title_box
        )

        header_row.addStretch(1)

        self.setup_quality = QLabel(
            "--"
        )

        header_row.addWidget(
            self.setup_quality
        )

        layout.addLayout(
            header_row
        )

        # Main content

        main = QHBoxLayout()

        main.setSpacing(16)

        # LEFT

        left = QVBoxLayout()

        left.setSpacing(9)

        stock_row = QHBoxLayout()

        self.symbol_label = QLabel(
            "--"
        )

        self.symbol_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 23px;
            font-weight: 900;
            """
        )

        stock_row.addWidget(
            self.symbol_label
        )

        self.pattern_badge = PatternBadge(
            "--"
        )

        stock_row.addWidget(
            self.pattern_badge
        )

        stock_row.addStretch(1)

        self.signal_badge = SignalBadge(
            "WATCH"
        )

        stock_row.addWidget(
            self.signal_badge
        )

        left.addLayout(
            stock_row
        )

        self.setup_description = QLabel(
            "Waiting for scanner setup data."
        )

        self.setup_description.setWordWrap(
            True
        )

        self.setup_description.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 9px;
            """
        )

        left.addWidget(
            self.setup_description
        )

        metrics = QGridLayout()

        metrics.setSpacing(8)

        self.rvol_metric = SetupMetric(
            "RELATIVE VOLUME"
        )

        self.vwap_metric = SetupMetric(
            "VWAP"
        )

        self.ema_metric = SetupMetric(
            "EMA STRUCTURE"
        )

        self.adx_metric = SetupMetric(
            "ADX"
        )

        self.sector_metric = SetupMetric(
            "SECTOR"
        )

        self.breakout_metric = SetupMetric(
            "BREAKOUT VOLUME"
        )

        metrics.addWidget(
            self.rvol_metric,
            0,
            0,
        )

        metrics.addWidget(
            self.vwap_metric,
            0,
            1,
        )

        metrics.addWidget(
            self.ema_metric,
            1,
            0,
        )

        metrics.addWidget(
            self.adx_metric,
            1,
            1,
        )

        metrics.addWidget(
            self.sector_metric,
            2,
            0,
        )

        metrics.addWidget(
            self.breakout_metric,
            2,
            1,
        )

        left.addLayout(metrics)

        rr_row = QHBoxLayout()

        rr_title = QLabel(
            "MAX RISK / REWARD"
        )

        rr_title.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 800;
            """
        )

        rr_row.addWidget(
            rr_title
        )

        rr_row.addStretch(1)

        self.rr_label = QLabel(
            "--"
        )

        self.rr_label.setStyleSheet(
            f"""
            color: {GREEN};
            font-size: 18px;
            font-weight: 900;
            """
        )

        rr_row.addWidget(
            self.rr_label
        )

        left.addLayout(
            rr_row
        )

        main.addLayout(
            left,
            4,
        )

        # CENTER

        self.risk_reward_visual = (
            RiskRewardVisual()
        )

        main.addWidget(
            self.risk_reward_visual,
            3,
        )

        # RIGHT

        right = QVBoxLayout()

        right.setSpacing(8)

        right_title = QLabel(
            "SETUP QUALITY"
        )

        right_title.setAlignment(
            Qt.AlignCenter
        )

        right_title.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 800;
            """
        )

        right.addWidget(
            right_title
        )

        self.confidence_ring = (
            ConfidenceRing()
        )

        right.addWidget(
            self.confidence_ring,
            alignment=Qt.AlignCenter,
        )

        self.trend_status = QLabel(
            "TREND --"
        )

        self.volume_status = QLabel(
            "VOLUME --"
        )

        self.market_status = QLabel(
            "MARKET --"
        )

        for widget in (
            self.trend_status,
            self.volume_status,
            self.market_status,
        ):

            widget.setAlignment(
                Qt.AlignCenter
            )

            right.addWidget(widget)

        right.addStretch(1)

        main.addLayout(
            right,
            2,
        )

        layout.addLayout(main)

        self._style_confirmation_label(
            self.trend_status,
            "TREND --",
            TEXT_MUTED,
        )

        self._style_confirmation_label(
            self.volume_status,
            "VOLUME --",
            TEXT_MUTED,
        )

        self._style_confirmation_label(
            self.market_status,
            "MARKET --",
            TEXT_MUTED,
        )

        self._set_quality(
            "--",
            TEXT_MUTED,
        )

    def _set_quality(
        self,
        text: str,
        color: str,
    ) -> None:

        self.setup_quality.setText(
            text
        )

        self.setup_quality.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border: 1px solid {color};
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: 900;
            }}
            """
        )

    def _style_confirmation_label(
        self,
        widget: QLabel,
        text: str,
        color: str,
    ) -> None:

        widget.setText(text)

        widget.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border-radius: 6px;
                padding: 5px;
                font-size: 8px;
                font-weight: 800;
            }}
            """
        )

    def set_setup(
        self,
        data: Dict,
    ) -> None:

        symbol = str(
            data.get(
                "symbol",
                "--",
            )
        )

        pattern = str(
            data.get(
                "pattern",
                "--",
            )
        )

        signal = str(
            data.get(
                "signal",
                "WATCH",
            )
        )

        confidence = int(
            data.get(
                "confidence",
                0,
            )
        )

        entry = float(
            data.get(
                "entry",
                0.0,
            )
        )

        stop = float(
            data.get(
                "stop",
                0.0,
            )
        )

        target1 = float(
            data.get(
                "target1",
                0.0,
            )
        )

        target2 = float(
            data.get(
                "target2",
                0.0,
            )
        )

        target3 = float(
            data.get(
                "target3",
                0.0,
            )
        )

        self.symbol_label.setText(
            symbol
        )

        self.pattern_badge.setText(
            pattern.upper()
        )

        self.signal_badge.set_signal(
            signal
        )

        self.confidence_ring.set_score(
            confidence
        )

        self.setup_description.setText(
            str(
                data.get(
                    "description",
                    "",
                )
            )
        )

        self.rr_label.setText(
            str(
                data.get(
                    "rr",
                    "--",
                )
            )
        )

        self.risk_reward_visual.set_levels(
            entry,
            stop,
            target1,
            target2,
            target3,
        )

        # Quality

        if confidence >= 90:

            quality = "A+ SETUP"
            quality_color = GREEN

        elif confidence >= 80:

            quality = "A SETUP"
            quality_color = CYAN

        elif confidence >= 70:

            quality = "B+ SETUP"
            quality_color = ORANGE

        else:

            quality = "WATCH"
            quality_color = TEXT_MUTED

        self._set_quality(
            quality,
            quality_color,
        )

        # Metrics

        rvol = float(
            data.get(
                "rvol",
                0.0,
            )
        )

        self.rvol_metric.update_metric(
            f"{rvol:.2f}×"
            if rvol
            else "--",
            (
                "Strong participation"
                if rvol >= 1.5
                else "Normal participation"
            ),
            (
                GREEN
                if rvol >= 1.5
                else ORANGE
            ),
        )

        vwap_status = str(
            data.get(
                "vwap",
                "--",
            )
        )

        vwap_change = float(
            data.get(
                "vwap_change",
                0.0,
            )
        )

        self.vwap_metric.update_metric(
            vwap_status.upper(),
            percentage_text(
                vwap_change
            ),
            (
                GREEN
                if vwap_status.upper()
                == "ABOVE"
                else RED
            ),
        )

        ema_structure = str(
            data.get(
                "ema_structure",
                "--",
            )
        )

        ema_detail = str(
            data.get(
                "ema_detail",
                "",
            )
        )

        self.ema_metric.update_metric(
            ema_structure.upper(),
            ema_detail,
            (
                GREEN
                if "BULL" in ema_structure.upper()
                else (
                    RED
                    if "BEAR" in ema_structure.upper()
                    else ORANGE
                )
            ),
        )

        adx = float(
            data.get(
                "adx",
                0.0,
            )
        )

        self.adx_metric.update_metric(
            f"{adx:.1f}"
            if adx
            else "--",
            (
                "Strong trend"
                if adx >= 25
                else "Weak trend"
            ),
            (
                GREEN
                if adx >= 25
                else ORANGE
            ),
        )

        self.sector_metric.update_metric(
            str(
                data.get(
                    "sector",
                    "--",
                )
            ).upper(),
            str(
                data.get(
                    "sector_status",
                    "",
                )
            ),
            PURPLE,
        )

        breakout_volume = float(
            data.get(
                "breakout_volume",
                0.0,
            )
        )

        self.breakout_metric.update_metric(
            (
                f"{breakout_volume:.0f}%"
                if breakout_volume
                else "--"
            ),
            (
                "Confirmed"
                if breakout_volume >= 150
                else "Moderate"
            ),
            (
                GREEN
                if breakout_volume >= 150
                else ORANGE
            ),
        )

        trend_confirmed = bool(
            data.get(
                "trend_confirmed",
                False,
            )
        )

        volume_confirmed = bool(
            data.get(
                "volume_confirmed",
                False,
            )
        )

        market_aligned = bool(
            data.get(
                "market_aligned",
                False,
            )
        )

        self._style_confirmation_label(
            self.trend_status,
            (
                "TREND CONFIRMED"
                if trend_confirmed
                else "TREND UNCONFIRMED"
            ),
            (
                GREEN
                if trend_confirmed
                else RED
            ),
        )

        self._style_confirmation_label(
            self.volume_status,
            (
                "VOLUME CONFIRMED"
                if volume_confirmed
                else "VOLUME WEAK"
            ),
            (
                CYAN
                if volume_confirmed
                else ORANGE
            ),
        )

        self._style_confirmation_label(
            self.market_status,
            (
                "MARKET ALIGNED"
                if market_aligned
                else "MARKET NOT ALIGNED"
            ),
            (
                PURPLE
                if market_aligned
                else ORANGE
            ),
        )


# ==========================================================
# FLOW BAR
# ==========================================================

class FlowBar(QWidget):

    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 5000.0,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._value = value

        self._max_value = max(
            1.0,
            abs(max_value),
        )

        self.setMinimumHeight(
            18
        )

    def set_value(
        self,
        value: float,
    ) -> None:

        self._value = value

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = self.rect().adjusted(
            2,
            5,
            -2,
            -5,
        )

        center_x = (
            rect.center().x()
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor("#17253A")
        )

        painter.drawRoundedRect(
            rect,
            4,
            4,
        )

        painter.setPen(
            QPen(
                QColor("#40516A"),
                1,
            )
        )

        painter.drawLine(
            QPointF(
                center_x,
                rect.top() - 2,
            ),
            QPointF(
                center_x,
                rect.bottom() + 2,
            ),
        )

        ratio = min(
            abs(self._value)
            / self._max_value,
            1.0,
        )

        half_width = (
            rect.width() / 2
        )

        active_width = (
            half_width * ratio
        )

        if self._value >= 0:

            active_rect = QRectF(
                center_x,
                rect.top(),
                active_width,
                rect.height(),
            )

            color = QColor(
                GREEN
            )

        else:

            active_rect = QRectF(
                center_x
                - active_width,
                rect.top(),
                active_width,
                rect.height(),
            )

            color = QColor(
                RED
            )

        if active_width <= 0:
            return

        gradient = QLinearGradient(
            active_rect.left(),
            0,
            active_rect.right(),
            0,
        )

        faded = QColor(
            color
        )

        faded.setAlpha(
            90
        )

        if self._value >= 0:

            gradient.setColorAt(
                0,
                faded,
            )

            gradient.setColorAt(
                1,
                color,
            )

        else:

            gradient.setColorAt(
                0,
                color,
            )

            gradient.setColorAt(
                1,
                faded,
            )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawRoundedRect(
            active_rect,
            4,
            4,
        )


# ==========================================================
# INSTITUTION FLOW ROW
# ==========================================================

class InstitutionFlowRow(QFrame):

    def __init__(
        self,
        name: str,
        value: float,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "InstitutionFlowRow"
        )

        self.setMinimumHeight(
            58
        )

        self.setStyleSheet(
            """
            QFrame#InstitutionFlowRow {
                background:
                    rgba(255,255,255,0.018);
                border:
                    1px solid #17263B;
                border-radius: 8px;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            7,
            10,
            7,
        )

        layout.setSpacing(
            3
        )

        top = QHBoxLayout()

        name_label = QLabel(
            name
        )

        name_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 9px;
            font-weight: 800;
            """
        )

        top.addWidget(
            name_label
        )

        top.addStretch(1)

        sign = (
            "+"
            if value >= 0
            else ""
        )

        color = (
            GREEN
            if value >= 0
            else RED
        )

        value_label = QLabel(
            f"{sign}₹{value:,.0f} Cr"
        )

        value_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 10px;
            font-weight: 800;
            """
        )

        top.addWidget(
            value_label
        )

        layout.addLayout(
            top
        )

        flow = FlowBar(
            value=value,
            max_value=5000,
        )

        layout.addWidget(
            flow
        )


# ==========================================================
# INSTITUTIONAL FLOW CARD
# ==========================================================

class InstitutionalFlowCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            310
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            9
        )

        layout.addWidget(
            SectionHeader(
                "INSTITUTIONAL FLOW"
            )
        )

        subtitle = QLabel(
            "Cash-market participation • ₹ Crore"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(
            subtitle
        )

        self.flow_container = (
            QVBoxLayout()
        )

        self.flow_container.setSpacing(
            7
        )

        layout.addLayout(
            self.flow_container
        )

        layout.addStretch(1)

        bias_row = QHBoxLayout()

        bias_title = QLabel(
            "INSTITUTIONAL BIAS"
        )

        bias_title.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            font-weight: 800;
            """
        )

        bias_row.addWidget(
            bias_title
        )

        bias_row.addStretch(1)

        self.bias_label = QLabel(
            "--"
        )

        bias_row.addWidget(
            self.bias_label
        )

        layout.addLayout(
            bias_row
        )

        self.set_flows(
            0,
            0,
        )

    def set_flows(
        self,
        fii: float,
        dii: float,
    ) -> None:

        clear_layout(
            self.flow_container
        )

        self.flow_container.addWidget(
            InstitutionFlowRow(
                "FII / FPI",
                fii,
            )
        )

        self.flow_container.addWidget(
            InstitutionFlowRow(
                "DII",
                dii,
            )
        )

        net = fii + dii

        if net > 500:

            text = "ACCUMULATION"
            color = GREEN

        elif net < -500:

            text = "DISTRIBUTION"
            color = RED

        else:

            text = "BALANCED"
            color = ORANGE

        self.bias_label.setText(
            text
        )

        self.bias_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background:
                    rgba(255,255,255,0.035);
                border: 1px solid {color};
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 8px;
                font-weight: 800;
            }}
            """
        )


# ==========================================================
# OPTIONS SENTIMENT METER
# ==========================================================

class OptionsSentimentMeter(QWidget):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._value = 1.0

        self.setMinimumHeight(
            65
        )

    def set_pcr(
        self,
        value: float,
    ) -> None:

        self._value = max(
            0.0,
            min(
                2.0,
                value,
            ),
        )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = self.rect().adjusted(
            10,
            28,
            -10,
            -18,
        )

        gradient = QLinearGradient(
            rect.left(),
            0,
            rect.right(),
            0,
        )

        gradient.setColorAt(
            0,
            QColor(RED),
        )

        gradient.setColorAt(
            0.5,
            QColor(ORANGE),
        )

        gradient.setColorAt(
            1,
            QColor(GREEN),
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawRoundedRect(
            rect,
            5,
            5,
        )

        ratio = (
            self._value / 2.0
        )

        x = (
            rect.left()
            + ratio * rect.width()
        )

        painter.setBrush(
            QColor(TEXT_PRIMARY)
        )

        painter.drawEllipse(
            QPointF(
                x,
                rect.center().y(),
            ),
            6,
            6,
        )

        font = QFont(
            FONT_FAMILY,
            9,
        )

        font.setBold(True)

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(TEXT_PRIMARY)
        )

        painter.drawText(
            QRectF(
                0,
                0,
                self.width(),
                22,
            ),
            Qt.AlignCenter,
            f"PCR  {self._value:.2f}",
        )


# ==========================================================
# DERIVATIVE METRIC
# ==========================================================

class DerivativeMetric(QFrame):

    def __init__(
        self,
        title: str,
        value: str = "--",
        status: str = "",
        accent: str = TEXT_MUTED,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "DerivativeMetric"
        )

        self.setMinimumHeight(
            72
        )

        self.setStyleSheet(
            """
            QFrame#DerivativeMetric {
                background:
                    rgba(255,255,255,0.022);
                border:
                    1px solid #18273C;
                border-radius: 8px;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            9,
            7,
            9,
            7,
        )

        layout.setSpacing(
            2
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 7px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            title_label
        )

        self.value_label = QLabel(
            value
        )

        self.value_label.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 800;
            """
        )

        layout.addWidget(
            self.value_label
        )

        self.status_label = QLabel(
            status
        )

        layout.addWidget(
            self.status_label
        )

        self.set_metric(
            value,
            status,
            accent,
        )

    def set_metric(
        self,
        value: str,
        status: str,
        accent: str,
    ) -> None:

        self.value_label.setText(
            value
        )

        self.status_label.setText(
            status
        )

        self.status_label.setStyleSheet(
            f"""
            color: {accent};
            font-size: 8px;
            font-weight: 700;
            """
        )


# ==========================================================
# DERIVATIVES PULSE CARD
# ==========================================================

class DerivativesPulseCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            310
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            SectionHeader(
                "DERIVATIVES PULSE"
            )
        )

        subtitle = QLabel(
            "NIFTY futures & options positioning"
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            font-size: 8px;
            """
        )

        layout.addWidget(
            subtitle
        )

        self.pcr_meter = (
            OptionsSentimentMeter()
        )

        layout.addWidget(
            self.pcr_meter
        )

        metrics = QGridLayout()

        metrics.setSpacing(
            7
        )

        self.futures_metric = (
            DerivativeMetric(
                "FUTURES BIAS"
            )
        )

        self.call_metric = (
            DerivativeMetric(
                "CALL OI WALL"
            )
        )

        self.put_metric = (
            DerivativeMetric(
                "PUT OI WALL"
            )
        )

        self.max_pain_metric = (
            DerivativeMetric(
                "MAX PAIN"
            )
        )

        metrics.addWidget(
            self.futures_metric,
            0,
            0,
        )

        metrics.addWidget(
            self.call_metric,
            0,
            1,
        )

        metrics.addWidget(
            self.put_metric,
            1,
            0,
        )

        metrics.addWidget(
            self.max_pain_metric,
            1,
            1,
        )

        layout.addLayout(
            metrics
        )

    def set_data(
        self,
        pcr: float,
        futures_bias: str,
        futures_status: str,
        call_wall: str,
        put_wall: str,
        max_pain: str,
    ) -> None:

        self.pcr_meter.set_pcr(
            pcr
        )

        futures_upper = (
            futures_bias.upper()
        )

        if "LONG" in futures_upper:

            futures_color = GREEN

        elif "SHORT" in futures_upper:

            futures_color = RED

        else:

            futures_color = ORANGE

        self.futures_metric.set_metric(
            futures_bias,
            futures_status,
            futures_color,
        )

        self.call_metric.set_metric(
            call_wall,
            "Resistance",
            RED,
        )

        self.put_metric.set_metric(
            put_wall,
            "Support",
            GREEN,
        )

        self.max_pain_metric.set_metric(
            max_pain,
            "Expiry magnet",
            ORANGE,
        )


# ==========================================================
# MARKET REGIME SCORE
# ==========================================================

class RegimeScoreWidget(QWidget):

    def __init__(
        self,
        score: int = 50,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._score = max(
            0,
            min(100, score),
        )

        self.setMinimumHeight(
            125
        )

    def set_score(
        self,
        score: int,
    ) -> None:

        self._score = max(
            0,
            min(
                100,
                int(score),
            ),
        )

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:

        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        rect = QRectF(
            15,
            45,
            self.width() - 30,
            14,
        )

        gradient = QLinearGradient(
            rect.left(),
            0,
            rect.right(),
            0,
        )

        gradient.setColorAt(
            0,
            QColor(RED),
        )

        gradient.setColorAt(
            0.45,
            QColor(ORANGE),
        )

        gradient.setColorAt(
            0.65,
            QColor(CYAN),
        )

        gradient.setColorAt(
            1,
            QColor(GREEN),
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawRoundedRect(
            rect,
            7,
            7,
        )

        position = (
            rect.left()
            + rect.width()
            * self._score
            / 100
        )

        painter.setBrush(
            QColor(TEXT_PRIMARY)
        )

        painter.drawEllipse(
            QPointF(
                position,
                rect.center().y(),
            ),
            8,
            8,
        )

        font = QFont(
            FONT_FAMILY,
            18,
        )

        font.setBold(True)

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(TEXT_PRIMARY)
        )

        painter.drawText(
            QRectF(
                0,
                2,
                self.width(),
                30,
            ),
            Qt.AlignCenter,
            str(self._score),
        )

        label_font = QFont(
            FONT_FAMILY,
            7,
        )

        label_font.setBold(True)

        painter.setFont(
            label_font
        )

        painter.setPen(
            QColor(TEXT_MUTED)
        )

        painter.drawText(
            QRectF(
                rect.left(),
                70,
                70,
                18,
            ),
            Qt.AlignLeft,
            "RISK OFF",
        )

        painter.drawText(
            QRectF(
                rect.right() - 70,
                70,
                70,
                18,
            ),
            Qt.AlignRight,
            "RISK ON",
        )


# ==========================================================
# MARKET REGIME CARD
# ==========================================================

class MarketRegimeCard(DashboardCard):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.setMinimumHeight(
            310
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            7
        )

        layout.addWidget(
            SectionHeader(
                "MARKET REGIME"
            )
        )

        self.regime_score = (
            RegimeScoreWidget()
        )

        layout.addWidget(
            self.regime_score
        )

        statuses = QGridLayout()

        statuses.setSpacing(
            7
        )

        self.trend_metric = (
            DerivativeMetric(
                "TREND"
            )
        )

        self.breadth_metric = (
            DerivativeMetric(
                "BREADTH"
            )
        )

        self.volatility_metric = (
            DerivativeMetric(
                "VOLATILITY"
            )
        )

        self.institution_metric = (
            DerivativeMetric(
                "INSTITUTIONS"
            )
        )

        self.derivatives_metric = (
            DerivativeMetric(
                "DERIVATIVES"
            )
        )

        self.sectors_metric = (
            DerivativeMetric(
                "SECTORS"
            )
        )

        statuses.addWidget(
            self.trend_metric,
            0,
            0,
        )

        statuses.addWidget(
            self.breadth_metric,
            0,
            1,
        )

        statuses.addWidget(
            self.volatility_metric,
            1,
            0,
        )

        statuses.addWidget(
            self.institution_metric,
            1,
            1,
        )

        statuses.addWidget(
            self.derivatives_metric,
            2,
            0,
        )

        statuses.addWidget(
            self.sectors_metric,
            2,
            1,
        )

        layout.addLayout(
            statuses
        )

    def set_regime(
        self,
        score: int,
        trend: str,
        breadth: str,
        volatility: str,
        institutions: str,
        derivatives: str,
        sectors: str,
    ) -> None:

        self.regime_score.set_score(
            score
        )

        def status_color(
            value: str,
        ) -> str:

            value_upper = value.upper()

            positive_words = (
                "BULL",
                "STRONG",
                "LOW",
                "POSITIVE",
                "SUPPORT",
                "BROAD",
                "RISK ON",
            )

            negative_words = (
                "BEAR",
                "WEAK",
                "HIGH",
                "NEGATIVE",
                "DISTRIBUT",
                "RISK OFF",
            )

            if any(
                word in value_upper
                for word in positive_words
            ):

                return GREEN

            if any(
                word in value_upper
                for word in negative_words
            ):

                return RED

            return ORANGE

        metric_data = (
            (
                self.trend_metric,
                trend,
            ),
            (
                self.breadth_metric,
                breadth,
            ),
            (
                self.volatility_metric,
                volatility,
            ),
            (
                self.institution_metric,
                institutions,
            ),
            (
                self.derivatives_metric,
                derivatives,
            ),
            (
                self.sectors_metric,
                sectors,
            ),
        )

        for metric, value in metric_data:

            metric.set_metric(
                value,
                "Confirmed",
                status_color(value),
            )


# ==========================================================
# DASHBOARD PAGE
# ==========================================================

class DashboardPage(QWidget):
    """
    Main StockVersity Pro dashboard.

    The page is deliberately UI/service separated.

    The current version uses demo data so the entire visual
    shell can be tested before live market services are wired
    into the widgets.
    """

    stock_requested = Signal(str)

    scanner_requested = Signal(str)

    watchlist_requested = Signal()

    alerts_requested = Signal()

    heatmap_requested = Signal()

    refresh_requested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self.logger = logger

        self.index_cards: Dict[
            str,
            IndexCard,
        ] = {}

        self.setObjectName(
            "DashboardPage"
        )

        self.setStyleSheet(
            f"""
            QWidget#DashboardPage {{
                background-color: {BACKGROUND};
            }}
            """
        )

        self._build_ui()

        self._load_demo_data()

        self._configure_refresh_timer()

        self._update_market_session_status()

        self._update_dashboard_timestamp()

    # ======================================================
    # BUILD PAGE
    # ======================================================

    def _build_ui(
        self,
    ) -> None:

        root_layout = QVBoxLayout(
            self
        )

        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root_layout.setSpacing(
            0
        )

        self.scroll_area = (
            QScrollArea()
        )

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                background: {BACKGROUND};
                border: none;
            }}

            QScrollBar:vertical {{
                background: {BACKGROUND};
                width: 10px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background: #263A57;
                border-radius: 5px;
                min-height: 40px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #355071;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        self.content_widget = QWidget()

        self.content_widget.setObjectName(
            "DashboardContent"
        )

        self.content_widget.setStyleSheet(
            f"""
            QWidget#DashboardContent {{
                background: {BACKGROUND};
            }}
            """
        )

        self.dashboard_layout = QVBoxLayout(
            self.content_widget
        )

        self.dashboard_layout.setContentsMargins(
            22,
            18,
            22,
            24,
        )

        self.dashboard_layout.setSpacing(
            14
        )

        self._build_dashboard_hero()

        self._build_index_cards()

        self._build_top_opportunities()

        self._build_market_intelligence()

        self._build_market_heatmap()

        self._build_scanner_and_movers()

        self._build_watchlist_and_alerts()

        self._build_market_pulse()

        self._build_trading_setup()

        self._build_institutional_intelligence()

        self.dashboard_layout.addStretch(
            1
        )

        self.scroll_area.setWidget(
            self.content_widget
        )

        root_layout.addWidget(
            self.scroll_area
        )

    # ======================================================
    # HERO
    # ======================================================

    def _build_dashboard_hero(
        self,
    ) -> None:

        self.dashboard_hero = (
            DashboardHero()
        )

        self.dashboard_hero.refresh_requested.connect(
            self._refresh_dashboard
        )

        self.dashboard_layout.addWidget(
            self.dashboard_hero
        )

    # ======================================================
    # INDEX CARDS
    # ======================================================

    def _build_index_cards(
        self,
    ) -> None:

        container = QWidget()

        layout = QGridLayout(
            container
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setHorizontalSpacing(
            10
        )

        layout.setVerticalSpacing(
            10
        )

        indexes = (
            (
                "NIFTY",
                "NIFTY 50",
            ),
            (
                "BANKNIFTY",
                "BANK NIFTY",
            ),
            (
                "FINNIFTY",
                "FIN NIFTY",
            ),
            (
                "INDIAVIX",
                "INDIA VIX",
            ),
        )

        for column, (
            symbol,
            name,
        ) in enumerate(indexes):

            card = IndexCard(
                symbol=symbol,
                name=name,
                value=0,
                change=0,
                history=[],
            )

            card.clicked.connect(
                self.stock_requested.emit
            )

            self.index_cards[
                symbol
            ] = card

            layout.addWidget(
                card,
                0,
                column,
            )

            layout.setColumnStretch(
                column,
                1,
            )

        self.dashboard_layout.addWidget(
            container
        )

    # ======================================================
    # TOP OPPORTUNITIES
    # ======================================================

    def _build_top_opportunities(
        self,
    ) -> None:

        self.top_opportunities = (
            TopOpportunitiesCard()
        )

        self.top_opportunities.stock_requested.connect(
            self.stock_requested.emit
        )

        self.top_opportunities.scanner_requested.connect(
            lambda:
                self.scanner_requested.emit(
                    "all"
                )
        )

        self.dashboard_layout.addWidget(
            self.top_opportunities
        )

    # ======================================================
    # MARKET INTELLIGENCE
    # ======================================================

    def _build_market_intelligence(
        self,
    ) -> None:

        self.market_intelligence = (
            MarketIntelligencePanel()
        )

        self.dashboard_layout.addWidget(
            self.market_intelligence
        )

    # ======================================================
    # MARKET HEATMAP
    # ======================================================

    def _build_market_heatmap(
        self,
    ) -> None:

        self.market_heatmap = (
            MarketHeatmapCard()
        )

        self.market_heatmap.stock_requested.connect(
            self.stock_requested.emit
        )

        self.market_heatmap.view_all_requested.connect(
            self.heatmap_requested.emit
        )

        self.dashboard_layout.addWidget(
            self.market_heatmap
        )

    # ======================================================
    # SCANNER + MOVERS
    # ======================================================

    def _build_scanner_and_movers(
        self,
    ) -> None:

        container = QWidget()

        grid = QGridLayout(
            container
        )

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(
            12
        )

        grid.setVerticalSpacing(
            12
        )

        self.scanner_summary = (
            ScannerSummaryCard()
        )

        self.top_movers = (
            TopMoversCard()
        )

        self.scanner_summary.scanner_requested.connect(
            self.scanner_requested.emit
        )

        self.top_movers.stock_requested.connect(
            self.stock_requested.emit
        )

        grid.addWidget(
            self.scanner_summary,
            0,
            0,
        )

        grid.addWidget(
            self.top_movers,
            0,
            1,
        )

        grid.setColumnStretch(
            0,
            2,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        self.dashboard_layout.addWidget(
            container
        )

    # ======================================================
    # WATCHLIST + ALERTS
    # ======================================================

    def _build_watchlist_and_alerts(
        self,
    ) -> None:

        container = QWidget()

        grid = QGridLayout(
            container
        )

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(
            12
        )

        grid.setVerticalSpacing(
            12
        )

        self.watchlist_card = (
            WatchlistCard()
        )

        self.live_alerts = (
            LiveAlertsCard()
        )

        self.watchlist_card.stock_requested.connect(
            self.stock_requested.emit
        )

        self.watchlist_card.watchlist_requested.connect(
            self.watchlist_requested.emit
        )

        self.live_alerts.stock_requested.connect(
            self.stock_requested.emit
        )

        self.live_alerts.alerts_requested.connect(
            self.alerts_requested.emit
        )

        grid.addWidget(
            self.watchlist_card,
            0,
            0,
        )

        grid.addWidget(
            self.live_alerts,
            0,
            1,
        )

        grid.setColumnStretch(
            0,
            1,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        self.dashboard_layout.addWidget(
            container
        )

    # ======================================================
    # MARKET PULSE
    # ======================================================

    def _build_market_pulse(
        self,
    ) -> None:

        container = QWidget()

        grid = QGridLayout(
            container
        )

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(
            12
        )

        grid.setVerticalSpacing(
            12
        )

        self.market_pulse = (
            MarketPulseCard()
        )

        self.intraday_momentum = (
            IntradayMomentumCard()
        )

        grid.addWidget(
            self.market_pulse,
            0,
            0,
        )

        grid.addWidget(
            self.intraday_momentum,
            0,
            1,
        )

        grid.setColumnStretch(
            0,
            1,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        self.dashboard_layout.addWidget(
            container
        )

    # ======================================================
    # TRADING SETUP
    # ======================================================

    def _build_trading_setup(
        self,
    ) -> None:

        self.trading_setup = (
            TradingSetupCard()
        )

        self.trading_setup.stock_requested.connect(
            self.stock_requested.emit
        )

        self.dashboard_layout.addWidget(
            self.trading_setup
        )

    # ======================================================
    # INSTITUTIONAL INTELLIGENCE
    # ======================================================

    def _build_institutional_intelligence(
        self,
    ) -> None:

        container = QWidget()

        grid = QGridLayout(
            container
        )

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(
            12
        )

        grid.setVerticalSpacing(
            12
        )

        self.institutional_flow = (
            InstitutionalFlowCard()
        )

        self.derivatives_pulse = (
            DerivativesPulseCard()
        )

        self.market_regime = (
            MarketRegimeCard()
        )

        grid.addWidget(
            self.institutional_flow,
            0,
            0,
        )

        grid.addWidget(
            self.derivatives_pulse,
            0,
            1,
        )

        grid.addWidget(
            self.market_regime,
            0,
            2,
        )

        grid.setColumnStretch(
            0,
            1,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        grid.setColumnStretch(
            2,
            1,
        )

        self.dashboard_layout.addWidget(
            container
        )

    # ======================================================
    # REFRESH TIMER
    # ======================================================

    def _configure_refresh_timer(
        self,
    ) -> None:

        self.dashboard_refresh_timer = (
            QTimer(self)
        )

        self.dashboard_refresh_timer.setInterval(
            30_000
        )

        self.dashboard_refresh_timer.timeout.connect(
            self.refresh
        )

        self.dashboard_refresh_timer.start()

    def _refresh_dashboard(
        self,
    ) -> None:

        self.dashboard_hero.refresh_button.set_loading(
            True
        )

        try:

            self.refresh()

            self.refresh_requested.emit()

        finally:

            QTimer.singleShot(
                500,
                self._finish_refresh_animation,
            )

    def _finish_refresh_animation(
        self,
    ) -> None:

        self.dashboard_hero.refresh_button.set_loading(
            False
        )

    # ======================================================
    # MARKET SESSION
    # ======================================================

    def _update_dashboard_timestamp(
        self,
    ) -> None:

        current = (
            QDateTime.currentDateTime()
        )

        self.dashboard_hero.set_last_update(
            current.toString(
                "hh:mm:ss AP"
            )
        )

    def _update_market_session_status(
        self,
    ) -> None:

        now = (
            QDateTime.currentDateTime()
        )

        weekday = (
            now.date().dayOfWeek()
        )

        current_time = (
            now.time()
        )

        weekday_session = (
            1 <= weekday <= 5
        )

        market_start = QTime(
            9,
            15,
        )

        market_end = QTime(
            15,
            30,
        )

        time_session = (
            market_start
            <= current_time
            <= market_end
        )

        is_open = (
            weekday_session
            and time_session
        )

        self.dashboard_hero.market_status.set_market_open(
            is_open
        )

        self.dashboard_hero.session_label.setText(
            "NSE • LIVE SESSION"
            if is_open
            else "NSE • OFF MARKET"
        )

    # ======================================================
    # PUBLIC REFRESH
    # ======================================================

    def refresh(
        self,
    ) -> None:

        self.logger.debug(
            "Dashboard refresh requested."
        )

        self._update_market_session_status()

        self._update_dashboard_timestamp()

    # ======================================================
    # DEMO DATA
    # ======================================================

    def _load_demo_data(
        self,
    ) -> None:
        """
        Development/demo values only.

        These values make the complete dashboard visible
        before the live market-data integration phase.
        """

        # --------------------------------------------------
        # INDEXES
        # --------------------------------------------------

        self.index_cards[
            "NIFTY"
        ].update_data(
            25488.90,
            0.97,
            [
                25240,
                25265,
                25250,
                25295,
                25280,
                25325,
                25310,
                25360,
                25342,
                25385,
                25415,
                25402,
                25445,
                25430,
                25488,
            ],
        )

        self.index_cards[
            "BANKNIFTY"
        ].update_data(
            57418.30,
            0.64,
            [
                57010,
                57080,
                57045,
                57120,
                57190,
                57210,
                57185,
                57280,
                57310,
                57290,
                57355,
                57380,
                57418,
            ],
        )

        self.index_cards[
            "FINNIFTY"
        ].update_data(
            27034.65,
            0.48,
            [
                26870,
                26895,
                26910,
                26898,
                26930,
                26955,
                26940,
                26982,
                26975,
                27010,
                27034,
            ],
        )

        self.index_cards[
            "INDIAVIX"
        ].update_data(
            12.42,
            -3.18,
            [
                13.15,
                13.02,
                13.08,
                12.94,
                12.88,
                12.80,
                12.73,
                12.69,
                12.58,
                12.51,
                12.42,
            ],
        )

        # --------------------------------------------------
        # TOP OPPORTUNITIES
        # --------------------------------------------------

        self.top_opportunities.set_opportunities(
            [
                {
                    "symbol": "HAL",
                    "score": 97,
                    "signal": "BUY",
                    "pattern": "VCP BREAKOUT",
                    "rr": "1:4.2",
                    "timeframe": "SWING",
                },
                {
                    "symbol": "BEL",
                    "score": 94,
                    "signal": "BUY",
                    "pattern": "BULL FLAG",
                    "rr": "1:3.6",
                    "timeframe": "SWING",
                },
                {
                    "symbol": "RELIANCE",
                    "score": 91,
                    "signal": "BUY",
                    "pattern": "ORB",
                    "rr": "1:2.8",
                    "timeframe": "15M",
                },
                {
                    "symbol": "SBIN",
                    "score": 88,
                    "signal": "BUY",
                    "pattern": "BREAKOUT",
                    "rr": "1:3.1",
                    "timeframe": "30M",
                },
                {
                    "symbol": "TATAMOTORS",
                    "score": 83,
                    "signal": "WATCH",
                    "pattern": "CUP & HANDLE",
                    "rr": "1:2.7",
                    "timeframe": "DAILY",
                },
            ]
        )

        # --------------------------------------------------
        # SECTOR ROTATION
        # --------------------------------------------------

        self.market_intelligence.sector_strength.set_sectors(
            [
                {
                    "name": "DEFENCE",
                    "change": 3.20,
                },
                {
                    "name": "PSU BANK",
                    "change": 2.35,
                },
                {
                    "name": "METAL",
                    "change": 1.62,
                },
                {
                    "name": "AUTO",
                    "change": 0.84,
                },
                {
                    "name": "IT",
                    "change": -0.72,
                },
            ]
        )

        # --------------------------------------------------
        # BREADTH
        # --------------------------------------------------

        self.market_intelligence.market_breadth.set_breadth(
            advances=34,
            declines=14,
            unchanged=2,
        )

        # --------------------------------------------------
        # HEATMAP
        # --------------------------------------------------

        self.market_heatmap.set_stocks(
            [
                {
                    "symbol": "HAL",
                    "change_percent": 4.82,
                },
                {
                    "symbol": "BEL",
                    "change_percent": 3.74,
                },
                {
                    "symbol": "SBIN",
                    "change_percent": 2.68,
                },
                {
                    "symbol": "RELIANCE",
                    "change_percent": 1.82,
                },
                {
                    "symbol": "LT",
                    "change_percent": 1.54,
                },
                {
                    "symbol": "M&M",
                    "change_percent": 1.31,
                },
                {
                    "symbol": "TATASTEEL",
                    "change_percent": 1.18,
                },
                {
                    "symbol": "HDFCBANK",
                    "change_percent": 0.92,
                },
                {
                    "symbol": "ICICIBANK",
                    "change_percent": 0.74,
                },
                {
                    "symbol": "MARUTI",
                    "change_percent": 0.58,
                },
                {
                    "symbol": "BHARTIARTL",
                    "change_percent": 0.42,
                },
                {
                    "symbol": "AXISBANK",
                    "change_percent": 0.26,
                },
                {
                    "symbol": "INFY",
                    "change_percent": -0.18,
                },
                {
                    "symbol": "TCS",
                    "change_percent": -0.46,
                },
                {
                    "symbol": "WIPRO",
                    "change_percent": -0.68,
                },
                {
                    "symbol": "HCLTECH",
                    "change_percent": -0.81,
                },
                {
                    "symbol": "SUNPHARMA",
                    "change_percent": -1.02,
                },
                {
                    "symbol": "DRREDDY",
                    "change_percent": -1.28,
                },
            ]
        )

        # --------------------------------------------------
        # SCANNER ENGINE
        # --------------------------------------------------

        self.scanner_summary.set_scanner_data(
            {
                "intraday": {
                    "count": 5,
                    "best_score": 91,
                    "buys": 4,
                    "sells": 1,
                },
                "swing": {
                    "count": 4,
                    "best_score": 97,
                    "buys": 4,
                    "sells": 0,
                },
                "positional": {
                    "count": 3,
                    "best_score": 88,
                    "buys": 2,
                    "sells": 1,
                },
            }
        )

        # --------------------------------------------------
        # MOVERS
        # --------------------------------------------------

        self.top_movers.set_movers(
            [
                {
                    "symbol": "HAL",
                    "price": 5318.40,
                    "change": 4.82,
                },
                {
                    "symbol": "BEL",
                    "price": 412.75,
                    "change": 3.74,
                },
                {
                    "symbol": "SBIN",
                    "price": 846.20,
                    "change": 2.68,
                },
                {
                    "symbol": "RELIANCE",
                    "price": 1498.55,
                    "change": 1.82,
                },
                {
                    "symbol": "HCLTECH",
                    "price": 1634.80,
                    "change": -0.81,
                },
            ]
        )

        # --------------------------------------------------
        # WATCHLIST
        # --------------------------------------------------

        self.watchlist_card.set_watchlist(
            [
                {
                    "symbol": "HAL",
                    "price": 5318.40,
                    "change": 4.82,
                    "signal": "BUY",
                    "score": 97,
                },
                {
                    "symbol": "BEL",
                    "price": 412.75,
                    "change": 3.74,
                    "signal": "BUY",
                    "score": 94,
                },
                {
                    "symbol": "RELIANCE",
                    "price": 1498.55,
                    "change": 1.82,
                    "signal": "BUY",
                    "score": 91,
                },
                {
                    "symbol": "TATAMOTORS",
                    "price": 722.40,
                    "change": -0.34,
                    "signal": "WATCH",
                    "score": 83,
                },
                {
                    "symbol": "INFY",
                    "price": 1622.10,
                    "change": -0.18,
                    "signal": "WATCH",
                    "score": 72,
                },
            ]
        )

        # --------------------------------------------------
        # ALERTS
        # --------------------------------------------------

        self.live_alerts.set_alerts(
            [
                {
                    "time": "10:18",
                    "symbol": "HAL",
                    "message":
                        "VCP breakout confirmed with "
                        "2.4× relative volume.",
                    "type": "BREAKOUT",
                },
                {
                    "time": "10:11",
                    "symbol": "BEL",
                    "message":
                        "Bull flag continuation above "
                        "intraday resistance.",
                    "type": "BUY",
                },
                {
                    "time": "09:58",
                    "symbol": "SBIN",
                    "message":
                        "VWAP reclaim with strong "
                        "banking-sector momentum.",
                    "type": "BUY",
                },
                {
                    "time": "09:46",
                    "symbol": "HCLTECH",
                    "message":
                        "Momentum weakening below "
                        "intraday VWAP.",
                    "type": "SELL",
                },
            ]
        )

        # --------------------------------------------------
        # MARKET PULSE
        # --------------------------------------------------

        self.market_pulse.set_pulse(
            score=82,
            trend_value="UPTREND",
            trend_status="Above 20 / 50 EMA",
            volatility_value="LOW",
            volatility_status="VIX 12.42",
            institution_value="POSITIVE",
            institution_status="Accumulation",
            momentum_value="87 / 100",
            momentum_status="Strong",
        )

        # --------------------------------------------------
        # INTRADAY CURVE
        # --------------------------------------------------

        self.intraday_momentum.set_market_data(
            index_name="NIFTY 50",
            price=25488.90,
            change=0.97,
            values=[
                25240,
                25265,
                25250,
                25295,
                25280,
                25325,
                25310,
                25360,
                25342,
                25385,
                25370,
                25415,
                25402,
                25445,
                25430,
                25462,
                25450,
                25488,
            ],
        )

        # --------------------------------------------------
        # TRADING SETUP
        # --------------------------------------------------

        self.trading_setup.set_setup(
            {
                "symbol": "HAL",
                "pattern": "VCP BREAKOUT",
                "signal": "BUY",
                "confidence": 97,

                "description":
                    "Volatility contraction breakout "
                    "with strong relative volume, "
                    "bullish EMA structure and "
                    "sector-strength confirmation.",

                "entry": 5315.00,
                "stop": 5240.00,
                "target1": 5390.00,
                "target2": 5465.00,
                "target3": 5630.00,

                "rr": "1 : 4.20",

                "rvol": 2.40,

                "vwap": "ABOVE",
                "vwap_change": 1.28,

                "ema_structure": "BULLISH",
                "ema_detail": "21 > 50 > 200",

                "adx": 31.8,

                "sector": "DEFENCE",
                "sector_status": "Leading sector",

                "breakout_volume": 184,

                "trend_confirmed": True,
                "volume_confirmed": True,
                "market_aligned": True,
            }
        )

        # --------------------------------------------------
        # INSTITUTIONAL FLOW
        # --------------------------------------------------

        self.institutional_flow.set_flows(
            fii=-1245.0,
            dii=2180.0,
        )

        # --------------------------------------------------
        # DERIVATIVES
        # --------------------------------------------------

        self.derivatives_pulse.set_data(
            pcr=1.18,
            futures_bias="LONG",
            futures_status="Positive buildup",
            call_wall="25,700",
            put_wall="25,300",
            max_pain="25,500",
        )

        # --------------------------------------------------
        # MARKET REGIME
        # --------------------------------------------------

        self.market_regime.set_regime(
            score=84,
            trend="BULLISH",
            breadth="STRONG",
            volatility="LOW",
            institutions="POSITIVE",
            derivatives="SUPPORTIVE",
            sectors="BROAD",
        )
        
